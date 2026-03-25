from django.contrib import admin
from .models import Review, ReviewReport

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'reviewer', 'reviewee', 'overall_rating', 'is_public', 'created_at']
    list_filter = ['overall_rating', 'is_public', 'is_verified']
    search_fields = ['reviewer__email', 'reviewee__email', 'comment']
    readonly_fields = ['created_at', 'updated_at', 'responded_at']
    
    fieldsets = (
        ('Booking', {'fields': ('booking',)}),
        ('Reviewer & Reviewee', {'fields': ('reviewer', 'reviewee')}),
        ('Rating', {'fields': ('overall_rating', 'category_ratings')}),
        ('Feedback', {'fields': ('comment', 'pros', 'cons')}),
        ('Response', {'fields': ('response', 'responded_at')}),
        ('Status', {'fields': ('is_verified', 'is_public')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    actions = ['verify_reviews', 'hide_reviews']
    
    def verify_reviews(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"{queryset.count()} review(s) verified.")
    verify_reviews.short_description = "Verify selected reviews"
    
    def hide_reviews(self, request, queryset):
        queryset.update(is_public=False)
        self.message_user(request, f"{queryset.count()} review(s) hidden.")
    hide_reviews.short_description = "Hide selected reviews"

@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'reported_by', 'reason', 'is_resolved', 'created_at']
    list_filter = ['reason', 'is_resolved']
    search_fields = ['review__comment', 'reported_by__email']
    readonly_fields = ['created_at']
    
    actions = ['resolve_reports']
    
    def resolve_reports(self, request, queryset):
        queryset.update(is_resolved=True, resolved_by=request.user)
        self.message_user(request, f"{queryset.count()} report(s) resolved.")
    resolve_reports.short_description = "Resolve selected reports"