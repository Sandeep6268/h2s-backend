from rest_framework import serializers
from .models import CustomUser, UserCourse, Course,CertificateRequest

class UserCourseSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name')
    course_id = serializers.CharField(source='course.course_id')
    
    class Meta:
        model = UserCourse
        fields = ['id', 'course_name', 'course_id', 'purchase_date', 'payment_id']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class CertificateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateRequest
        fields = '__all__'