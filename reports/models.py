from django.db import models
from django.conf import settings

# reports/models.py - For storing generated reports
class Report(models.Model):
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50)
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Store report data
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)