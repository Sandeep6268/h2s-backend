# authapp/serializers.py

from rest_framework import serializers
from .models import CustomUser,ContactSubmission  # Adjust if your import path is different

from rest_framework import serializers
from .models import CertificateRequest


from rest_framework import serializers
# from .models import CustomUser, Course
from .models import CustomUser

# class CourseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Course
#         fields = ['course_url', 'purchased_at']
class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = '__all__'
# class UserWithCoursesSerializer(serializers.ModelSerializer):
#     courses = CourseSerializer(many=True, read_only=True)
    
#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'email', 'courses']

class CertificateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateRequest
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']  # Add any other fields you need


from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('user', 'status', 'created_at')