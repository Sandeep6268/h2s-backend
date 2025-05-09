from django.contrib import admin
from .models import CustomUser, CertificateRequest

admin.site.register(CustomUser, admin.ModelAdmin)
admin.site.register(CertificateRequest)