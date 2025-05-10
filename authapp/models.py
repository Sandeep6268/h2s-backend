from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Course(models.Model):
    COURSE_CHOICES = [
        ('htmlcss89', 'HTML + CSS'),
        ('htmlcssjs62', 'HTML + CSS + JS'),
        ('python24', 'Python'),
        ('pythondjango90', 'Python + Django'),
        ('react79', 'React'),
        ('reactandjs43', 'React + JavaScript'),
    ]
    
    course_id = models.CharField(max_length=20, choices=COURSE_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name

class UserCourse(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('user', 'course')

class CertificateRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.course.name}"