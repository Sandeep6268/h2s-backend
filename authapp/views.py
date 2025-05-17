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
class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            amount = float(request.data.get('amount'))
            course_url = request.data.get('course_url')
            
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            order = client.order.create({
                "amount": int(amount * 100),
                "currency": "INR",
                "payment_capture": 1
            })
            
            # Create course record
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
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            course_url = data.get('course_url')
            
            # Verify payment signature
            params_dict = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }
            
            client.utility.verify_payment_signature(params_dict)
            
            # Update course purchase
            course, created = Course.objects.get_or_create(
                user=request.user,
                razorpay_order_id=data['razorpay_order_id'],
                defaults={
                    'course_url': course_url,
                    'razorpay_payment_id': data['razorpay_payment_id'],
                    'razorpay_signature': data['razorpay_signature'],
                    'payment_status': 'SUCCESS',
                    'amount': float(data['amount'])/100  # convert paise to INR
                }
            )
            
            if not created:
                course.payment_status = 'SUCCESS'
                course.razorpay_payment_id = data['razorpay_payment_id']
                course.save()
            
            return Response({'status': 'Payment verified successfully'})
            
        except Exception as e:
            # Log failed payment
            if 'razorpay_order_id' in data:
                Course.objects.filter(
                    razorpay_order_id=data['razorpay_order_id']
                ).update(payment_status='FAILED')
            
            return Response({'error': str(e)}, status=400)
        
@csrf_exempt
def razorpay_webhook(request):
    if request.method == 'POST':
        payload = request.body
        sig_header = request.META['HTTP_X_RAZORPAY_SIGNATURE']
        
        try:
            client.utility.verify_webhook_signature(
                payload, 
                sig_header, 
                settings.RAZORPAY_WEBHOOK_SECRET
            )
            # Process webhook
        except:
            return HttpResponse(status=400)
            
    return HttpResponse(status=200)