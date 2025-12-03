from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class House(models.Model):
    HOUSE_TYPES = [
        ('single_room','Single Room'),
        ('bedsitter', 'Bedsitter'),
        ('one_bedroom', 'One Bedroom'),
        ('two_bedroom', 'Two Bedroom'),
        ('three_bedroom', 'Three Bedroom'),
        ('studio', 'Studio Apartment'),
        ('double_room', 'Double Room'),
    ]

    title = models.CharField(max_length=200)
    house_type = models.CharField(choices=HOUSE_TYPES, max_length=20)

    description = models.TextField()

    # location
    location = models.CharField(max_length=400, help_text="e.g. Ongata Rongai, Kajiado")
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    # pricing and terms
    rent = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monthly rent in KES")
    deposit = models.DecimalField(max_digits=10, decimal_places=2, help_text="House deposit required")
    house_number = models.CharField(max_length=20)
    floor_number = models.CharField(max_length=20, blank=True, null=True, help_text="e.g  Ground Floor, Bungalow, Block A, Plot 5, or leave empty")

    is_active = models.BooleanField(default=False, help_text="House is visible to public")
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('unpaid', 'Unpaid'),
            ('pending', 'Payment Pending'),
            ('paid', 'Paid'),
        ],
        default='unpaid'
    )

    # owner and status
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='houses')
    date_posted = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.get_house_type_display()} - KES {self.rent}"

    class Meta:
        verbose_name = "House Listing"
        verbose_name_plural = "House Listings"
        ordering = ['-date_posted']

    
    
    def can_be_viewed(self):
        """Check if house can be viewed by public"""
        return self.is_active and self.payment_status == 'paid'


class HouseImage(models.Model):
    house = models.ForeignKey(House,on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='house/images/')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Images for {self.house.title}"

    class Meta:
        verbose_name = "House image"
        verbose_name_plural = "House images"
        ordering = ['-created_at','-updated_at']


class HouseTerm(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="terms")
    term = models.TextField(max_length=2000, help_text="e.g. No pets, 1 month deposit")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Terms for {self.house.title}"

    class Meta:
        verbose_name = "House term"
        verbose_name_plural = "House terms"
        ordering = ['-created_at','-updated_at']

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('house_posted', 'House Posted'),
        ('edit_profile', 'Edited Profile'),
        ('edit_company_profile', 'Edited Company Profile'),
        ('house_updated', 'House Updated'),
        ('profile_updated', 'Profile Updated'),
        ('password_changed', 'Password Changed'),
        ('house_viewed', 'House Viewed'),
        ('delete_house', 'House Deleted'),
        ('review_posted', 'Review Posted'),
        ('make_payment', 'Paid for a house.')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='activities')
    activity_type = models.CharField(choices=ACTIVITY_TYPES, max_length=20)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.created_at}"
    

