import json
import logging
from django.conf import settings
from django.utils import timezone
from .models import Notification, UserDevice

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending push notifications"""
    
    @staticmethod
    def create_notification(user, notification_type, title, message, **kwargs):
        """Create a notification"""
        try:
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                data=kwargs.get('data', {}),
                priority=kwargs.get('priority', 'medium'),
                booking=kwargs.get('booking')
            )
            
            # Send push notification (async in production)
            # For now, just mark as sent
            notification.is_sent = True
            notification.sent_at = timezone.now()
            notification.save()
            
            return notification
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    def send_push_notification(notification):
        """Send push notification to user's devices"""
        devices = UserDevice.objects.filter(
            user=notification.user,
            is_active=True
        )
        
        for device in devices:
            try:
                if device.device_type == 'ios':
                    NotificationService.send_apns(notification, device)
                elif device.device_type == 'android':
                    NotificationService.send_fcm(notification, device)
                else:
                    NotificationService.send_web(notification, device)
            except Exception as e:
                logger.error(f"Failed to send notification to {device.device_token}: {e}")
    
    @staticmethod
    def send_fcm(notification, device):
        """Send via Firebase Cloud Messaging"""
        # Placeholder for FCM implementation
        # You'll need to install firebase-admin and set up credentials
        logger.info(f"Sending FCM to {device.device_token}: {notification.title}")
    
    @staticmethod
    def send_apns(notification, device):
        """Send via Apple Push Notification Service"""
        # Placeholder for APNS implementation
        logger.info(f"Sending APNS to {device.device_token}: {notification.title}")
    
    @staticmethod
    def send_web(notification, device):
        """Send via Web Push"""
        # Placeholder for web push implementation
        logger.info(f"Sending Web Push to {device.device_token}: {notification.title}")

class BookingNotificationService:
    """Handle notifications for booking events"""
    
    @staticmethod
    def notify_driver_new_booking(booking):
        """Notify driver about new booking"""
        from accounts.models import User
        
        # Find nearby drivers (simplified - notify all active drivers)
        drivers = User.objects.filter(
            user_type='driver',
            is_active=True,
            is_verified=True
        )
        
        for driver in drivers:
            NotificationService.create_notification(
                user=driver,
                notification_type='booking_created',
                title='New Booking Available!',
                message=f'New {booking.cargo_weight} ton booking from {booking.pickup_address[:50]}',
                data={
                    'booking_id': booking.id,
                    'pickup_lat': str(booking.pickup_latitude),
                    'pickup_lng': str(booking.pickup_longitude),
                    'cargo_weight': str(booking.cargo_weight),
                    'pickup_address': booking.pickup_address
                },
                priority='high',
                booking=booking
            )
    
    @staticmethod
    def notify_customer_booking_accepted(booking):
        """Notify customer that booking was accepted"""
        NotificationService.create_notification(
            user=booking.customer,
            notification_type='booking_accepted',
            title='Booking Accepted!',
            message=f'Driver {booking.driver.get_full_name()} has accepted your booking',
            data={
                'booking_id': booking.id,
                'driver_id': booking.driver.id,
                'driver_name': booking.driver.get_full_name(),
                'vehicle': f"{booking.vehicle.make} {booking.vehicle.model}" if booking.vehicle else 'Truck',
                'estimated_arrival': '30 minutes'
            },
            priority='high',
            booking=booking
        )
    
    @staticmethod
    def notify_customer_trip_started(booking):
        """Notify customer that trip has started"""
        NotificationService.create_notification(
            user=booking.customer,
            notification_type='booking_started',
            title='Trip Started!',
            message=f'Your driver has started the trip to {booking.dropoff_address[:50]}',
            data={
                'booking_id': booking.id,
                'driver_name': booking.driver.get_full_name(),
                'vehicle': f"{booking.vehicle.make} {booking.vehicle.model}" if booking.vehicle else 'Truck',
                'estimated_arrival': booking.estimated_delivery_time
            },
            priority='high',
            booking=booking
        )
    
    @staticmethod
    def notify_customer_trip_completed(booking):
        """Notify customer that trip is completed"""
        NotificationService.create_notification(
            user=booking.customer,
            notification_type='booking_completed',
            title='Trip Completed!',
            message=f'Your trip is complete. Total: Rs. {booking.total_amount}',
            data={
                'booking_id': booking.id,
                'total_amount': str(booking.total_amount),
                'distance_km': str(booking.distance_km) if booking.distance_km else 'N/A'
            },
            priority='medium',
            booking=booking
        )
    
    @staticmethod
    def notify_driver_trip_cancelled(booking):
        """Notify driver about cancellation"""
        if booking.driver:
            NotificationService.create_notification(
                user=booking.driver,
                notification_type='booking_cancelled',
                title='Booking Cancelled',
                message=f'Booking #{booking.id} was cancelled',
                data={
                    'booking_id': booking.id,
                    'reason': booking.cancellation_reason,
                    'cancelled_by': booking.cancelled_by.get_full_name() if booking.cancelled_by else 'System'
                },
                priority='high',
                booking=booking
            )
    
    @staticmethod
    def notify_customer_booking_reminder(booking):
        """Send reminder for upcoming booking"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Send reminder 1 hour before pickup
        reminder_time = booking.pickup_time - timedelta(hours=1)
        
        if reminder_time <= timezone.now() <= booking.pickup_time:
            NotificationService.create_notification(
                user=booking.customer,
                notification_type='booking_reminder',
                title='Upcoming Trip Reminder',
                message=f'Your trip will start in 1 hour. Pickup at {booking.pickup_address[:50]}',
                data={
                    'booking_id': booking.id,
                    'pickup_time': booking.pickup_time.isoformat(),
                    'pickup_address': booking.pickup_address
                },
                priority='medium',
                booking=booking
            )
    
    @staticmethod
    def notify_driver_vehicle_verified(vehicle):
        """Notify driver when vehicle is verified"""
        NotificationService.create_notification(
            user=vehicle.driver,
            notification_type='vehicle_verified',
            title='Vehicle Verified!',
            message=f'Your vehicle {vehicle.make} {vehicle.model} has been verified',
            data={
                'vehicle_id': vehicle.id,
                'vehicle_name': f"{vehicle.make} {vehicle.model}",
                'license_plate': vehicle.license_plate
            },
            priority='high'
        )
    
    @staticmethod
    def notify_driver_vehicle_rejected(vehicle, reason):
        """Notify driver when vehicle is rejected"""
        NotificationService.create_notification(
            user=vehicle.driver,
            notification_type='vehicle_rejected',
            title='Vehicle Verification Failed',
            message=f'Your vehicle {vehicle.make} {vehicle.model} was rejected: {reason[:100]}',
            data={
                'vehicle_id': vehicle.id,
                'vehicle_name': f"{vehicle.make} {vehicle.model}",
                'reason': reason
            },
            priority='high'
        )
    
    @staticmethod
    def notify_user_review_received(review):
        """Notify user when they receive a review"""
        NotificationService.create_notification(
            user=review.reviewee,
            notification_type='review_received',
            title='New Review Received!',
            message=f'You received a {review.overall_rating}-star rating from {review.reviewer.get_full_name()}',
            data={
                'review_id': review.id,
                'rating': review.overall_rating,
                'reviewer_name': review.reviewer.get_full_name(),
                'comment': review.comment[:100]
            },
            priority='medium'
        )