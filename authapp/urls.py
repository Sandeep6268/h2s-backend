from django.urls import path
from .views import GetUserById, SubmitCertificateRequest,SubmitContactForm,CreateOrderView,VerifyPaymentView,PaymentWebhookView,PurchaseCourseView,UserCoursesView,CourseAccessView,UserCoursesViewPurchased,ContactFormAPI,SendWelcomeEmailView

urlpatterns = [
    path('user/<int:user_id>/', GetUserById.as_view(), name='get-user'),
    path('certificate-request/', SubmitCertificateRequest.as_view(), name='certificate-request'),
    path('purchase-course/', PurchaseCourseView.as_view(), name='purchase-course'),
    path('my-courses/', UserCoursesView.as_view(), name='user-courses'),
    # path('contact/', SubmitContactForm.as_view(), name='contact-submission'),
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('course-access/', CourseAccessView.as_view(), name='course-access'),
    path('user-courses/', UserCoursesViewPurchased.as_view(), name='user-courses'),
    path('contact-us/', ContactFormAPI.as_view(), name='contact-form'),
    path('send-welcome-email/', SendWelcomeEmailView.as_view(), name='send-welcome-email'),

]
