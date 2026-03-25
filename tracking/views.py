from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import LocationUpdate, TripRoute
from bookings.models import Booking
from .serializers import LocationUpdateSerializer, TripRouteSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_route(request, booking_id):
    """Get route for a booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if request.user.user_type == 'customer' and booking.customer != request.user:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    if request.user.user_type == 'driver' and booking.driver != request.user:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        route = TripRoute.objects.get(booking=booking)
        serializer = TripRouteSerializer(route)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TripRoute.DoesNotExist:
        return Response({'error': 'Route not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_eta(request, booking_id):
    """Update ETA for a booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.user.user_type != 'driver' or booking.driver != request.user:
        return Response({'error': 'Only the driver can update ETA'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        route = TripRoute.objects.get(booking=booking)
        route.current_eta = request.data.get('eta')
        route.traffic_delay_minutes = request.data.get('traffic_delay', 0)
        route.save()
        
        return Response({'message': 'ETA updated successfully'}, status=status.HTTP_200_OK)
    except TripRoute.DoesNotExist:
        return Response({'error': 'Route not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def location_history(request, vehicle_id):
    """Get location history for a vehicle"""
    from vehicles.models import Vehicle
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    # Check permissions
    if request.user.user_type == 'driver' and vehicle.driver != request.user:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    hours = request.GET.get('hours', 24)
    locations = LocationUpdate.objects.filter(
        vehicle=vehicle,
        timestamp__gte=timezone.now() - timedelta(hours=int(hours))
    ).order_by('timestamp')
    
    serializer = LocationUpdateSerializer(locations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_route(request, booking_id):
    """Create route for a booking (driver or admin)"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.user.user_type not in ['driver', 'admin']:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    # Check if route already exists
    if TripRoute.objects.filter(booking=booking).exists():
        return Response({'error': 'Route already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    data = request.data
    route = TripRoute.objects.create(
        booking=booking,
        origin_lat=data['origin_lat'],
        origin_lng=data['origin_lng'],
        destination_lat=data['destination_lat'],
        destination_lng=data['destination_lng'],
        route_points=data.get('route_points', []),
        distance_meters=data['distance_meters'],
        duration_seconds=data['duration_seconds'],
        polyline=data.get('polyline', '')
    )
    
    serializer = TripRouteSerializer(route)
    return Response(serializer.data, status=status.HTTP_201_CREATED)