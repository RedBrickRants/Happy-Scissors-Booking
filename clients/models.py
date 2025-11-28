from django.db import models
from django.conf import settings

class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    preferences = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    loyalty_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def total_appointments(self):
        return self.appointment_set.count()
    
    @property
    def upcoming_appointments(self):
        from django.utils import timezone
        return self.appointment_set.filter(scheduled_time__gte=timezone.now(), status__in = ['pending', 'confirmed']).order_by('scheduled_time')   
