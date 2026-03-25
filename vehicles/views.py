from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Vehicle
from .serializers import (
    VehicleSerializer, VehicleCreateSerializer, VehicleUpdateSerializer,
    VehicleAdminSerializer, VehicleListSerializer
)
from accounts.permissions import IsDriver, IsAdmin, IsOwnerOrReadOnly

class VehicleListCreateView(generics.ListCreateAPIView):
    """List all vehicles or create a new vehicle"""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['vehicle_type', 'status', 'is_available', 'current_city']
    search_fields = ['make', 'model', 'license_plate', 'current_city']
    ordering_fields = ['capacity_tons', 'base_price_per_km', 'created_at']
    
    def get_queryset(self):
        """Return vehicles based on user type"""
        user = self.request.user
        
        if user.user_type == 'admin':
            return Vehicle.objects.all()
        elif user.user_type == 'driver':
            return Vehicle.objects.filter(driver=user)
        else:  # customer
            return Vehicle.objects.filter(status='verified', is_available=True)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VehicleCreateSerializer
        return VehicleListSerializer
    
    def perform_create(self, serializer):
        """Create vehicle for logged-in driver"""
        if self.request.user.user_type != 'driver':
            raise PermissionError("Only drivers can register vehicles")
        serializer.save(driver=self.request.user)

class VehicleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a vehicle"""
    
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Vehicle.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return VehicleUpdateSerializer
        return VehicleSerializer
    
    def delete(self, request, *args, **kwargs):
        """Soft delete vehicle by marking as inactive"""
        vehicle = self.get_object()
        vehicle.status = 'inactive'
        vehicle.is_available = False
        vehicle.save()
        return Response({
            'message': 'Vehicle deactivated successfully'
        }, status=status.HTTP_200_OK)

class VehicleVerifyView(APIView):
    """Admin view to verify or reject vehicles"""
    
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        """Verify a vehicle"""
        vehicle = get_object_or_404(Vehicle, pk=pk)
        
        if vehicle.status != 'pending':
            return Response({
                'error': f'Vehicle is already {vehicle.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        notes = request.data.get('notes', '')
        vehicle.verify(request.user, notes)
        
        return Response({
            'message': 'Vehicle verified successfully',
            'vehicle': VehicleSerializer(vehicle).data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        """Reject a vehicle"""
        vehicle = get_object_or_404(Vehicle, pk=pk)
        
        if vehicle.status != 'pending':
            return Response({
                'error': f'Vehicle is already {vehicle.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        notes = request.data.get('notes', '')
        vehicle.reject(request.user, notes)
        
        return Response({
            'message': 'Vehicle rejected',
            'vehicle': VehicleSerializer(vehicle).data
        }, status=status.HTTP_200_OK)

class DriverVehiclesView(generics.ListAPIView):
    """List all vehicles for a specific driver"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VehicleListSerializer
    
    def get_queryset(self):
        driver_id = self.kwargs.get('driver_id')
        return Vehicle.objects.filter(driver_id=driver_id)

class AvailableVehiclesView(generics.ListAPIView):
    """List all available verified vehicles for customers"""
    
    permission_classes = [permissions.AllowAny]
    serializer_class = VehicleListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['vehicle_type', 'current_city', 'capacity_tons']
    search_fields = ['current_city', 'make', 'model']
    
    def get_queryset(self):
        return Vehicle.objects.filter(
            status='verified',
            is_available=True
        )