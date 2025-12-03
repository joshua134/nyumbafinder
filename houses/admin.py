from django.contrib import admin

from houses.models import House, HouseTerm, HouseImage


# title = models.CharField(max_length=200)
#     house_type = models.CharField(choices=HOUSE_TYPES, max_length=20)
#
#     # location
#     location = models.CharField(max_length=400, help_text="e.g. Ongata Romgai, Kajiado")
#     latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
#     longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
#
#     # pricing and terms
#     rent = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monthly rent in KES")
#     deposit = models.DecimalField(max_digits=10, decimal_places=2, help_text="House deposit required")
#     house_number = models.CharField(max_length=20)
#     floor_number = models.CharField(max_length=10, blank=True, null=True)
#
#     # owner and status
#     owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='house')
#     listing_fee_paid = models.BooleanField(default=False)
#     date_posted = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

# Register your models here.
@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display =  ['title','owner','rent','is_active', 'date_posted']
    list_filter =  ['house_type', 'is_active', 'updated_at','date_posted']
    search_fields = ['title','location','owner__email']
    readonly_fields = ['date_posted','updated_at']
    actions = ['approve_houses', 'reject_houses']

    def approve_houses(self, request, queryset):
        queryset.update(listing_fee_paid=True)

    approve_houses.short_description = "Approve selected listings"

    def reject_houses(self, request, queryset):
        queryset.update(listing_fee_paid=False)

    reject_houses.short_description = "Reject selected listings"

@admin.register(HouseImage)
class HouseImageAdmin(admin.ModelAdmin):
    list_display = ['house', 'created_at']

@admin.register(HouseTerm)
class HouseTermAdmin(admin.ModelAdmin):
    list_display = ['house', 'term']