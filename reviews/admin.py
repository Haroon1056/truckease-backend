from django.contrib import admin
from .models import Review, ReviewReport

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'reviewer', 'overall_rating', 'created_at')
    list_filter = ('overall_rating',)
    search_fields = ('reviewer__email', 'comment')

class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'reason', 'is_resolved', 'created_at')
    list_filter = ('reason', 'is_resolved')

admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewReport, ReviewReportAdmin)