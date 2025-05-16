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
# views.py
class PurchaseCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            course_url = request.data.get('course_url')
            payment_id = request.data.get('payment_id')
            order_id = request.data.get('order_id')
            user = request.user
            
            if not all([course_url, payment_id, order_id]):
                return Response(
                    {"error": "All fields are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if course already exists
            if Course.objects.filter(user=user, course_url=course_url).exists():
                return Response(
                    {"message": "Course already purchased"},
                    status=status.HTTP_200_OK
                )

            # Create new course
            course = Course.objects.create(
                user=user,
                course_url=course_url,
                payment_id=payment_id,
                order_id=order_id
            )

            return Response({
                "message": "Course purchased successfully",
                "course": {
                    "id": course.id,
                    "course_url": course.course_url,
                    "purchased_at": course.purchased_at
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            # 1. Input validation
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

            # 2. Generate unique order ID
            order_id = f"H2S_{int(time.time())}_{user.id}"
            
            # 3. Save order to database first (for webhook reference)
            order = Order.objects.create(
                user=user,
                order_id=order_id,
                course_url=course_url,
                amount=amount,
                status='PENDING'
            )

            # 4. Prepare Cashfree request
            headers = {
                "Content-Type": "application/json",
                "x-client-id": settings.CASHFREE_APP_ID,
                "x-client-secret": settings.CASHFREE_SECRET_KEY,
                "x-api-version": "2022-09-01"
            }

            # IMPORTANT CHANGE: Use frontend payment status page instead of direct course URL
            payload = {
                "order_id": order_id,
                "order_amount": amount,
                "order_currency": "INR",
                "order_note": f"Course Purchase: {course_url}",
                "customer_details": {
                    "customer_id": str(user.id),
                    "customer_name": (user.username or "Customer")[:50],
                    "customer_email": user.email,
                    "customer_phone": (user.phone or "9999999999")[:10]
                },
                "order_meta": {
                    "return_url": f"{settings.FRONTEND_URL}/payment-status?order_id={order_id}",
                    "notify_url": f"{settings.BACKEND_URL}/api/cashfree-webhook/"
                }
            }

            # 5. Make request to Cashfree
            response = requests.post(
                "https://api.cashfree.com/pg/orders",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            # 6. Handle Cashfree response
            response.raise_for_status()
            cashfree_data = response.json()

            # 7. Update order with Cashfree reference
            order.cashfree_order_id = cashfree_data.get("order_id")
            order.save()

            return Response({
                "orderId": order_id,
                "paymentSessionId": cashfree_data["payment_session_id"],
                "cf_order_id": cashfree_data.get("order_id")
            })

        except requests.exceptions.RequestException as e:
            if 'order' in locals():
                order.status = 'FAILED'
                order.save()
                
            error_msg = f"Cashfree API error: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error_msg += f" | Response: {e.response.text}"
            return Response(
                {"error": error_msg},
                status=status.HTTP_502_BAD_GATEWAY
            )
            
        except Exception as e:
            return Response(
                {"error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# views.py
# views.py
# Django View Example
class VerifyPayment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_id = request.GET.get('payment_id')
        
        try:
            # 1. Verify with Cashfree API
            headers = {
                "x-client-id": settings.CASHFREE_APP_ID,
                "x-client-secret": settings.CASHFREE_SECRET_KEY,
                "x-api-version": "2022-09-01"
            }
            
            cf_response = requests.get(
                f"https://api.cashfree.com/pg/orders/{order_id}/payments/{payment_id}",
                headers=headers
            )
            
            if cf_response.status_code != 200:
                return Response(
                    {"status": "FAILED", "message": "Payment verification failed"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            payment_data = cf_response.json()
            
            # 2. Check payment status
            if payment_data.get("payment_status") == "SUCCESS":
                return Response({
                    "status": "SUCCESS",
                    "message": "Payment verified successfully"
                })
            
            return Response({
                "status": "PENDING",
                "message": "Payment not completed"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(
                {"status": "ERROR", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EnrollCourse(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            order_id = request.data.get('order_id')
            course_url = request.data.get('course_url')
            
            # Check if already enrolled
            if Course.objects.filter(order_id=order_id).exists():
                return Response({"status": "SUCCESS", "message": "Already enrolled"})
                
            # Create enrollment
            Course.objects.create(
                user=request.user,
                course_url=course_url,
                order_id=order_id,
                status='ACTIVE'
            )
            
            return Response({"status": "SUCCESS"})
            
        except Exception as e:
            return Response(
                {"status": "ERROR", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# views.py
# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import json
import hmac
import hashlib

@csrf_exempt
def cashfree_webhook(request):
    if request.method == "POST":
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
                return HttpResponse("Invalid signature", status=403)

            data = json.loads(request.body)
            if data.get('txStatus') == 'SUCCESS':
                order_id = data.get('orderId')
                payment_id = data.get('referenceId')
                course_url = data.get('orderNote', '')

                try:
                    order = Order.objects.get(order_id=order_id)
                    Course.objects.get_or_create(
                        user=order.user,
                        course_url=course_url,
                        defaults={
                            'payment_id': payment_id,
                            'order_id': order_id,
                            'status': 'ACTIVE'
                        }
                    )
                except Order.DoesNotExist:
                    print(f"Order not found: {order_id}")
                
            return HttpResponse(status=200)
        except Exception as e:
            print(f"Webhook error: {str(e)}")
            return HttpResponse(status=400)
    return HttpResponse(status=405)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Order  # Update this path based on your project

class CheckPaymentStatus(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response({"error": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(order_id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.status == "PAID":
            return Response({
                "status": "PAID",
                "redirect_url": order.course_url  # You can append this to frontend URL in frontend
            })
        else:
            return Response({
                "status": order.status,
                "redirect_url": "/"  # Send to homepage
            })
