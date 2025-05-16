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

class SubmitContactForm(APIView):
    def post(self, request):
        serializer = ContactSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Thank you for your submission!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class PurchaseCourseView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def post(self, request):
#         course_url = request.data.get('course_url')
        
#         if not course_url:
#             return Response({"error": "Course URL is required"}, status=400)
            
#         # Save to database
#         Course.objects.create(
#             user=request.user,
#             course_url=course_url
#         )
        
#         return Response({"message": "Course purchased successfully!"})

# views.py
class PurchaseCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            course_url = request.data.get('course_url')
            payment_id = request.data.get('payment_id')
            order_id = request.data.get('order_id')
            
            if not course_url:
                return Response({"error": "Course URL is required"}, status=400)
                
            # Save to database
            Course.objects.create(
                user=request.user,
                course_url=course_url,
                payment_id=payment_id,
                order_id=order_id,
                status="ACTIVE"
            )
            
            return Response({
                "message": "Course purchased successfully!",
                "course_url": course_url
            })
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)

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
    

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import time
from .models import Order

# views.py
class CreateCashfreeOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Input validation
            amount = request.data.get('amount')
            course_url = request.data.get('course_url')
            user = request.user

            if not all([amount, course_url]):
                return Response(
                    {"error": "Both amount and course_url are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                amount = float(amount)
                if amount <= 0:
                    return Response(
                        {"error": "Amount must be positive"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (TypeError, ValueError):
                return Response(
                    {"error": "Invalid amount format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Prepare Cashfree request
            headers = {
                "Content-Type": "application/json",
                "x-client-id": settings.CASHFREE_APP_ID,
                "x-client-secret": settings.CASHFREE_SECRET_KEY,
                "x-api-version": "2022-09-01"
            }

            order_id = f"H2S_{int(time.time())}_{user.id}"
            payload = {
                "order_id": order_id,
                "order_amount": amount,
                "order_currency": "INR",
                "customer_details": {
                    "customer_id": str(user.id),
                    "customer_name": (user.username or "Customer")[:50],
                    "customer_email": user.email,
                    "customer_phone": (user.phone or "9999999999")[:10]
                },
                "order_meta": {
                    "return_url": f"{settings.FRONTEND_URL}/payment-complete?order_id={order_id}",
                    "notify_url": f"{settings.BACKEND_URL}/api/cashfree-webhook/"
                }
            }

            # Make request to Cashfree
            response = requests.post(
                "https://api.cashfree.com/pg/orders",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            # Handle Cashfree response
            if response.status_code != 200:
                return Response(
                    {"error": f"Cashfree API error: {response.text}"},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            cashfree_data = response.json()
            return Response({
                "orderId": order_id,
                "paymentSessionId": cashfree_data["payment_session_id"]
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# views.py
class VerifyPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            order_id = request.data.get('orderId')
            payment_id = request.data.get('paymentId')
            
            # Verify with Cashfree API
            cashfree_url = f"https://api.cashfree.com/pg/orders/{order_id}/payments/{payment_id}"
            headers = {
                "x-client-id": settings.CASHFREE_APP_ID,
                "x-client-secret": settings.CASHFREE_SECRET_KEY,
                "x-api-version": "2022-09-01"
            }
            
            response = requests.get(cashfree_url, headers=headers)
            response.raise_for_status()
            payment_data = response.json()
            
            if payment_data.get("payment_status") == "SUCCESS":
                return Response({"status": "success"})
            return Response({"status": "failed"}, status=400)
            
        except Exception as e:
            return Response({"error": str(e)}, status=400) 
# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# views.py
@csrf_exempt
def cashfree_webhook(request):
    if request.method == "POST":
        try:
            # Verify webhook signature first
            signature = request.headers.get("x-cf-signature")
            # Add signature verification logic
            
            data = json.loads(request.body)
            order_id = data.get("orderId")
            payment_status = data.get("paymentStatus")
            
            if payment_status == "SUCCESS":
                # Get order from your database
                order = Order.objects.get(order_id=order_id)
                
                # Create course purchase
                Course.objects.create(
                    user=order.user,
                    course_url=order.course_url,
                    order_id=order_id
                )
                
            return HttpResponse(status=200)
        except Exception as e:
            print("Webhook error:", str(e))
            return HttpResponse(status=400)
    return HttpResponse(status=405)