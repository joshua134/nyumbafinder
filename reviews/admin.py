from django.contrib import admin

from reviews.models import Review


# Register your models here.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['house', 'name', 'rating', 'created_at']
    list_filter = ['rating',  'created_at']
    search_fields = ['name', 'email']