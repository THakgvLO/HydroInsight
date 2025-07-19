import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waterquality.settings')

app = Celery('waterquality')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Periodic tasks configuration
app.conf.beat_schedule = {
    # Check for water quality issues every hour
    'check-water-quality-hourly': {
        'task': 'watergis.tasks.check_water_quality',
        'schedule': crontab(minute=0),  # Every hour at minute 0
    },
    
    # Generate alerts for issues daily at 8 AM
    'generate-alerts-daily': {
        'task': 'watergis.tasks.generate_alerts',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
    
    # Clean old data weekly on Sunday at 2 AM
    'clean-old-data-weekly': {
        'task': 'watergis.tasks.clean_old_data',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Sunday at 2 AM
    },
    
    # Update station statistics daily at 6 AM
    'update-station-stats-daily': {
        'task': 'watergis.tasks.update_station_statistics',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 