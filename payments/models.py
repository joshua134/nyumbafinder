# from datetime import timezone
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

from houses.models import House

# Create your models here.
class PaymentPlan(models.Model):
    """Different payment plans/options"""
    
    PLAN_TYPES = [
        ('per_listing', 'Per Listing'),
        ('subscription', 'Subscription'),
        ('featured', 'Featured Boost'),
    ]
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    duration_days = models.IntegerField(default=30)  # How long listing stays active
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - KES {self.price}"
    

class Payment(models.Model):
    """Track all payments"""
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('airtel', 'Airtel Money'),
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('unpaid', 'Unpaid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(PaymentPlan, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # M-Pesa/Airtel specific fields
    phone_number = models.CharField(max_length=15, blank=True)
    transaction_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    merchant_request_id = models.CharField(max_length=50, blank=True)
    checkout_request_id = models.CharField(max_length=50, blank=True)
    
    # Payment status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    payment_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    verification_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Related property (if payment is for specific property)
    house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
    
    # Metadata
    notes = models.TextField(blank=True)
    raw_response = models.JSONField(null=True, blank=True)  # Store API responses
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - KES {self.amount} - {self.get_status_display()}"

    def latest_mpesa_code(self):
        tx = self.transactions.filter(request_type="STK_PUSH", status_code=0).last()
        if not tx:
            return None
        items = tx.response_data.get("Body", {}).get("stkCallback", {}).get("CallbackMetadata", {}).get("Item", [])
        metadata = {item["Name"]: item.get("Value") for item in items}
        return metadata.get("MpesaReceiptNumber")
    
    def mark_as_completed(self, transaction_id=None):
        self.status = 'paid'
        self.is_verified = True
        self.payment_date = timezone.now()
        self.verification_date = timezone.now()
        # Set expiry date 1.5 years from now
        self.expiry_date = timezone.now() + timedelta(days=int(1.5 * 365))
        if transaction_id:
            self.transaction_id = transaction_id
        self.save()

class PaymentTransaction(models.Model):
    """Detailed transaction log for reconciliation"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    request_type = models.CharField(max_length=50)  # e.g., 'STK_PUSH', 'C2B'
    request_data = models.JSONField()
    response_data = models.JSONField()
    status_code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.payment.id} - {self.request_type}"