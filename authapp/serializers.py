# authapp/serializers.py

from rest_framework import serializers
from .models import CustomUser,ContactSubmission  # Adjust if your import path is different

from rest_framework import serializers
from .models import CertificateRequest


from rest_framework import serializers
from .models import CustomUser, Course
from .models import CustomUser

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_url', 'purchased_at']
class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = '__all__'

class ContactFormSerializer(serializers.ModelSerializer):  # Renamed from ContactSubmissionSerializer
    class Meta:
        model = ContactSubmission
        fields = '__all__'  # Kept original field names (first_name, last_name, etc.)
class UserWithCoursesSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'courses']

class CertificateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateRequest
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email','phone']  # Add any other fields you need


from .models import UserCourseAccess,PaymentRecord

class UserCourseAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourseAccess
        fields = ['course_path', 'access_granted_at', 'last_accessed']

class PaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecord
        fields = '__all__'