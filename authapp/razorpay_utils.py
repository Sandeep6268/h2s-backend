import razorpay
from django.conf import settings

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_razorpay_order(amount_inr, currency="INR"):
    try:
        data = {
            "amount": int(amount_inr * 100),  # paise
            "currency": currency,
            "payment_capture": 1  # auto-capture
        }
        return client.order.create(data=data)
    except Exception as e:
        raise Exception(f"Razorpay order creation failed: {str(e)}")

def verify_payment_signature(params_dict):
    try:
        return client.utility.verify_payment_signature(params_dict)
    except Exception as e:
        raise Exception(f"Signature verification failed: {str(e)}")