

from django.db import models

class WeatherData(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    detailing_type = models.CharField(max_length=20)
    data = models.JSONField()
    last_updated = models.DateTimeField()
