from django.urls import path
from . import views

urlpatterns = [
    # Booking CRUD
    path('bookings/', views.BookingListCreateView.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    
    # Driver actions
    path('bookings/<int:pk>/accept/', views.AcceptBookingView.as_view(), name='accept-booking'),
    path('bookings/<int:pk>/start-trip/', views.StartTripView.as_view(), name='start-trip'),
    path('bookings/<int:pk>/complete-trip/', views.CompleteTripView.as_view(), name='complete-trip'),
    
    # Cancel booking
    path('bookings/<int:pk>/cancel/', views.CancelBookingView.as_view(), name='cancel-booking'),
    
    # Booking history
    path('bookings/<int:booking_id>/history/', views.BookingHistoryView.as_view(), name='booking-history'),
]