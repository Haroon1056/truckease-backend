from rest_framework import serializers
from .models import Review, ReviewReport
from bookings.serializers import BookingSerializer

class ReviewSerializer(serializers.ModelSerializer):
    """Main review serializer"""
    
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    reviewee_name = serializers.CharField(source='reviewee.get_full_name', read_only=True)
    booking_details = BookingSerializer(source='booking', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'booking_details',
            'reviewer', 'reviewer_name', 'reviewee', 'reviewee_name',
            'overall_rating', 'category_ratings', 'comment',
            'pros', 'cons', 'response', 'responded_at',
            'is_verified', 'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reviewer', 'reviewee']

class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""
    
    class Meta:
        model = Review
        fields = ['booking', 'overall_rating', 'category_ratings', 
                  'comment', 'pros', 'cons', 'is_public']
    
    def validate(self, data):
        """Validate that booking is completed and not already reviewed"""
        booking = data['booking']
        
        if booking.status != 'completed':
            raise serializers.ValidationError("Cannot review an incomplete trip")
        
        if hasattr(booking, 'review'):
            raise serializers.ValidationError("This booking has already been reviewed")
        
        return data

class ReviewResponseSerializer(serializers.Serializer):
    """Serializer for responding to reviews"""
    
    response = serializers.CharField(max_length=500, required=True)

class ReviewReportSerializer(serializers.ModelSerializer):
    """Serializer for reporting reviews"""
    
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    
    class Meta:
        model = ReviewReport
        fields = ['id', 'review', 'reason', 'description', 
                  'is_resolved', 'reported_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']

class DriverRatingSerializer(serializers.Serializer):
    """Driver rating statistics"""
    
    driver_id = serializers.IntegerField()
    driver_name = serializers.CharField()
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField()
    recent_reviews = ReviewSerializer(many=True)