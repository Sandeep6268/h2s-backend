# authapp/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from .models import CertificateRequest


@api_view(["POST"])
def submit_certificate_request(request):
    data = request.data
    try:
        CertificateRequest.objects.create(
            name=data["name"],
            mobile=data["mobile"],
            email=data["email"],
            course=data["course"]
        )
        return Response({"message": "Certificate request submitted successfully!"}, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

class GetUserById(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
