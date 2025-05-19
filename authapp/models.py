from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# authapp/models.py

# models.py
class Course(models.Model):
    COURSE_CHOICES = [
        ('/htmlcss89', 'HTML + CSS'),
        ('/htmlcssjs62', 'HTML + CSS + JS'),
        ('/python24', 'Python'),
        ('/pythondjango90', 'Python + Django'),
        ('/react79', 'React'),
        ('/reactandjs43', 'React + JavaScript'),
    ]
    
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    course_url = models.CharField(max_length=50, choices=COURSE_CHOICES)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course_url}"

   

#     def __str__(self):
#         return f"{self.user.email} - {self.get_course_url_display()} "

class ContactSubmission(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

class CertificateRequest(models.Model):
    COURSE_CHOICES = [
        ('htmlcss', 'HTML + CSS'),
        ('htmlcssjs', 'HTML + CSS + JS'),
        ('python', 'Python'),
        ('pythondjango', 'Python + Django'),
        ('react', 'React'),
        ('reactjs', 'React + JavaScript'),
    ]

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    course = models.CharField(max_length=20, choices=COURSE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.course}"
    

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email



class UserCourseAccess(models.Model):
    """Tracks course access without duplicating purchase records"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course_path = models.CharField(max_length=100)  # e.g. "/python24"
    access_granted_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Course Access"
        # unique_together = ('user', 'course_path')
    def __str__(self):
        return f'{self.user.username} - {self.course_path}'

class PaymentRecord(models.Model):
    """Stores payment verification data"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=255, unique=True)
    razorpay_payment_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    course_path = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)