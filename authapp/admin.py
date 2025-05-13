from django.contrib import admin
from .models import CustomUser, CertificateRequest,Course

admin.site.register(CustomUser, admin.ModelAdmin)
admin.site.register(CertificateRequest)
admin.site.register(Course)