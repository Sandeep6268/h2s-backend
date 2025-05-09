# authapp/serializers.py

from rest_framework import serializers
from .models import CustomUser  # Adjust if your import path is different


from .models import CertificateRequest

class CertificateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateRequest
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']  # Add any other fields you need
