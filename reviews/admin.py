from django.contrib import admin
from .models import Review, ReviewReport

class ReviewAdmin(admin.ModelAdmin):
    pass

class ReviewReportAdmin(admin.ModelAdmin):
    pass

admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewReport, ReviewReportAdmin)