# authapp/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404

import razorpay

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
from urllib.parse import quote
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
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Course
from .serializers import UserWithCoursesSerializer,CourseSerializer
import json

from django.http import HttpResponse
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


from .razorpay_utils import verify_payment_signature
from django.db import transaction

class PurchaseCourseView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        try:
            data = request.data
            course_url = data.get('course_url')
            
            if not course_url:
                return Response({"error": "Course URL is required"}, status=400)
            
            # Verify payment first
            params_dict = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }
            
            verify_payment_signature(params_dict)
            
            # Create or update course purchase
            course, created = Course.objects.update_or_create(
                user=request.user,
                razorpay_order_id=data['razorpay_order_id'],
                defaults={
                    'course_url': course_url,
                    'razorpay_payment_id': data['razorpay_payment_id'],
                    'razorpay_signature': data['razorpay_signature'],
                    'amount': float(data['amount'])/100,  # convert from paise to INR
                    'payment_status': 'SUCCESS',
                    'status': 'ACTIVE'
                }
            )
            
            return Response({
                "message": "Course purchased successfully!",
                "course_id": course.id
            })
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# class UserCoursesView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         courses = Course.objects.filter(user=request.user)
#         serializer = CourseSerializer(courses, many=True)
#         return Response(serializer.data)

# authapp/views.py
class UserCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            courses = Course.objects.filter(
                user=request.user,
                payment_status='SUCCESS'  # Only show successfully paid courses
            ).select_related('user')
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



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
    
from django.conf import settings
from .razorpay_utils import create_razorpay_order,verify_payment_signature,client
import json

# authapp/views.py
# authapp/views.py
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Course
from .razorpay_utils import create_razorpay_order, client
from django.conf import settings

class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Input validation
            amount = request.data.get('amount')
            course_url = request.data.get('course_url')
            
            if not all([amount, course_url]):
                return Response(
                    {"error": "Both amount and course_url are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                return Response(
                    {"error": "Amount must be a positive number"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create order
            order = create_razorpay_order(amount)
            
            # Save to database
            Course.objects.create(
                user=request.user,
                course_url=course_url,
                razorpay_order_id=order['id'],
                amount=amount,
                payment_status='PENDING'
            )
            
            return Response(order)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            data = request.data
            params_dict = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }
            
            # Verify payment signature
            client.utility.verify_payment_signature(params_dict)
            
            # Update course record
            course = Course.objects.get(
                razorpay_order_id=data['razorpay_order_id'],
                user=request.user
            )
            
            course.razorpay_payment_id = data['razorpay_payment_id']
            course.razorpay_signature = data['razorpay_signature']
            course.payment_status = 'SUCCESS'
            course.save()
            
            return Response({'status': 'Payment verified successfully'})
            
        except Exception as e:
            # Log failed payment
            if 'razorpay_order_id' in data:
                Course.objects.filter(
                    razorpay_order_id=data['razorpay_order_id']
                ).update(payment_status='FAILED')
            
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

@csrf_exempt
def razorpay_webhook(request):
    if request.method == 'POST':
        try:
            payload = request.body.decode('utf-8')
            sig_header = request.META['HTTP_X_RAZORPAY_SIGNATURE']
            
            # Verify webhook signature
            client.utility.verify_webhook_signature(
                payload, 
                sig_header, 
                settings.RAZORPAY_WEBHOOK_SECRET
            )
            
            data = json.loads(payload)
            event = data.get('event')
            
            if event == 'payment.captured':
                payment = data.get('payload', {}).get('payment', {}).get('entity', {})
                order_id = payment.get('order_id')
                
                if order_id:
                    Course.objects.filter(
                        razorpay_order_id=order_id
                    ).update(
                        razorpay_payment_id=payment.get('id'),
                        payment_status='SUCCESS'
                    )
            
            return HttpResponse(status=200)
            
        except Exception as e:
            print(f"Webhook error: {str(e)}")
            return HttpResponse(status=400)
    
    return HttpResponse(status=405)