from django.contrib import admin
from .models import CustomUser, CertificateRequest,Course,ContactSubmission

admin.site.register(CustomUser, admin.ModelAdmin)
admin.site.register(CertificateRequest)
admin.site.register(Course)
admin.site.register(ContactSubmission)
