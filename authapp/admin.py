from django.contrib import admin
from .models import CustomUser, CertificateRequest,UserCourse

admin.site.register(CustomUser, admin.ModelAdmin)
admin.site.register(CertificateRequest)
admin.site.register(UserCourse)