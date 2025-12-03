# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
import json
from django.conf import settings

from houses.models import House
from payments.models import Payment, PaymentTransaction
from payments.utils import format_phone, initiate_mpesa_stk_push

@login_required
def initiate_payment(request, house_id):
    """Show payment page"""
    house = get_object_or_404(House, id=house_id, owner=request.user)
    
    # Check if house already has active payment
    if house.payment_status == 'paid':
        messages.info(request, "This house been paid for and active.")
        return redirect('house_detail', house_id=house.id)
    
    return render(request, 'payments/initiate_payment.html', {'house': house,'amount': settings.AMOUNT_TO_PAY_PER_HOUSE})

@login_required
def process_payment(request, house_id):
    """Process payment request"""
    if request.method != 'POST':
        return redirect('initiate_payment', house_id=house_id)
    
    house = get_object_or_404(House, id=house_id, owner=request.user)
    phone = request.POST.get('phone', '').strip()
    method = request.POST.get('method', 'mpesa')

    # Validate input
    if not phone or len(phone) < 9:
        messages.error(request, "Please enter a valid phone number")
        return redirect('initiate_payment', house_id=house_id)
    
    # Format phone
    phone = format_phone(phone)
    
    amount = float(settings.AMOUNT_TO_PAY_PER_HOUSE)

    # Create payment record
    payment = Payment.objects.create(
        user=request.user,
        amount=amount,
        payment_method=method,
        phone_number=phone,
        house=house,
        status='pending'
    )
    
    # Update house status
    house.payment_status = 'pending'
    house.save()
    
    # For M-Pesa STK Push
    if method == 'mpesa':
        result = initiate_mpesa_stk_push(phone, str(amount), payment.id, house.id)
        
        if result['success']:
            # Save checkout request ID
            payment.checkout_request_id = result.get('checkout_request_id')
            payment.merchant_request_id = result.get('merchant_request_id')
            payment.save()
            
            request.session['amount'] = amount
            messages.success(request, "Payment request sent! Check your phone.")
            return redirect('payment_pending', payment_id=payment.id)
        else:
            messages.error(request, f"Payment failed: {result.get('error')}")
            payment.delete()
            return redirect('initiate_payment', house_id=house_id)
    
    # For other methods (implement as needed)
    else:
        messages.warning(request, "This payment method is coming soon.")
        return redirect('initiate_payment', house_id=house_id)

@login_required
def payment_pending(request, payment_id):
    """Show pending payment page"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    return render(request, 'payments/processing.html', {
        'payment': payment,
        'house': payment.house,
        'amount': settings.AMOUNT_TO_PAY_PER_HOUSE
    })

@login_required
def payment_success(request, payment_id):
    """Show payment success page"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status != 'paid':
        messages.warning(request, "Payment not completed yet.")
        return redirect('payment_pending', payment_id=payment_id)
    
    return render(request, 'payments/success.html', {
        'payment': payment,
        'house': payment.house,
        'amount': settings.AMOUNT_TO_PAY_PER_HOUSE
    })

@login_required
def payment_failed(request, payment_id):
    """Show payment failed page"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    return render(request, 'payments/failed.html', {
        'payment': payment,
        'house': payment.house,
        'amount': settings.AMOUNT_TO_PAY_PER_HOUSE
    })

@login_required
def check_payment_status(request, payment_id):
    """AJAX endpoint to check payment status"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    print("DEBUG PAYMENT:")
    print("  ID =", payment.id)
    print("  status =", payment.status)
    print("  is_verified =", payment.is_verified)
    print("  payment_date =", payment.payment_date)
    print("  house =", payment.house)
    print("  raw_response =", payment.raw_response)

    # print(f"status : {payment.status}  is_vefiried : {payment.is_verified} mpesa_code : {payment.mpesa_code}")
    
    # return JsonResponse({
    #     'status': payment.status,
    #     'is_verified': payment.is_verified,
    #     'mpesa_code': payment.latest_mpesa_code(),
    #     'redirect_url': reverse('payment_success', args=[payment_id]) if payment.status == 'paid' else None
    # })
    redirect_url = None
    if payment.status in ['paid', 'completed']:
        redirect_url = reverse('payment_success', args=[payment_id])
    elif payment.status == 'failed':
        redirect_url = reverse('payment_failed', args=[payment_id])

    print(f"REDICT URL : {redirect_url}")

    return JsonResponse({
        'status': payment.status,
        'is_verified': payment.is_verified,
        'redirect_url': redirect_url,
    })

