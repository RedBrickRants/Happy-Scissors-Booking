from django.db import models

# business/models.py - Consider moving these from appointments
class BusinessSettings(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    # ... other business settings

class NotificationSettings(models.Model):
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    # ... other notification settings