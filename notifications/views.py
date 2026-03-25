from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Notification, UserDevice
from .serializers import (
    NotificationSerializer, NotificationMarkReadSerializer,
    UserDeviceSerializer, NotificationCountSerializer
)

class NotificationListView(generics.ListAPIView):
    """List user notifications"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'is_read']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class NotificationDetailView(generics.RetrieveAPIView):
    """Get notification details"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class NotificationMarkReadView(APIView):
    """Mark notification(s) as read"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = NotificationMarkReadSerializer(data=request.data)
        
        if serializer.is_valid():
            if serializer.validated_data.get('mark_all'):
                # Mark all as read
                Notification.objects.filter(
                    user=request.user,
                    is_read=False
                ).update(
                    is_read=True,
                    read_at=timezone.now()
                )
            else:
                # Mark specific notifications
                notification_ids = serializer.validated_data.get('notification_ids', [])
                Notification.objects.filter(
                    user=request.user,
                    id__in=notification_ids,
                    is_read=False
                ).update(
                    is_read=True,
                    read_at=timezone.now()
                )
            
            return Response({
                'message': 'Notifications marked as read'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MarkSingleNotificationReadView(APIView):
    """Mark a single notification as read"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.mark_as_read()
        
        return Response({
            'message': 'Notification marked as read'
        }, status=status.HTTP_200_OK)

class UnreadCountView(APIView):
    """Get unread notification count"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        total_count = Notification.objects.filter(user=request.user).count()
        
        serializer = NotificationCountSerializer({
            'unread_count': unread_count,
            'total_count': total_count
        })
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeviceRegistrationView(APIView):
    """Register device for push notifications"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = UserDeviceSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check if device already exists
            device_token = serializer.validated_data['device_token']
            
            # Delete existing device with same token
            UserDevice.objects.filter(
                device_token=device_token
            ).delete()
            
            # Create new device
            device = serializer.save(user=request.user)
            
            return Response({
                'message': 'Device registered successfully',
                'device': UserDeviceSerializer(device).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """Unregister device"""
        device_token = request.data.get('device_token')
        
        if device_token:
            deleted = UserDevice.objects.filter(
                user=request.user,
                device_token=device_token
            ).delete()
            
            if deleted[0] > 0:
                return Response({
                    'message': 'Device unregistered successfully'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Device not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'error': 'device_token required'
        }, status=status.HTTP_400_BAD_REQUEST)

class DeleteAllDevicesView(APIView):
    """Delete all devices for current user"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        UserDevice.objects.filter(user=request.user).delete()
        
        return Response({
            'message': 'All devices unregistered successfully'
        }, status=status.HTTP_200_OK)