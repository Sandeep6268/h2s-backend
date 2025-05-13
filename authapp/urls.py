from django.urls import path
from .views import GetUserById, SubmitCertificateRequest
from .views import save_course, get_user_courses

urlpatterns = [
    path('user/<int:user_id>/', GetUserById.as_view(), name='get-user'),
    path('certificate-request/', SubmitCertificateRequest.as_view(), name='certificate-request'),
    path('save-course/', save_course, name='save-course'),
    path('get-courses/', get_user_courses, name='get-courses'),

]