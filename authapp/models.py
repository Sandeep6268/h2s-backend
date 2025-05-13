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
