from django.urls import path
from . import views

urlpatterns = [
    # Notification endpoints
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/mark-read/', views.NotificationMarkReadView.as_view(), name='mark-read'),
    path('notifications/<int:pk>/mark-read/', views.MarkSingleNotificationReadView.as_view(), name='mark-single-read'),
    path('notifications/unread-count/', views.UnreadCountView.as_view(), name='unread-count'),
    
    # Device registration endpoints
    path('devices/register/', views.DeviceRegistrationView.as_view(), name='device-register'),
    path('devices/delete-all/', views.DeleteAllDevicesView.as_view(), name='delete-all-devices'),
]