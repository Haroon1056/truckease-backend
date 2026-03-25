from django.urls import path
from . import views

urlpatterns = [
    # Review endpoints
    path('reviews/', views.ReviewListCreateView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    path('reviews/<int:pk>/respond/', views.ReviewResponseView.as_view(), name='review-response'),
    path('reviews/<int:pk>/report/', views.ReviewReportView.as_view(), name='review-report'),
    path('drivers/<int:driver_id>/ratings/', views.DriverRatingView.as_view(), name='driver-ratings'),
]