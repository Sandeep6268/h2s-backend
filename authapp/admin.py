from django.contrib import admin
from .models import CustomUser, CertificateRequest

admin.site.register(CustomUser, admin.ModelAdmin)
# admin.site.register(CertificateRequest)
@admin.register(CertificateRequest)
class CertificateRequestAdmin(admin.ModelAdmin):
    readonly_fields = ['name', 'email', 'mobile', 'course', 'timestamp']

    def has_delete_permission(self, request, obj=None):
        return False
