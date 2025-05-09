from .views import GetUserById,CertificateRequestView
from django.urls import path

urlpatterns = [
    path('user/<int:user_id>/', GetUserById.as_view(), name='get-user'),
    path("certificate/", CertificateRequestView.as_view(), name="certificate-request"),
]