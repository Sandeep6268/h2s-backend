from django.contrib import admin
from .models import CustomUser, CertificateRequest,Course,ContactSubmission,PaymentRecord,UserCourseAccess

admin.site.register(CustomUser, admin.ModelAdmin)
admin.site.register(CertificateRequest)
admin.site.register(Course)
admin.site.register(ContactSubmission)
admin.site.register(PaymentRecord)
admin.site.register(UserCourseAccess)
