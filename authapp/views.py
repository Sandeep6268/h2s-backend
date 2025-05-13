# authapp/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404
from .models import UserCourse




from rest_framework import status
from .models import CertificateRequest
from .serializers import CertificateRequestSerializer


class SaveCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({'error': 'Course ID is required'}, status=400)
        
        # Create the user course record
        UserCourse.objects.create(user=request.user, course_id=course_id)
        return Response({'status': 'success'}, status=201)

class GetUserCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = UserCourse.objects.filter(user=request.user).values_list('course_id', flat=True)
        return Response(list(courses))



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