@login_required
def resend_payment_request(request, payment_id):
    """Resend payment request"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status == 'paid':
        return JsonResponse({'success': False, 'error': 'Payment already completed'})
    
    # Resend M-Pesa request
    result = initiate_mpesa_stk_push(
        payment.phone_number,
        float(payment.amount),
        payment.id,
        payment.house.id
    )
    
    if result['success']:
        payment.checkout_request_id = result.get('checkout_request_id')
        payment.merchant_request_id = result.get('merchant_request_id')
        payment.save()
        
        return JsonResponse({'success': True, 'message': 'Payment request resent'})
    else:
        return JsonResponse({'success': False, 'error': result.get('error')})

@login_required
def cancel_payment(request, payment_id):
    """Cancel pending payment"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status == 'pending':
        payment.status = 'cancelled'
        payment.house.payment_status = 'unpaid'
        payment.house.save()
        payment.save()
        
        messages.info(request, "Payment cancelled.")
        return redirect('house_detail', house_id=payment.house.id)
    
    messages.warning(request, "Cannot cancel this payment.")
    return redirect('payment_pending', payment_id=payment_id)

@login_required
def payment_history(request):
    """Show user's payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate stats
    total_spent = sum(p.amount for p in payments if p.status == 'paid')
    active_listings = House.objects.filter(
        owner=request.user, 
        payment_status='paid',
        is_active=True
    ).count()
    
    return render(request, 'payments/history.html', {
        'payments': payments,
        'total_spent': total_spent,
        'active_listings': active_listings
    })

@login_required
def payment_receipt(request, payment_id):
    """Show/download payment receipt"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    return render(request, 'payments/receipt.html', {
        'payment': payment,
        'house': payment.house
    })

@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa STK Push callback"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        callback = data.get('Body', {}).get('stkCallback', {})

        result_code = callback.get('ResultCode')
        result_desc = callback.get('ResultDesc')
        checkout_id = callback.get('CheckoutRequestID')

        # Find payment
        payment = Payment.objects.filter(checkout_request_id=checkout_id).first()
        if not payment:
            return JsonResponse({
                "ResultCode": 1,
                "ResultDesc": "Payment not found"
            }, status=404)

        if result_code == 0:
            # Payment successful
            items = callback.get("CallbackMetadata", {}).get("Item", [])
            metadata = {item["Name"]: item.get("Value") for item in items}

            transaction_id = metadata.get("MpesaReceiptNumber")
            phone = metadata.get("PhoneNumber")
            amount = metadata.get("Amount")

            # Update payment
            payment.transaction_id = transaction_id
            payment.phone_number = phone or payment.phone_number
            payment.amount = amount or payment.amount
            payment.raw_response = data
            payment.mark_as_completed(transaction_id)

            # Update house
            if payment.house:
                payment.house.payment_status = "paid"
                payment.house.is_active = True
                payment.house.save()

            PaymentTransaction.objects.create(
                payment=payment,
                request_type="STK_PUSH",
                request_data={},  # any request data you want to log
                response_data=data,  # full callback
                status_code=result_code
            )

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})

        else:
            # Payment failed
            payment.status = 'failed'
            payment.notes = result_desc
            payment.save()

            if payment.house:
                payment.house.payment_status = 'unpaid'
                payment.house.save()

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Failed logged"})

    except Exception as e:
        print(f"Callback error: {e}")
        return JsonResponse({
            "ResultCode": 1,
            "ResultDesc": "Internal error"
        }, status=500)


@csrf_exempt
def mpesa_validation(request):
    """M-Pesa validation URL (required for PayBill)"""
    # This endpoint validates payments before they're processed
    data = json.loads(request.body)
    
    # You can add validation logic here
    # For now, accept all payments
    
    response = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    
    return JsonResponse(response)

@login_required
def verify_payment_manual(request):
    """Manual payment verification (admin)"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST':
        mpesa_code = request.POST.get('mpesa_code')
        payment_id = request.POST.get('payment_id')
        
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.mark_as_paid(mpesa_code)
            messages.success(request, "Payment verified successfully.")
        except Payment.DoesNotExist:
            messages.error(request, "Payment not found.")
        
        return redirect('admin:payments_payment_changelist')
    
    pending_payments = Payment.objects.filter(status='pending')
    return render(request, 'payments/admin_verify.html', {
        'pending_payments': pending_payments
    })
