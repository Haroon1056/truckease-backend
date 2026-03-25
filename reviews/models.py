from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    """Rating and review system for completed trips"""
    
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ]
    
    CATEGORY_CHOICES = [
        ('punctuality', 'Punctuality'),
        ('professionalism', 'Professionalism'),
        ('communication', 'Communication'),
        ('vehicle_condition', 'Vehicle Condition'),
        ('value_for_money', 'Value for Money'),
    ]
    
    # Relationships
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='review'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    reviewee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    
    # Ratings
    overall_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    category_ratings = models.JSONField(default=dict, help_text="Ratings for each category")
    
    # Feedback
    comment = models.TextField(blank=True, max_length=500)
    pros = models.TextField(blank=True, max_length=500)
    cons = models.TextField(blank=True, max_length=500)
    
    # Response from reviewee
    response = models.TextField(blank=True, max_length=500)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reviewee', '-created_at']),
            models.Index(fields=['booking']),
            models.Index(fields=['overall_rating']),
        ]
    
    def __str__(self):
        return f"Review for {self.reviewee.email} - Rating: {self.overall_rating}"
    
    def save(self, *args, **kwargs):
        """Auto-set reviewer/reviewee based on booking"""
        if not self.reviewer_id:
            self.reviewer = self.booking.customer
            self.reviewee = self.booking.driver
        super().save(*args, **kwargs)

class ReviewReport(models.Model):
    """Report inappropriate reviews"""
    
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('offensive', 'Offensive Content'),
        ('fake', 'Fake Review'),
        ('irrelevant', 'Irrelevant'),
        ('other', 'Other'),
    ]
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'reported_by']