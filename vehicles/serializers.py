from rest_framework import serializers
from .models import Vehicle
from accounts.serializers import UserSerializer

class VehicleSerializer(serializers.ModelSerializer):
    """Base vehicle serializer"""
    
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)
    driver_email = serializers.CharField(source='driver.email', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'driver', 'driver_name', 'driver_email',
            'vehicle_type', 'make', 'model', 'year', 'license_plate', 'color',
            'capacity_tons', 'dimensions', 'description', 'features',
            'front_image', 'back_image', 'side_image', 'interior_image',
            'current_city', 'current_area', 'latitude', 'longitude',
            'status', 'is_available', 'base_price_per_km', 'base_price_per_hour',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'driver', 'status', 'created_at', 'updated_at', 'verified_at']

class VehicleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating vehicle"""
    
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_type', 'make', 'model', 'year', 'license_plate', 'color',
            'capacity_tons', 'dimensions', 'description', 'features',
            'front_image', 'back_image', 'side_image', 'interior_image',
            'current_city', 'current_area', 'latitude', 'longitude',
            'base_price_per_km', 'base_price_per_hour'
        ]
    
    def validate_license_plate(self, value):
        """Check if license plate already exists"""
        if Vehicle.objects.filter(license_plate=value).exists():
            raise serializers.ValidationError("License plate already registered")
        return value
    
    def validate(self, data):
        """Validate vehicle data"""
        if data['capacity_tons'] <= 0:
            raise serializers.ValidationError({"capacity_tons": "Capacity must be greater than 0"})
        
        if data['base_price_per_km'] <= 0:
            raise serializers.ValidationError({"base_price_per_km": "Price must be greater than 0"})
        
        return data

class VehicleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating vehicle"""
    
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_type', 'make', 'model', 'year', 'color',
            'capacity_tons', 'dimensions', 'description', 'features',
            'front_image', 'back_image', 'side_image', 'interior_image',
            'current_city', 'current_area', 'latitude', 'longitude',
            'is_available', 'base_price_per_km', 'base_price_per_hour'
        ]

class VehicleAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for vehicle verification"""
    
    driver_details = UserSerializer(source='driver', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = ['id', 'driver', 'created_at', 'updated_at']

class VehicleListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing vehicles"""
    
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'make', 'model', 'vehicle_type', 'license_plate',
            'capacity_tons', 'current_city', 'status', 'is_available',
            'base_price_per_km', 'driver_name', 'front_image'
        ]