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
from .models import CustomUser
# from .serializers import UserWithCoursesSerializer,CourseSerializer
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
from .models import CustomUser
# from .serializers import UserWithCoursesSerializer,CourseSerializer
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


from django.db import transaction

# class PurchaseCourseView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     @transaction.atomic
#     def post(self, request):
#         try:
#             data = request.data
#             course_url = data.get('course_url')
            
#             if not course_url:
#                 return Response({"error": "Course URL is required"}, status=400)
            
#             # Verify payment first
#             params_dict = {
#                 'razorpay_payment_id': data['razorpay_payment_id'],
#                 'razorpay_signature': data['razorpay_signature']
#             }
            
#             verify_payment_signature(params_dict)
            
#             # Create or update course purchase
#             course, created = Course.objects.update_or_create(
#                 user=request.user,
#                 # razorpay_order_id=data['razorpay_order_id'],
#                 defaults={
#                     'course_url': course_url,
#                     'razorpay_payment_id': data['razorpay_payment_id'],
#                     'razorpay_signature': data['razorpay_signature'],
#                     'amount': float(data['amount'])/100,  # convert from paise to INR
#                     'payment_status': 'SUCCESS',
#                     'status': 'ACTIVE'
#                 }
#             )
            
#             return Response({
#                 "message": "Course purchased successfully!",
#                 "course_id": course.id
#             })
            
#         except Exception as e:
#             return Response({"error": str(e)}, status=400)

# class UserCoursesView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         courses = Course.objects.filter(user=request.user)
#         serializer = CourseSerializer(courses, many=True)
#         return Response(serializer.data)

# authapp/views.py
# class UserCoursesView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         try:
#             courses = Course.objects.filter(
#                 user=request.user,
#                 payment_status='SUCCESS'  # Only show successfully paid courses
#             ).select_related('user')
#             serializer = CourseSerializer(courses, many=True)
#             return Response(serializer.data)
#         except Exception as e:
#             return Response(
#                 {'error': str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )



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
    


# authapp/views.py
# authapp/views.py


import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import PaymentSerializer
from .models import Payment
import json

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = int(float(request.data.get('amount'))) * 100  # Razorpay expects amount in paise
            course_url = request.data.get('course_url')
            
            if not amount or not course_url:
                return Response({'error': 'Amount and course URL are required'}, status=status.HTTP_400_BAD_REQUEST)

            data = {
                'amount': amount,
                'currency': 'INR',
                'receipt': f"receipt_{request.user.id}_{int(time.time())}",
                'payment_capture': '1'  # Auto-capture payment
            }
            
            order = client.order.create(data=data)
            
            # Save the order to database
            Payment.objects.create(
                user=request.user,
                razorpay_order_id=order['id'],
                amount=amount/100,  # Store in INR, not paise
                course_url=course_url
            )
            
            return Response(order)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class PaymentWebhookView(APIView):
    def post(self, request):
        try:
            payload = request.body.decode('utf-8')
            signature = request.headers.get('X-Razorpay-Signature')
            
            # Verify the webhook signature
            client.utility.verify_webhook_signature(payload, signature, settings.RAZORPAY_WEBHOOK_SECRET)
            
            data = json.loads(payload)
            
            if data['event'] == 'payment.captured':
                payment_id = data['payload']['payment']['entity']['id']
                order_id = data['payload']['payment']['entity']['order_id']
                
                # Update payment in database
                payment = Payment.objects.get(razorpay_order_id=order_id)
                payment.razorpay_payment_id = payment_id
                payment.status = 'completed'
                payment.save()
                
                # Here you can add any additional logic like sending emails, etc.
                
            return Response({'status': 'success'})
            
        except Exception as e:
            print(f"Webhook error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = {
                'razorpay_payment_id': request.data.get('payment_id'),
                'razorpay_order_id': request.data.get('order_id'),
                'razorpay_signature': request.data.get('signature')
            }
            
            client.utility.verify_payment_signature(data)
            
            # Update payment status
            payment = Payment.objects.get(
                razorpay_order_id=data['razorpay_order_id'],
                user=request.user
            )
            payment.razorpay_payment_id = data['razorpay_payment_id']
            payment.razorpay_signature = data['razorpay_signature']
            payment.status = 'completed'
            payment.save()
            
            return Response({'status': 'Payment verified successfully'})
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)