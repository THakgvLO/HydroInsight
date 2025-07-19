from django.db import models
from django.contrib.gis.db import models as gis_models
from django.db.models import JSONField
from watergis.models import WaterQualityStation, WaterSample
from django.utils import timezone
from datetime import timedelta


class StationStatistics(models.Model):
    """Stores calculated statistics for each station"""
    station = models.OneToOneField(WaterQualityStation, on_delete=models.CASCADE, related_name='statistics')
    
    # Sample counts
    total_samples = models.IntegerField(default=0)
    samples_last_30_days = models.IntegerField(default=0)
    samples_last_90_days = models.IntegerField(default=0)
    
    # Parameter statistics
    avg_ph = models.FloatField(null=True, blank=True)
    avg_turbidity = models.FloatField(null=True, blank=True)
    avg_dissolved_oxygen = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)
    
    # Quality indicators
    quality_score = models.FloatField(default=0.0)  # 0-100 scale
    last_sample_date = models.DateTimeField(null=True, blank=True)
    
    # Trend indicators
    ph_trend = models.CharField(max_length=20, default='stable')  # improving, declining, stable
    turbidity_trend = models.CharField(max_length=20, default='stable')
    oxygen_trend = models.CharField(max_length=20, default='stable')
    
    # Metadata
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Station Statistics"
    
    def __str__(self):
        return f"Stats for {self.station.name}"


class SystemOverview(models.Model):
    """System-wide statistics and overview"""
    date = models.DateField(unique=True)
    
    # Overall statistics
    total_stations = models.IntegerField(default=0)
    active_stations = models.IntegerField(default=0)
    total_samples = models.IntegerField(default=0)
    samples_today = models.IntegerField(default=0)
    
    # Quality metrics
    avg_quality_score = models.FloatField(default=0.0)
    stations_with_issues = models.IntegerField(default=0)
    critical_alerts = models.IntegerField(default=0)
    
    # Geographic distribution
    regions_covered = models.IntegerField(default=0)
    provinces_covered = models.IntegerField(default=0)
    
    # Data freshness
    stations_updated_today = models.IntegerField(default=0)
    data_completeness = models.FloatField(default=0.0)  # Percentage
    
    class Meta:
        verbose_name_plural = "System Overviews"
        ordering = ['-date']
    
    def __str__(self):
        return f"System Overview - {self.date}"


class TrendAnalysis(models.Model):
    """Stores trend analysis results"""
    station = models.ForeignKey(WaterQualityStation, on_delete=models.CASCADE, related_name='trends')
    parameter = models.CharField(max_length=50)  # ph, turbidity, dissolved_oxygen, temperature
    period = models.CharField(max_length=20)  # daily, weekly, monthly
    
    # Trend data
    trend_data = JSONField()  # Store time series data
    trend_direction = models.CharField(max_length=20)  # increasing, decreasing, stable
    trend_strength = models.FloatField()  # Correlation coefficient
    forecast_data = JSONField(null=True, blank=True)  # Future predictions
    
    # Metadata
    analysis_date = models.DateTimeField(auto_now_add=True)
    data_points = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Trend Analyses"
        unique_together = ['station', 'parameter', 'period']
    
    def __str__(self):
        return f"{self.station.name} - {self.parameter} ({self.period})"


class ComparativeAnalysis(models.Model):
    """Stores comparative analysis between stations or time periods"""
    analysis_type = models.CharField(max_length=50)  # station_comparison, time_period, regional
    comparison_data = JSONField()  # Store comparison results
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Comparative Analyses"
    
    def __str__(self):
        return f"{self.analysis_type} - {self.created_at.date()}"
