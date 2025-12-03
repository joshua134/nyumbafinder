from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from accounts.utils import decrypt_data, encrypt_data


# Create your models here.

class Role(models.Model):
    name=models.CharField(max_length=15,unique=True)
    description = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def clean_name(self):
        name = self.name
        if Role.objects.filter(name__iexact=name).exists():
            raise models.ValidationError("Role with this name already exists.")
        return name

    def clean_description(self):
        description = self.description
        if len(description) < 10:
            raise models.ValidationError("Description must be at least 10 characters long.")
        return description
    
    def save(self, *args, **kwargs):
        # Convert name to lowercase before saving
        self.name = self.name.lower().strip()
        
        # Full clean to run validation
        self.full_clean()
        
        # Call the parent save method
        super().save(*args, **kwargs)


class Profile(models.Model):
    USER_TYPES_CHOICES = [
        ('landlord', 'Landlord'),
        ('agent', 'Agent'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True, blank=True) 

    # common fields
    phone = PhoneNumberField( blank=True, null=True, region='KE', help_text="e.g. +254712345678")
    national_id = models.CharField(max_length=20, blank=True, null=True, help_text="National ID or Passport Number")


    # Verification status
    is_verified = models.BooleanField(default=False, help_text="Activation link is sent to email")
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def set_national_id(self, national_id):
        self.national_id = encrypt_data(national_id)

    def get_national_id(self):
        return decrypt_data(self.national_id)
    
    def set_phone(self, phone):
        self.phone = encrypt_data(phone)

    def get_phone(self):
        return decrypt_data(self.phone)
    
    # make it look like normal fields in admin/forms
    phone_plain = property(get_phone, set_phone)
    national_id_plain = property(get_national_id, set_national_id)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role.name})"

    def is_inactive_long(self):
        """ Check if user has no activity for 3 to 4 months."""
        inactive_period = timezone.now() - timedelta(days=100)
        return self.last_activity < inactive_period and not self.profile.houses.exists()

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User profiles"

    def clean_phone(self):
        phone = self.phone
        if Profile.objects.filter(phone=phone).exists():
            raise models.ValidationError("Phone number already in use.")
        return phone
    def get_user_type_display(self):
        return self.role.name


class AgentCompany(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='company')
    company_name = models.CharField(max_length=200)
    company_address = models.TextField()
    website = models.URLField(blank=True, null=True)

    # GOOGLE MAP PIN
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    # BUSINESS REG NO
    business_registration = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class CompanyContact(models.Model):
    CONTACT_TYPES = [
        ('phone', 'Phone'),
        ('email', 'Email'),
    ]
    company = models.ForeignKey(AgentCompany, on_delete=models.CASCADE, related_name='contacts')
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPES)
    value = models.CharField(max_length=200)

    class Meta:
        unique_together = ('company', 'contact_type', 'value')

    def __str__(self):
        return f"{self.company.company_name} - {self.value}"