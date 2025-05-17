# authapp/razorpay_utils.py
import razorpay
import hmac
import hashlib
from django.conf import settings

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def verify_payment_signature(params_dict):
    """
    Verify Razorpay payment signature
    """
    try:
        client.utility.verify_payment_signature(params_dict)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False

def verify_webhook_signature(request):
    """
    Verify Razorpay webhook signature
    """
    received_sign = request.headers.get('X-Razorpay-Signature', '')
    payload = request.body
    
    # Calculate expected signature
    key = settings.RAZORPAY_WEBHOOK_SECRET.encode('utf-8')
    expected_sign = hmac.new(key, payload, hashlib.sha256).hexdigest()
    
    # Compare signatures
    return hmac.compare_digest(received_sign, expected_sign)