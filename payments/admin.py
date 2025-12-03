from django.contrib import admin

from payments.models import Payment, PaymentPlan, PaymentTransaction


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'amount', 'payment_method', 'status', 'is_verified', 'payment_date', 'created_at']
    list_filter = ['payment_method', 'status', 'is_verified', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'transaction_id', 'phone_number']
    readonly_fields = ['created_at', 'updated_at', 'payment_date', 'verification_date']

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'duration_days', 'is_active', 'created_at']
    list_filter = ['plan_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['payment', 'request_type', 'status_code', 'created_at']
    list_filter = ['request_type', 'status_code', 'created_at']
    search_fields = ['payment__user__username', 'payment__transaction_id']
    readonly_fields = ['created_at']