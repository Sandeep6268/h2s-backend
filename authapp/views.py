from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import CustomUser, UserCourse, Course
from .serializers import UserCourseSerializer, CustomUserSerializer, CertificateRequestSerializer
from rest_framework import status

class GetUserById(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if request.user.id != user_id:
            return Response({"error": "Unauthorized"}, status=403)
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

class UserCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if request.user.id != user_id:
            return Response({"error": "Unauthorized"}, status=403)
            
        courses = UserCourse.objects.filter(user_id=user_id).select_related('course')
        serializer = UserCourseSerializer(courses, many=True)
        return Response(serializer.data)

class RecordCoursePurchase(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        course_id = request.data.get('course_id')
        course_name = request.data.get('course_name')
        payment_id = request.data.get('payment_id')
        
        if not all([course_id, payment_id]):
            return Response({"error": "Missing required fields"}, status=400)
            
        course = get_object_or_404(Course, course_id=course_id)
        
        if UserCourse.objects.filter(user=user, course=course).exists():
            return Response({"error": "Course already purchased"}, status=400)
            
        UserCourse.objects.create(
            user=user,
            course=course,
            payment_id=payment_id
        )
        
        return Response({
            "message": "Course purchase recorded successfully",
            "course_id": course_id,
            "course_name": course.name
        }, status=201)

class SubmitCertificateRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CertificateRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'message': 'Certificate request submitted!'}, status=201)
        return Response(serializer.errors, status=400)