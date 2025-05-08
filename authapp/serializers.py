# authapp/serializers.py

from rest_framework import serializers
from .models import CustomUser  # Adjust if your import path is different

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']  # Add any other fields you need
