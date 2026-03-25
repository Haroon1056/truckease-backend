from django.contrib import admin
from .models import Review, ReviewReport

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'reviewer', 'reviewee', 'overall_rating', 'is_public', 'created_at']
    list_filter = ['overall_rating', 'is_public', 'created_at']
    search_fields = ['reviewer__email', 'reviewee__email', 'comment']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ['review', 'reported_by', 'reason', 'is_resolved', 'created_at']
    list_filter = ['reason', 'is_resolved']
    search_fields = ['review__comment', 'reported_by__email']