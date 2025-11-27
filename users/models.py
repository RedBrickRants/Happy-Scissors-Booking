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
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def is_staff(self):
        return self.user_type == 'staff'
    
    @property
    def is_client(self):
        return self.user_type == 'client'
