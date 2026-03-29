from rest_framework import serializers
from .models import Booking, BookingHistory
from vehicles.serializers import VehicleListSerializer
from accounts.serializers import UserSerializer
from django.utils import timezone

class BookingSerializer(serializers.ModelSerializer):
    """Main booking serializer"""
    
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True, allow_null=True)
    vehicle_details = VehicleListSerializer(source='vehicle', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'customer_name', 'customer_email',
            'driver', 'driver_name', 'vehicle', 'vehicle_details',
            'pickup_address', 'pickup_latitude', 'pickup_longitude',
            'dropoff_address', 'dropoff_latitude', 'dropoff_longitude',
            'cargo_type', 'cargo_weight', 'cargo_description', 'is_hazardous',
            'pickup_time', 'estimated_delivery_time', 'actual_pickup_time', 'actual_delivery_time',
            'distance_km', 'base_fare', 'distance_charge', 'waiting_charge', 'total_amount',
            'payment_method', 'payment_status', 'payment_id',
            'status', 'cancellation_reason',
            'customer_notes', 'driver_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'customer', 'total_amount']

class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a booking"""
    
    class Meta:
        model = Booking
        fields = [
            'id',
            'pickup_address', 'pickup_latitude', 'pickup_longitude',
            'dropoff_address', 'dropoff_latitude', 'dropoff_longitude',
            'cargo_type', 'cargo_weight', 'cargo_description', 'is_hazardous',
            'pickup_time', 'customer_notes'
        ]
        read_only_fields = ['id']
    
    def validate_pickup_time(self, value):
        """Validate pickup time is in the future"""
        if value < timezone.now():
            raise serializers.ValidationError("Pickup time must be in the future")
        return value
    
    def validate_cargo_weight(self, value):
        """Validate cargo weight"""
        if value <= 0:
            raise serializers.ValidationError("Cargo weight must be greater than 0")
        return value
    
    def create(self, validated_data):
        # Set base_fare and total_amount
        validated_data['base_fare'] = 100  # Default base fare
        validated_data['total_amount'] = validated_data['base_fare']
        return super().create(validated_data)

class BookingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating booking (driver actions)"""
    
    class Meta:
        model = Booking
        fields = [
            'status', 'driver_notes', 'actual_pickup_time', 'actual_delivery_time',
            'distance_km', 'distance_charge', 'waiting_charge'
        ]
    
    def validate(self, data):
        """Validate status transitions"""
        if 'status' in data:
            valid_transitions = {
                'accepted': ['pending'],
                'in_progress': ['accepted'],
                'completed': ['in_progress'],
                'cancelled': ['pending', 'accepted'],
                'rejected': ['pending']
            }
            instance = self.instance
            if instance and instance.status in valid_transitions.get(data['status'], []):
                return data
            raise serializers.ValidationError(f"Cannot change status from {instance.status} to {data['status']}")
        return data

class BookingHistorySerializer(serializers.ModelSerializer):
    """Serializer for booking history"""
    
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = BookingHistory
        fields = ['id', 'status', 'changed_by_name', 'notes', 'created_at']