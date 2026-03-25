"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

# Set default settings module BEFORE any imports that need settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django ASAP
django.setup()

# Now import Django-specific modules after setup
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from tracking import consumers

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/tracking/<int:booking_id>/', consumers.LocationConsumer.as_asgi()),
            path('ws/driver/<int:driver_id>/', consumers.DriverLocationConsumer.as_asgi()),
        ])
    ),
})