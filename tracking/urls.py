from django.urls import path
from . import views

urlpatterns = [
    path('tracking/booking/<int:booking_id>/route/', views.get_route, name='get-route'),
    path('tracking/booking/<int:booking_id>/route/create/', views.create_route, name='create-route'),
    path('tracking/booking/<int:booking_id>/eta/', views.update_eta, name='update-eta'),
    path('tracking/vehicle/<int:vehicle_id>/history/', views.location_history, name='location-history'),
]