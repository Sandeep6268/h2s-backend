from django.contrib.auth.models import AbstractUser
from django.db import models


# authapp/models.py

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

class ContactSubmission(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


# models.py
class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True)
    cashfree_order_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    course_url = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('CREATED', 'Created'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order_id} - {self.status}"