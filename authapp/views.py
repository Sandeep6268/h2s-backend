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



from .models import ContactSubmission,Course
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


# class UserCoursesView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         courses = Course.objects.filter(user=request.user)
#         serializer = CourseSerializer(courses, many=True)
#         return Response(serializer.data)

class PurchaseCourseView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        course_url = request.data.get('course_url')
        
        if not course_url:
            return Response({"error": "Course URL is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate course URL
        valid_courses = dict(Course.COURSE_CHOICES).keys()
        if course_url not in valid_courses:
            return Response({"error": "Invalid course URL"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if user already has this course
        if Course.objects.filter(user=request.user, course_url=course_url).exists():
            return Response({"error": "You already have access to this course"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Save to database
            course = Course.objects.create(
                user=request.user,
                course_url=course_url
            )
            
            return Response({
                "message": "Course purchased successfully!",
                "course_id": course.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = Course.objects.filter(user=request.user)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    

# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import json
import logging
from .models import Course
from .razorpay_utils import razorpay_client

logger = logging.getLogger(__name__)

@csrf_exempt
def razorpay_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    try:
        payload = request.body.decode('utf-8')
        received_sig = request.headers.get('X-Razorpay-Signature', '')
        
        # 1. Verify webhook signature using Razorpay's built-in method
        razorpay_client.utility.verify_webhook_signature(
            payload,
            received_sig,
            settings.RAZORPAY_WEBHOOK_SECRET
        )
        
        data = json.loads(payload)
        event_type = data.get('event')
        
        # 2. Process only payment success events
        if event_type == 'payment.captured':
            payment_data = data['payload']['payment']['entity']
            
            # 3. Validate required fields
            required_fields = ['id', 'notes']
            if not all(field in payment_data for field in required_fields):
                logger.error("Missing required payment fields")
                return HttpResponse(status=400)
                
            if not all(k in payment_data['notes'] for k in ['user_id', 'course_url']):
                logger.error("Missing required note fields")
                return HttpResponse(status=400)
            
            # 4. Save to database
            try:
                Course.objects.get_or_create(
                    user_id=payment_data['notes']['user_id'],
                    course_url=payment_data['notes']['course_url'],
                    defaults={
                        'purchased_at': payment_data.get('created_at')
                    }
                )
                logger.info(f"Course registered for user {payment_data['notes']['user_id']}")
                return HttpResponse(status=200)
                
            except IntegrityError:
                logger.warning("Duplicate course purchase detected")
                return HttpResponse(status=200)  # Still return 200 to prevent retries
                
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                return HttpResponse(status=500)
                
        return HttpResponse(status=200)
        
    except razorpay.errors.SignatureVerificationError:
        logger.warning("Invalid webhook signature")
        return HttpResponse(status=400)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON payload")
        return HttpResponse(status=400)
        
    except Exception as e:
        logger.critical(f"Webhook processing failed: {str(e)}")
        return HttpResponse(status=500)

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
import time
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get and validate amount
            amount_str = request.data.get('amount')
            if not amount_str:
                return Response(
                    {'error': 'Amount is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                amount = int(float(amount_str) * 100)  # Convert to paise
                if amount <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid amount. Must be a positive number'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create Razorpay order
            data = {
                'amount': amount,
                'currency': 'INR',
                'receipt': f"receipt_{request.user.id}_{int(time.time())}",
                'payment_capture': '1'  # Auto-capture
            }
            
            order = client.order.create(data=data)
            
            return Response({
                'id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'status': 'created'
            })
            
        except Exception as e:
            print(f"Order creation error: {str(e)}")
            return Response(
                {'error': f'Order creation failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

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
                # Here you can add any post-payment logic like sending emails, etc.
                # But no database storage
                pass
                
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
            
            # Verify payment signature with Razorpay
            client.utility.verify_payment_signature(data)
            
            # If verification succeeds, return success
            # No database storage involved
            return Response({'status': 'Payment verified successfully'})
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)