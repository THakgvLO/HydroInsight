from django.contrib.gis.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

# Create your models here.

class WaterQualityStation(models.Model):
    name = models.CharField(max_length=100)
    location = models.PointField(geography=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Additional fields for CSV import
    station_type = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=100, blank=True)
    measurement_start_date = models.DateField(null=True, blank=True)
    measurement_end_date = models.DateField(null=True, blank=True)
    number_of_samples = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class WaterSample(models.Model):
    station = models.ForeignKey(WaterQualityStation, on_delete=models.CASCADE, related_name='samples')
    timestamp = models.DateTimeField()
    ph = models.FloatField()
    turbidity = models.FloatField()
    dissolved_oxygen = models.FloatField()
    temperature = models.FloatField()
    conductivity = models.FloatField(null=True, blank=True)
    total_dissolved_solids = models.FloatField(null=True, blank=True)
    other_data = models.JSONField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Sample at {self.station.name} on {self.timestamp}"
    
    def check_water_quality(self):
        """Check if water quality parameters are within acceptable ranges"""
        issues = []
        
        # pH range: 6.5-8.5 (slightly acidic to slightly alkaline)
        if self.ph < 6.5 or self.ph > 8.5:
            issues.append(f"pH ({self.ph}) outside normal range (6.5-8.5)")
        
        # Turbidity: < 5 NTU (clear water)
        if self.turbidity > 5:
            issues.append(f"High turbidity ({self.turbidity} NTU) - water is cloudy")
        
        # Dissolved oxygen: > 6 mg/L (good for aquatic life)
        if self.dissolved_oxygen < 6:
            issues.append(f"Low dissolved oxygen ({self.dissolved_oxygen} mg/L) - poor for aquatic life")
        
        # Temperature: 10-25°C (reasonable range for most aquatic life)
        if self.temperature < 10 or self.temperature > 25:
            issues.append(f"Temperature ({self.temperature}°C) outside optimal range (10-25°C)")
        
        return issues

class Alert(models.Model):
    ALERT_TYPES = [
        ('water_quality', 'Water Quality Issue'),
        ('equipment', 'Equipment Malfunction'),
        ('maintenance', 'Maintenance Required'),
        ('data_gap', 'Data Gap Detected'),
        ('threshold_exceeded', 'Threshold Exceeded'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    station = models.ForeignKey(WaterQualityStation, on_delete=models.CASCADE, related_name='alerts')
    sample = models.ForeignKey(WaterSample, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    alert_type = models.CharField(max_length=100, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium')
    message = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')

    def __str__(self):
        return f"Alert: {self.alert_type} at {self.station.name} ({'Resolved' if self.resolved else 'Active'})"
    
    def resolve(self, user=None):
        """Mark alert as resolved"""
        from django.utils import timezone
        self.resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()
