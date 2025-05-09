# authapp/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from .models import CertificateRequest
from rest_framework import status


class SubmitCertificateRequest(APIView):
    def post(self, request):
        data = request.data
        required_fields = ["name", "mobile", "email", "course"]

        for field in required_fields:
            if field not in data or not data[field]:
                return Response(
                    {"error": f"Missing field: {field}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            CertificateRequest.objects.create(
                name=data["name"],
                mobile=data["mobile"],
                email=data["email"],
                course=data["course"]
            )
            return Response(
                {"message": "Certificate request submitted successfully!"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetUserById(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
