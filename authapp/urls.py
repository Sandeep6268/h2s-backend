from django.urls import path
from .views import (
    GetUserById,
    SubmitCertificateRequest,
    SavePurchase,
    GetUserCourses,
    PurchasedCourseList
)

urlpatterns = [
    path('user/<int:user_id>/', GetUserById.as_view(), name='get-user'),
    path('certificate-request/', SubmitCertificateRequest.as_view(), name='certificate-request'),
    path('purchase/', SavePurchase.as_view(), name='save-purchase'),
    path('my-courses/', GetUserCourses.as_view(), name='get-user-courses'),
    path('purchased-courses/<int:user_id>/', PurchasedCourseList.as_view(), name='purchased-courses'),
]