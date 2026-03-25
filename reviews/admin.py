from django.contrib import admin
from .models import Review, ReviewReport

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'reviewer', 'overall_rating', 'created_at']
    list_filter = ['overall_rating']

# Temporarily disable ReviewReport admin
# @admin.register(ReviewReport)
# class ReviewReportAdmin(admin.ModelAdmin):
#     list_display = ['review', 'reason', 'is_resolved']