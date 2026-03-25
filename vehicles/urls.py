from django.urls import path
from . import views

urlpatterns = [
    # Vehicle CRUD operations
    path('vehicles/', views.VehicleListCreateView.as_view(), name='vehicle-list-create'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    
    # Admin verification
    path('vehicles/<int:pk>/verify/', views.VehicleVerifyView.as_view(), name='vehicle-verify'),
    
    # Driver specific vehicles
    path('drivers/<int:driver_id>/vehicles/', views.DriverVehiclesView.as_view(), name='driver-vehicles'),
    
    # Available vehicles for customers
    path('vehicles/available/', views.AvailableVehiclesView.as_view(), name='available-vehicles'),
]