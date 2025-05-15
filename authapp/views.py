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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from cashfree_pg import OrderCreateRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.exceptions import ApiException

class CreateCashfreeOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cashfree = Cashfree(
                x_client_id=settings.CASHFREE_APP_ID,
                x_client_secret=settings.CASHFREE_SECRET_KEY,
                x_api_version=settings.CASHFREE_API_VERSION,
                environment=settings.CASHFREE_ENVIRONMENT
            )

            course_url = request.data.get('course_url')
            amount = request.data.get('amount')
            
            if not course_url or not amount:
                return Response(
                    {"error": "Course URL and amount are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            order_request = OrderCreateRequest(
                order_amount=float(amount),
                order_currency="INR",
                order_id=f"ORDER_{request.user.id}_{int(time.time())}",
                customer_details={
                    "customer_id": str(request.user.id),
                    "customer_email": request.user.email,
                    "customer_phone": request.user.phone if hasattr(request.user, 'phone') else "9999999999"
                },
                order_meta={
                    "return_url": f"{settings.FRONTEND_URL}/payment-success?course_url={course_url}",
                    "notify_url": f"{settings.BACKEND_URL}/api/cashfree-webhook/"
                }
            )

            order_response = cashfree.orders_create_order(order_request)
            return Response({
                "payment_link": order_response.payment_link,
                "order_id": order_response.order_id
            })

        except ApiException as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# authapp/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def cashfree_webhook(request):
    if request.method == 'POST':
        try:
            # Verify webhook signature
            signature = request.headers.get('x-cf-signature')
            raw_body = request.body.decode('utf-8')
            
            # Verify signature here (implementation depends on Cashfree's method)
            
            data = json.loads(raw_body)
            order_id = data.get('orderId')
            payment_status = data.get('txStatus')
            
            if payment_status == 'SUCCESS':
                # Update your database here
                # Example: mark payment as successful
                pass
                
            return JsonResponse({"status": "success"})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)


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
