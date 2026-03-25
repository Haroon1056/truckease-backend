import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import LocationUpdate
from vehicles.models import Vehicle
from bookings.models import Booking

logger = logging.getLogger(__name__)

class LocationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time location tracking"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope['user']
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.room_group_name = f'tracking_{self.booking_id}'
        
        # Check if user is authorized to track this booking
        if await self.is_authorized():
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"User {self.user.email} connected to tracking for booking {self.booking_id}")
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"User {self.user.email} disconnected from tracking")
    
    async def receive(self, text_data):
        """Receive location updates from drivers"""
        if self.user.user_type != 'driver':
            return
        
        try:
            data = json.loads(text_data)
            
            # Save location update
            await self.save_location_update(data)
            
            # Broadcast to all connected clients
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location_update',
                    'data': {
                        'latitude': data.get('latitude'),
                        'longitude': data.get('longitude'),
                        'speed': data.get('speed'),
                        'timestamp': data.get('timestamp'),
                        'heading': data.get('heading')
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error processing location update: {e}")
    
    async def location_update(self, event):
        """Send location update to WebSocket"""
        await self.send(text_data=json.dumps(event['data']))
    
    @database_sync_to_async
    def is_authorized(self):
        """Check if user is authorized to track this booking"""
        try:
            booking = Booking.objects.get(id=self.booking_id)
            
            # Customer, driver, or admin can track
            if (self.user.user_type == 'customer' and booking.customer == self.user) or \
               (self.user.user_type == 'driver' and booking.driver == self.user) or \
               (self.user.user_type == 'admin'):
                return True
        except Booking.DoesNotExist:
            pass
        return False
    
    @database_sync_to_async
    def save_location_update(self, data):
        """Save location update to database"""
        try:
            booking = Booking.objects.get(id=self.booking_id)
            vehicle = booking.vehicle if booking.vehicle else None
            
            LocationUpdate.objects.create(
                vehicle=vehicle,
                booking=booking,
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                speed=data.get('speed'),
                heading=data.get('heading'),
                accuracy=data.get('accuracy')
            )
        except Exception as e:
            logger.error(f"Error saving location update: {e}")

class DriverLocationConsumer(AsyncWebsocketConsumer):
    """WebSocket for driver's live location for all active trips"""
    
    async def connect(self):
        self.user = self.scope['user']
        
        if self.user.user_type != 'driver':
            await self.close()
            return
        
        self.room_group_name = f'driver_{self.user.id}'
        
        # Join driver room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"Driver {self.user.email} connected to location stream")
    
    async def disconnect(self, close_code):
        """Handle disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive periodic location updates"""
        try:
            data = json.loads(text_data)
            
            # Get active bookings for this driver
            active_bookings = await self.get_active_bookings()
            
            # Broadcast location to each active booking
            for booking in active_bookings:
                await self.channel_layer.group_send(
                    f'tracking_{booking.id}',
                    {
                        'type': 'location_update',
                        'data': {
                            'latitude': data.get('latitude'),
                            'longitude': data.get('longitude'),
                            'speed': data.get('speed'),
                            'timestamp': data.get('timestamp'),
                            'heading': data.get('heading')
                        }
                    }
                )
        except Exception as e:
            logger.error(f"Error in driver location update: {e}")
    
    @database_sync_to_async
    def get_active_bookings(self):
        """Get driver's active bookings"""
        from bookings.models import Booking
        return list(Booking.objects.filter(
            driver=self.user,
            status__in=['accepted', 'in_progress']
        ))