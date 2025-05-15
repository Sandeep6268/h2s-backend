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
from cashfree_pg.models import OrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.exceptions import ApiException
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import time

class CreateCashfreeOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Initialize Cashfree client
            cashfree = Cashfree(
                x_client_id=settings.CASHFREE['APP_ID'],
                x_client_secret=settings.CASHFREE['SECRET_KEY'],
                x_api_version=settings.CASHFREE['API_VERSION'],
                environment=settings.CASHFREE['ENVIRONMENT']
            )

            # Get course details from request
            course_url = request.data.get('course_url')
            amount = request.data.get('amount')  # Amount should be in INR
            
            if not course_url or not amount:
                return Response(
                    {"error": "Course URL and amount are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create order request
            order_request = OrderRequest(
                order_amount=float(amount),
                order_currency="INR",
                order_id=f"ORDER_{request.user.id}_{int(time.time())}",
                customer_details={
                    "customer_id": str(request.user.id),
                    "customer_email": request.user.email,
                    "customer_phone": getattr(request.user, 'phone', "9999999999")
                },
                order_meta={
                    "return_url": f"https://h2stechsolutions.netlify.app/payment-success?course_url={course_url}",
                    "notify_url": "https://h2s-backend-urrt.onrender.com/api/cashfree-webhook/"
                }
            )
            

            # Create order
            order_response = cashfree.orders_create_order(order_request)

            # Return payment link to frontend
            return Response({
                "payment_link": order_response.payment_link,
                "order_id": order_response.order_id
            })

        except ApiException as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def cashfree_webhook(request):
    if request.method == 'POST':
        try:
            # Verify the webhook signature
            signature = request.headers.get('x-cf-signature')
            raw_body = request.body.decode('utf-8')
            
            # You should verify the signature here using your secret key
            # Implementation depends on Cashfree's signature generation method
            
            data = json.loads(raw_body)
            order_id = data.get('orderId')
            payment_status = data.get('txStatus')
            
            if payment_status == 'SUCCESS':
                # Get course URL from order meta or other identifier
                # Here you would typically save the payment confirmation
                # and grant access to the course
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
