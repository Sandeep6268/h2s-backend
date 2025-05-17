import razorpay
from django.conf import settings

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_razorpay_order(amount_inr):
    data = {
        "amount": int(amount_inr * 100),  # paise
        "currency": "INR",
        "payment_capture": 1  # auto-capture
    }
    return client.order.create(data=data)

def verify_payment_signature(params_dict):
    return client.utility.verify_payment_signature(params_dict)