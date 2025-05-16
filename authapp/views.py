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
            order_id = request.data.get('order_id', None)  # Optional for Cashfree
            
            if not course_url:
                return Response({"error": "Course URL is required"}, status=400)
                
            # Save to database
            Course.objects.create(
                user=request.user,
                course_url=course_url,
                order_id=order_id  # Store Cashfree order ID if available
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

class CreateCashfreeOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = float(request.data.get('amount'))
            course_url = request.data.get('course_url')
            user = request.user
            
            # Generate unique order ID
            order_id = f"H2S{int(time.time())}{user.id}"
            
            # Prepare Cashfree request
            cashfree_url = "https://api.cashfree.com/pg/orders"
            headers = {
                "Content-Type": "application/json",
                "x-client-id": settings.CASHFREE_APP_ID,
                "x-client-secret": settings.CASHFREE_SECRET_KEY,
                "x-api-version": "2022-09-01"
            }
            
            payload = {
                "order_id": order_id,
                "order_amount": amount,
                "order_currency": "INR",
                "order_note": f"Course Purchase: {course_url}",
                "customer_details": {
                    "customer_id": str(user.id),
                    "customer_name": user.username,
                    "customer_email": user.email,
                    "customer_phone": user.phone or "9999999999"
                },
                "order_meta": {
                    "return_url": f"{settings.FRONTEND_URL}{course_url}?order_id={order_id}",
                    "notify_url": f"{settings.BACKEND_URL}/api/cashfree-webhook/"
                }
            }
            
            # Create Cashfree order
            response = requests.post(cashfree_url, json=payload, headers=headers)
            response.raise_for_status()
            cashfree_data = response.json()
            
            # Save order to database
            Order.objects.create(
                user=user,
                order_id=order_id,
                cashfree_order_id=cashfree_data.get("order_id"),
                amount=amount,
                course_url=course_url,
                status="CREATED"
            )
            
            
            return Response({
                "orderId": order_id,
                "paymentSessionId": cashfree_data.get("payment_session_id")
            })
           
    
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class VerifyPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            order_id = request.data.get('orderId')
            payment_id = request.data.get('paymentId')
            
            # Verify payment with Cashfree
            verify_url = f"https://api.cashfree.com/pg/orders/{order_id}/payments/{payment_id}"
            headers = {
                "x-client-id": settings.CASHFREE_APP_ID,
                "x-client-secret": settings.CASHFREE_SECRET_KEY,
                "x-api-version": "2022-09-01"
            }
            
            response = requests.get(verify_url, headers=headers)
            response.raise_for_status()
            payment_data = response.json()
            
            # Update order status
            order = Order.objects.get(order_id=order_id)
            if payment_data.get("payment_status") == "SUCCESS":
                order.status = "SUCCESS"
                order.payment_id = payment_id
                order.save()
                
                # Create course enrollment
                Course.objects.create(
                    user=request.user,
                    course_url=order.course_url
                )
                
                return Response({"status": "success", "redirectUrl": order.course_url})
            
            order.status = "FAILED"
            order.save()
            return Response({"status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def cashfree_webhook(request):
    if request.method == "POST":
        try:
            # Verify webhook signature
            signature = request.headers.get("x-cf-signature")
            # Implement signature verification logic here
            
            data = json.loads(request.body)
            order_id = data.get("orderId")
            payment_status = data.get("paymentStatus")
            
            # Update order status
            order = Order.objects.get(order_id=order_id)
            order.status = payment_status
            order.save()
            
            if payment_status == "SUCCESS":
                # Ensure course is created if not already
                if not Course.objects.filter(user=order.user, course_url=order.course_url).exists():
                    Course.objects.create(
                        user=order.user,
                        course_url=order.course_url
                    )
            
            return HttpResponse(status=200)
        except Exception as e:
            print("Webhook error:", str(e))
            return HttpResponse(status=400)
    return HttpResponse(status=405)