from django.urls import path
from . import views

urlpatterns = [
    # Payment initiation
    path('payment/initiate/<int:house_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/process/<int:house_id>/', views.process_payment, name='process_payment'),
    
    # Payment status and management
    # path('payment/status/<int:payment_id>/', views.payment_status, name='payment_status'),
    path('payment/check/<int:payment_id>/', views.check_payment_status, name='check_payment_status'),
    path('payment/resend/<int:payment_id>/', views.resend_payment_request, name='resend_payment_request'),
    path('payment/cancel/<int:payment_id>/', views.cancel_payment, name='cancel_payment'),
    
    # Payment success/failure
    path('payment/success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('payment/failed/<int:payment_id>/', views.payment_failed, name='payment_failed'),
    path('payment/pending/<int:payment_id>/', views.payment_pending, name='payment_pending'),
    
    # M-Pesa callbacks (no authentication needed)
    path('payment/mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('payment/mpesa-validation/', views.mpesa_validation, name='mpesa_validation'),
    
    # Payment history
    path('payment/history/', views.payment_history, name='payment_history'),
    path('payment/receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
    
    # Admin/management
    path('payment/verify-payment/', views.verify_payment_manual, name='verify_payment_manual'),
    # path('payment/refund/<int:payment_id>/', views.request_refund, name='request_refund'),
]