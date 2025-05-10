from django.urls import path
from .views import (
    GetUserById,
    SubmitCertificateRequest,
    UserCoursesView,
    RecordCoursePurchase
)

urlpatterns = [
    path('user/<int:user_id>/', GetUserById.as_view(), name='get-user'),
    path('user/<int:user_id>/courses/', UserCoursesView.as_view(), name='user-courses'),
    path('record-purchase/', RecordCoursePurchase.as_view(), name='record-purchase'),
    path('certificate-request/', SubmitCertificateRequest.as_view(), name='certificate-request'),
]