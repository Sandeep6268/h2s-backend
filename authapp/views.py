from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import generics
from .models import CustomUser, CertificateRequest, PurchasedCourse
from .serializers import (
    CustomUserSerializer, 
    CertificateRequestSerializer, 
    PurchasedCourseSerializer,
    PurchasedCourseDetailSerializer
)
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

class SubmitCertificateRequest(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Add the current user to the request data
        request.data['user'] = request.user.id
        serializer = CertificateRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Certificate request submitted successfully!'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

class GetUserById(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # Ensure users can only access their own data
        if request.user.id != user_id:
            return Response(
                {'detail': 'You do not have permission to access this user.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

class SavePurchase(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        
        serializer = PurchasedCourseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Purchase saved successfully',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

class GetUserCourses(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = PurchasedCourse.objects.filter(user=request.user).order_by('-purchased_at')
        serializer = PurchasedCourseDetailSerializer(courses, many=True)
        return Response(serializer.data)

class PurchasedCourseList(generics.ListAPIView):
    serializer_class = PurchasedCourseDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        # Verify the requesting user matches the requested user
        if self.request.user.id != int(user_id):
            return PurchasedCourse.objects.none()
        return PurchasedCourse.objects.filter(user__id=user_id).order_by('-purchased_at')