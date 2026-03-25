from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Review, ReviewReport
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer, ReviewResponseSerializer,
    ReviewReportSerializer, DriverRatingSerializer
)
from accounts.permissions import IsCustomer, IsDriver, IsAdmin
from bookings.models import Booking

class ReviewListCreateView(generics.ListCreateAPIView):
    """List reviews or create a new review"""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['overall_rating', 'is_public']
    search_fields = ['comment', 'reviewee__first_name', 'reviewee__last_name']
    ordering_fields = ['created_at', 'overall_rating']
    
    def get_queryset(self):
        """Return reviews based on user type"""
        user = self.request.user
        
        if user.user_type == 'customer':
            return Review.objects.filter(reviewer=user)
        elif user.user_type == 'driver':
            return Review.objects.filter(reviewee=user)
        else:
            return Review.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def perform_create(self, serializer):
        """Create review for completed booking"""
        booking = serializer.validated_data['booking']
        
        # Check if user is the customer of this booking
        if booking.customer != self.request.user:
            raise PermissionError("You can only review your own trips")
        
        serializer.save(reviewer=self.request.user, reviewee=booking.driver)

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a review"""
    
    permission_classes = [permissions.IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    
    def get_permissions(self):
        """Custom permissions for different actions"""
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAuthenticated(), IsCustomer()]
        return [permissions.IsAuthenticated()]
    
    def delete(self, request, *args, **kwargs):
        """Soft delete review"""
        review = self.get_object()
        
        # Only the reviewer or admin can delete
        if review.reviewer != request.user and request.user.user_type != 'admin':
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        review.is_public = False
        review.save()
        
        return Response({'message': 'Review hidden successfully'}, status=status.HTTP_200_OK)

class ReviewResponseView(APIView):
    """Driver response to review"""
    
    permission_classes = [permissions.IsAuthenticated, IsDriver]
    
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk, reviewee=request.user)
        
        serializer = ReviewResponseSerializer(data=request.data)
        if serializer.is_valid():
            review.response = serializer.validated_data['response']
            review.responded_at = timezone.now()
            review.save()
            
            return Response({
                'message': 'Response added successfully',
                'review': ReviewSerializer(review).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewReportView(APIView):
    """Report inappropriate reviews"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        
        # Check if already reported
        if ReviewReport.objects.filter(review=review, reported_by=request.user).exists():
            return Response({
                'error': 'You have already reported this review'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ReviewReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(review=review, reported_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DriverRatingView(APIView):
    """Get driver ratings and statistics"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, driver_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        driver = get_object_or_404(User, id=driver_id, user_type='driver')
        
        reviews = Review.objects.filter(reviewee=driver, is_public=True)
        
        # Calculate statistics
        avg_rating = reviews.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0
        total_reviews = reviews.count()
        
        # Rating distribution
        distribution = {}
        for i in range(1, 6):
            distribution[str(i)] = reviews.filter(overall_rating=i).count()
        
        # Recent reviews
        recent_reviews = reviews.order_by('-created_at')[:10]
        
        data = {
            'driver_id': driver.id,
            'driver_name': driver.get_full_name(),
            'average_rating': round(avg_rating, 2),
            'total_reviews': total_reviews,
            'rating_distribution': distribution,
            'recent_reviews': ReviewSerializer(recent_reviews, many=True).data
        }
        
        return Response(data, status=status.HTTP_200_OK)