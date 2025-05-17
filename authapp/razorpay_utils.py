# authapp/razorpay_utils.py
import razorpay
import hmac
import hashlib
from django.conf import settings

# Initialize client with error handling
try:
    razorpay_client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID, 
        settings.RAZORPAY_KEY_SECRET
    ))
except Exception as e:
    raise ImportError(f"Failed to initialize Razorpay client: {str(e)}")

def verify_payment_signature(params_dict):
    """Verify Razorpay payment signature"""
    try:
        razorpay_client.utility.verify_payment_signature(params_dict)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
    except Exception as e:
        print(f"Signature verification error: {str(e)}")
        return False

def verify_webhook_signature(request):
    """Verify Razorpay webhook signature"""
    try:
        received_sign = request.headers.get('X-Razorpay-Signature', '')
        payload = request.body
        
        if not received_sign or not payload:
            return False
            
        key = settings.RAZORPAY_WEBHOOK_SECRET.encode('utf-8')
        expected_sign = hmac.new(key, payload, hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(received_sign, expected_sign)
    except Exception as e:
        print(f"Webhook verification error: {str(e)}")
        return False