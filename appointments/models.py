from django.db import models
from django.conf import settings
from services.models import Service
from clients.models import Client

class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    specialization = models.TextField(blank=True)
    services = models.ManyToManyField(Service, related_name='qualified_staff')
    is_active = models.BooleanField(default=True)
    maximum_daily_appointments = models.IntegerField(default=10)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def availability(self):
        # Placeholder for availability logic
        from django.utils import timezone
        today = timezone.now().date()
        days_appointments = self.appointment_set.filter(scheduled_time__date=today).count()
        if days_appointments >= self.maximum_daily_appointments:
            return "Fully Booked"
        return days_appointments < self.maximum_daily_appointments
    

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('canceled', 'Canceled'),
        ('no_show', 'No Show'),
   ]
    
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_time']
    
    def __str__(self):
        return f"{self.client} - {self.service} - {self.scheduled_time}"
    
    def save(self, *args, **kwargs):
        # Automatically set end_time based on service duration
        if not self.end_time:
            from django.utils import timezone
            self.end_time = self.scheduled_time + timezone.timedelta(minutes=self.service.duration)
        super().save(*args, **kwargs)

class BusinessHours(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['day_of_week']
        verbose_name_plural = "Business Hours"
    
    def __str__(self):
        status = f"{self.get_day_of_week_display()}: {self.open_time} - {self.close_time}"
        return f"{self.get_day_of_week_display()}: Closed" if self.is_closed else status