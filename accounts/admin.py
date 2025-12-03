from django.contrib import admin

from accounts.models import Role, Profile


# Register your models here.
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields =  ['name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','role', 'phone', 'is_verified', 'is_active']
    list_filter =  ['role','is_verified','is_active']
    search_fields = ['user__email', 'phone', 'national_id']