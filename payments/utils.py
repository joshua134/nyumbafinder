# payments/utils.py
import requests
import base64
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def format_phone(phone):
    """Format Kenyan phone number to Safaricom format (2547XXXXXXXX)."""

    phone = str(phone).strip().replace(" ", "").replace("-", "").replace("+", "")

    # 0712345678 → 254712345678
    if phone.startswith("0") and len(phone) == 10:
        return "254" + phone[1:]

    # 712345678 → 254712345678
    if phone.startswith("7") and len(phone) == 9:
        return "254" + phone

    # Already correct: 254712345678
    if phone.startswith("254") and len(phone) == 12:
        return phone

    # 2547123456789 → trim to 12 digits
    if phone.startswith("254") and len(phone) > 12:
        return phone[:12]

    # Try to extract last 9 digits
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) >= 9:
        return "254" + digits[-9:]

    raise ValueError(f"Invalid phone number format: {phone}")

def initiate_mpesa_stk_push(phone_number, amount, payment_id, house_id):
    """Send MPesa STK Push request."""

    try:
        # Format phone
        phone = format_phone(phone_number)

        # Timestamp + password
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{settings.MPESA_BUSINESS_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
        ).decode()

        # TEST MODE: Always use amount = 1
        final_amount =  float(amount)
        
        payload = {
            "BusinessShortCode": settings.MPESA_BUSINESS_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": final_amount,
            "PartyA": phone,
            "PartyB": settings.MPESA_BUSINESS_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": f"HOUSE{house_id}",
            "TransactionDesc": f"NyumbaFinder Listing #{house_id}"
        }

        logger.info(f"STK PUSH PAYLOAD {payment_id}: {payload}")

        access_token = get_mpesa_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            settings.MPESA_STK_PUSH_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        print(f" Responce in utils : {response} ")

        data = response.json()

        print(f" Data in utils : {data} ")

        if response.status_code == 200 and "CheckoutRequestID" in data:
            logger.info(f"STK PUSH SUCCESS {payment_id}: {data}")

            return {
                "success": True,
                "checkout_request_id": data["CheckoutRequestID"],
                "merchant_request_id": data["MerchantRequestID"],
                "customer_message": data.get("CustomerMessage", ""),
                "raw_response": data
            }

        # API returned error (not HTTP error)
        logger.error(f"STK PUSH FAILURE {payment_id}: {data}")
        return {
            "success": False,
            "error": data.get("errorMessage", data.get("ResponseDescription", "Unknown Error")),
            "raw_response": data
        }

    except Exception as e:
        logger.error(f"STK PUSH EXCEPTION {payment_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_mpesa_access_token():
    """Get M-Pesa OAuth token."""
    try:
        auth = base64.b64encode(
            f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
        ).decode()

        headers = {"Authorization": f"Basic {auth}"}

        response = requests.get(settings.MPESA_OAUTH_URL, headers=headers, timeout=10)

        data = response.json()

        if response.status_code != 200:
            logger.error(f"OAuth token failure: {data}")
            raise Exception(data.get("errorMessage", "Failed to obtain token"))

        token = data.get("access_token")
        if not token:
            raise Exception("Access token missing in response")

        return token

    except Exception as e:
        logger.error(f"Access token exception: {str(e)}")
        raise