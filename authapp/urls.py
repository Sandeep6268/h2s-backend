from .views import GetUserById
from django.urls import path

urlpatterns = [
    path('user/<int:user_id>/', GetUserById.as_view(), name='get-user'),
]