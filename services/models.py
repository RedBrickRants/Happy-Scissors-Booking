from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration = models.IntegerField(help_text="Duration in minutes")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
# Create your models here.
