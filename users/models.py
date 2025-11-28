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
    
    # Remove the problematic properties and use methods instead
    def is_admin_user(self):
        return self.user_type == 'admin'
    
    def is_staff_user(self):
        return self.user_type == 'staff'
    
    def is_client_user(self):
        return self.user_type == 'client'
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"