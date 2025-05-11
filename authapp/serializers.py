from rest_framework import serializers
from .models import CustomUser, CertificateRequest, PurchasedCourse

class CertificateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateRequest
        fields = '__all__'
        read_only_fields = ['user', 'timestamp']

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'email']

class PurchasedCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasedCourse
        fields = '__all__'
        read_only_fields = ['user', 'purchased_at']

class PurchasedCourseDetailSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchasedCourse
        fields = ['id', 'course_url', 'razorpay_payment_id', 'purchased_at', 'course_name']
        read_only_fields = fields

    def get_course_name(self, obj):
        # Map course URLs to their display names
        course_names = {
            "/htmlcss89": "HTML & CSS Internship",
            "/htmlcssjs62": "HTML, CSS & JS Internship",
            "/python24": "Python Internship",
            "/pythondjango90": "Django + Python Internship",
            "/react79": "React JS Internship",
            "/reactandjs43": "React JS + JavaScript Internship"
        }
        return course_names.get(obj.course_url, obj.course_url)