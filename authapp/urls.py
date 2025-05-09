from .views import GetUserById,submit_certificate_request
from django.urls import path

urlpatterns = [
    path('user/<int:user_id>/', GetUserById.as_view(), name='get-user'),
    path("certificate/", submit_certificate_request, name="certificate-request"),
]