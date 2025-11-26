from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('client', 'Client'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"
# Create your models here.
