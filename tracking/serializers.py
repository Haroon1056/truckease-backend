from rest_framework import serializers
from .models import LocationUpdate, TripRoute

class LocationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for location updates"""
    
    class Meta:
        model = LocationUpdate
        fields = ['id', 'latitude', 'longitude', 'speed', 'heading', 
                  'accuracy', 'timestamp', 'is_active']
        read_only_fields = ['id', 'timestamp']

class TripRouteSerializer(serializers.ModelSerializer):
    """Serializer for trip routes"""
    
    class Meta:
        model = TripRoute
        fields = [
            'id', 'booking', 'origin_lat', 'origin_lng',
            'destination_lat', 'destination_lng', 'route_points',
            'distance_meters', 'duration_seconds', 'polyline',
            'current_eta', 'traffic_delay_minutes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']