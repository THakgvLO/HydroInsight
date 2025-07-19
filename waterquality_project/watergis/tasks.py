from celery import shared_task
from django.utils import timezone
from django.core.management import call_command
from datetime import timedelta
from .models import WaterSample, WaterQualityStation, Alert

@shared_task
def check_water_quality():
    """Check recent water quality samples for issues"""
    from .management.commands.generate_alerts import Command as AlertCommand
    
    # Run alert generation for last 24 hours
    alert_cmd = AlertCommand()
    alert_cmd.handle(check_recent=24)
    
    return f"Water quality check completed at {timezone.now()}"

@shared_task
def generate_alerts():
    """Generate alerts for water quality issues"""
    from .management.commands.generate_alerts import Command as AlertCommand
    
    alert_cmd = AlertCommand()
    alert_cmd.handle(check_recent=168)  # Last 7 days
    
    return f"Alert generation completed at {timezone.now()}"

@shared_task
def clean_old_data():
    """Clean old water quality data"""
    # Remove samples older than 5 years
    cutoff_date = timezone.now() - timedelta(days=5*365)
    old_samples = WaterSample.objects.filter(timestamp__lt=cutoff_date)
    count = old_samples.count()
    old_samples.delete()
    
    # Update station sample counts
    for station in WaterQualityStation.objects.all():
        station.number_of_samples = station.samples.count()
        station.save()
    
    return f"Cleaned {count} old samples at {timezone.now()}"

@shared_task
def update_station_statistics():
    """Update station statistics and metadata"""
    for station in WaterQualityStation.objects.all():
        samples = station.samples.all()
        
        if samples.exists():
            # Update measurement date range
            station.measurement_start_date = samples.earliest('timestamp').timestamp.date()
            station.measurement_end_date = samples.latest('timestamp').timestamp.date()
            station.number_of_samples = samples.count()
            
            # Update status based on recent activity
            last_sample = samples.latest('timestamp')
            days_since_last = (timezone.now() - last_sample.timestamp).days
            
            if days_since_last <= 7:
                station.status = 'Active'
            elif days_since_last <= 30:
                station.status = 'Inactive'
            else:
                station.status = 'Offline'
            
            station.save()
    
    return f"Station statistics updated at {timezone.now()}"

@shared_task
def process_real_time_data():
    """Process real-time data from live monitoring stations"""
    # This task would be triggered by real-time data feeds
    # For now, it's a placeholder for future live data integration
    
    # Example: Process data from IoT sensors, API feeds, etc.
    # This would create new WaterSample objects and trigger immediate alerts
    
    return f"Real-time data processing completed at {timezone.now()}" 