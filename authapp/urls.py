from django.urls import path
from .views import SubmitCertificateRequest, GetUserById

urlpatterns = [
    path("certificate/", SubmitCertificateRequest.as_view(), name="certificate-request"),
    path("user/<int:user_id>/", GetUserById.as_view(), name="get-user"),
]
