# authapp/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404




from rest_framework import status
from .models import CertificateRequest
from .serializers import CertificateRequestSerializer



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Course
from .serializers import UserWithCoursesSerializer,CourseSerializer
import json



from .models import ContactSubmission
from .serializers import ContactSubmissionSerializer
# from cashfree_pg.models import OrderRequest
# authapp/views.py
import time
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

class CreateCashfreeOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logger.info(f"Received payment request: {request.data}")
            
            if not all(k in request.data for k in ['amount', 'course_url']):
                return Response(
                    {"error": "Missing required fields (amount, course_url)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Configuration
            base_url = "https://sandbox.cashfree.com" if settings.DEBUG else "https://api.cashfree.com"
            endpoint = f"{base_url}/pg/orders"
            
            headers = {
                "x-client-id": settings.CASHFREE_APP_ID,
                "x-client-secret": settings.CASHFREE_SECRET_KEY,
                "x-api-version": "2022-09-01",
                "Content-Type": "application/json"
            }
            
            # Prepare order data
            data = {
                "order_amount": float(request.data['amount']),
                "order_currency": "INR",
                "order_id": f"ORDER_{request.user.id}_{int(time.time())}",
                "customer_details": {
                    "customer_id": str(request.user.id),
                    "customer_email": request.user.email,
                    "customer_phone": getattr(request.user, 'phone', "9999999999")
                },
                "order_meta": {
                    "return_url": f"{settings.FRONTEND_URL}/payment-success?course_url={request.data.get('course_url')}",
                    "notify_url": f"{settings.BACKEND_URL}/api/cashfree-webhook/"
                }
            }
            
            # Make API call
            response = requests.post(endpoint, json=data, headers=headers)
            response.raise_for_status()  # Raises exception for 4XX/5XX responses
            
            return Response(response.json())
            
        except Exception as e:
            return Response(
                {"error": "Payment processing failed", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import hmac
import hashlib

@csrf_exempt
def cashfree_webhook(request):
    if request.method == 'POST':
        try:
            # Verify signature
            received_signature = request.headers.get('x-cf-signature')
            secret_key = settings.CASHFREE_SECRET_KEY.encode()
            expected_signature = hmac.new(
                secret_key,
                request.body,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(received_signature, expected_signature):
                return JsonResponse({"status": "error", "message": "Invalid signature"}, status=400)
            
            data = json.loads(request.body)
            # Process payment status here
            # Example: Update your database
            # order_id = data.get('orderId')
            # status = data.get('txStatus')
            
            return JsonResponse({"status": "success"})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)




class SubmitContactForm(APIView):
    def post(self, request):
        serializer = ContactSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Thank you for your submission!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class PurchaseCourseView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        course_url = request.data.get('course_url')
        
        if not course_url:
            return Response({"error": "Course URL is required"}, status=400)
            
        # Save to database
        Course.objects.create(
            user=request.user,
            course_url=course_url
        )
        
        return Response({"message": "Course purchased successfully!"})

class UserCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = Course.objects.filter(user=request.user)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)



class SubmitCertificateRequest(APIView):
    def post(self, request):
        serializer = CertificateRequestSerializer(data=request.data)
        if serializer.is_valid():
            cert = serializer.save()
            print("Certificate saved:", cert)
            return Response({'message': 'Certificate request submitted!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUserById(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
