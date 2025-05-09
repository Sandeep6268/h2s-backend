from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,CertificateRequest


admin.site.register(CertificateRequest)
admin.site.register(CustomUser, UserAdmin)
