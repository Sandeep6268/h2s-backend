from django.urls import path
from .views import GetUserById, SubmitCertificateRequest,PurchaseCourseView,UserCoursesView,SubmitContactForm

urlpatterns = [
    path('user/<int:user_id>/', GetUserById.as_view(), name='get-user'),
    path('certificate-request/', SubmitCertificateRequest.as_view(), name='certificate-request'),
    path('purchase-course/', PurchaseCourseView.as_view(), name='purchase-course'),
    path('my-courses/', UserCoursesView.as_view(), name='user-courses'),
    path('contact/', SubmitContactForm.as_view(), name='contact-submission'),
]