from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

COURSE_CHOICES = [
    ("htmlcss", "HTML + CSS"),
    ("htmlcssjs", "HTML + CSS + JS"),
    ("python", "Python"),
    ("python_django", "Python + Django"),
    ("react", "React"),
    ("react_js", "React + JavaScript"),
]

class CertificateRequest(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    course = models.CharField(max_length=100)


    def __str__(self):
        return f"{self.name} - {self.course}"