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
from rest_framework.permissions import IsAuthenticated,AllowAny
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

class ContactFormAPI(APIView):  # Renamed from SubmitContactForm
    def post(self, request):
        serializer = ContactSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Thank you for your submission!"}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class SubmitContactForm(APIView):
    permission_classes = [AllowAny]  # Explicitly allow anyone to access
    
    def post(self, request):
        print("Received data:", request.data)  # Add this line
        serializer = ContactSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Thank you for your submission!'}, status=status.HTTP_201_CREATED)
        print("Validation errors:", serializer.errors)  # Add this line
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
        





from .models import UserCourseAccess
from .serializers import UserCourseAccessSerializer

class CourseAccessView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            course_path = request.data.get('course_path')
            
            # Validate course path format
            if not course_path or not course_path.startswith('/'):
                return Response(
                    {"error": "Invalid course path"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if access already exists
            if UserCourseAccess.objects.filter(
                user=request.user, 
                course_path=course_path
            ).exists():
                return Response(
                    {"message": "Access already granted"},
                    status=status.HTTP_200_OK
                )
            
            # Create new access record
            UserCourseAccess.objects.create(
                user=request.user,
                course_path=course_path
            )
            
            return Response(
                {"message": "Course access granted"},
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        try:
            accesses = UserCourseAccess.objects.filter(user=request.user)
            serializer = UserCourseAccessSerializer(accesses, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class UserCoursesViewPurchased(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            courses = UserCourseAccess.objects.filter(
                user=request.user
            ).order_by('-access_granted_at')
            
            # Format to match what your frontend expects
            data = [{
                'course_path': course.course_path,
                'access_granted_at': course.access_granted_at
            } for course in courses]
            
            return Response(data)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )