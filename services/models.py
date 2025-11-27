from django.db import models

#service category model consists of different categories of services offered such as hair, nails, spa treitments etc.
class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['display_order', 'name']
    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    duration = models.IntegerField(help_text="Duration in minutes")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)
    requires_appointment = models.BooleanField(default=True)
    requires_specialist = models.BooleanField(default=False)

    class Meta:
        ordering = ['category', 'name']


    def __str__(self):
        return self.name
# Create your models here.
