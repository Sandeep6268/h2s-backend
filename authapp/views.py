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