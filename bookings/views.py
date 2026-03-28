from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Booking, BookingHistory
from .serializers import (
    BookingSerializer, BookingCreateSerializer, 
    BookingUpdateSerializer, BookingHistorySerializer
)
from accounts.permissions import IsCustomer, IsDriver, IsAdmin

class BookingListCreateView(generics.ListCreateAPIView):
    """List bookings or create new booking"""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'payment_status']
    search_fields = ['pickup_address', 'dropoff_address', 'cargo_type']
    ordering_fields = ['pickup_time', 'created_at', 'total_amount']
    
    def get_queryset(self):
        """Return bookings based on user type"""
        user = self.request.user
        
        if user.user_type == 'customer':
            return Booking.objects.filter(customer=user)
        elif user.user_type == 'driver':
            return Booking.objects.filter(driver=user)
        else:  # admin
            return Booking.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingSerializer
    
    def perform_create(self, serializer):
        """Create booking for logged-in customer"""
        if self.request.user.user_type != 'customer':
            raise PermissionError("Only customers can create bookings")
        
        # Add default values
        booking = serializer.save(
            customer=self.request.user,
            base_fare=100,  # Default base fare
            total_amount=100  # Initial total amount
        )
        
        # Create history entry
        BookingHistory.objects.create(
            booking=booking,
            status='pending',
            changed_by=self.request.user,
            notes='Booking created'
        )

class BookingDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update booking details"""
    
    permission_classes = [permissions.IsAuthenticated]
    queryset = Booking.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookingUpdateSerializer
        return BookingSerializer
    
    def update(self, request, *args, **kwargs):
        """Update booking and track history"""
        booking = self.get_object()
        
        # Check permissions
        if request.user.user_type == 'customer' and booking.customer != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.user_type == 'driver' and booking.driver != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # Track old status
        old_status = booking.status
        
        response = super().update(request, *args, **kwargs)
        
        # Track new status if changed
        if 'status' in request.data and request.data['status'] != old_status:
            BookingHistory.objects.create(
                booking=booking,
                status=request.data['status'],
                changed_by=request.user,
                notes=request.data.get('driver_notes', '')
            )
        
        return response
    
class AvailableBookingsView(generics.ListAPIView):
    """View for drivers to see available (unassigned) bookings"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        # Only drivers can access this
        if self.request.user.user_type != 'driver':
            return Booking.objects.none()
        
        # Return bookings that are pending and have no driver assigned
        return Booking.objects.filter(
            status='pending',
            driver__isnull=True
        )

class AcceptBookingView(APIView):
    """Driver accepts a booking"""
    
    permission_classes = [permissions.IsAuthenticated, IsDriver]
    
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, status='pending')
        
        # Check if driver has a verified vehicle
        if not request.user.vehicles.filter(status='verified', is_available=True).exists():
            return Response({
                'error': 'You need at least one verified vehicle to accept bookings'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        vehicle = request.user.vehicles.filter(status='verified', is_available=True).first()
        
        booking.accept_booking(request.user, vehicle)
        
        # Create history entry
        BookingHistory.objects.create(
            booking=booking,
            status='accepted',
            changed_by=request.user,
            notes=f'Booking accepted by driver {request.user.get_full_name()}'
        )
        
        return Response({
            'message': 'Booking accepted successfully',
            'booking': BookingSerializer(booking).data
        }, status=status.HTTP_200_OK)

class StartTripView(APIView):
    """Driver starts the trip"""
    
    permission_classes = [permissions.IsAuthenticated, IsDriver]
    
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, driver=request.user, status='accepted')
        
        booking.start_trip()
        
        # Create history entry
        BookingHistory.objects.create(
            booking=booking,
            status='in_progress',
            changed_by=request.user,
            notes='Trip started'
        )
        
        return Response({
            'message': 'Trip started successfully',
            'booking': BookingSerializer(booking).data
        }, status=status.HTTP_200_OK)

class CompleteTripView(APIView):
    """Driver completes the trip"""
    
    permission_classes = [permissions.IsAuthenticated, IsDriver]
    
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, driver=request.user, status='in_progress')
        
        # Update trip details
        booking.distance_km = request.data.get('distance_km', booking.distance_km)
        booking.distance_charge = request.data.get('distance_charge', booking.distance_charge)
        booking.waiting_charge = request.data.get('waiting_charge', booking.waiting_charge)
        
        # Recalculate total
        booking.total_amount = booking.calculate_total()
        
        booking.complete_trip()
        
        # Create history entry
        BookingHistory.objects.create(
            booking=booking,
            status='completed',
            changed_by=request.user,
            notes='Trip completed'
        )
        
        return Response({
            'message': 'Trip completed successfully',
            'total_amount': booking.total_amount,
            'booking': BookingSerializer(booking).data
        }, status=status.HTTP_200_OK)

class CancelBookingView(APIView):
    """Cancel a booking"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        
        # Check permissions
        if request.user.user_type == 'customer' and booking.customer != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.user_type == 'driver' and booking.driver != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if booking can be cancelled
        if booking.status not in ['pending', 'accepted']:
            return Response({
                'error': f'Cannot cancel booking with status: {booking.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reason = request.data.get('reason', '')
        booking.cancel_booking(request.user, reason)
        
        # Create history entry
        BookingHistory.objects.create(
            booking=booking,
            status='cancelled',
            changed_by=request.user,
            notes=f'Cancelled by {request.user.user_type}: {reason}'
        )
        
        return Response({
            'message': 'Booking cancelled successfully',
            'booking': BookingSerializer(booking).data
        }, status=status.HTTP_200_OK)

class BookingHistoryView(generics.ListAPIView):
    """View booking history"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookingHistorySerializer
    
    def get_queryset(self):
        booking_id = self.kwargs.get('booking_id')
        booking = get_object_or_404(Booking, pk=booking_id)
        
        # Check permissions
        if self.request.user.user_type == 'customer' and booking.customer != self.request.user:
            return BookingHistory.objects.none()
        if self.request.user.user_type == 'driver' and booking.driver != self.request.user:
            return BookingHistory.objects.none()
        
        return BookingHistory.objects.filter(booking=booking)