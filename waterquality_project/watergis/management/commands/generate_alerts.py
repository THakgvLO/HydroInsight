from django.core.management.base import BaseCommand
from django.utils import timezone
from watergis.models import WaterSample, Alert, WaterQualityStation
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate alerts for water quality issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-recent',
            type=int,
            default=24,
            help='Check samples from last N hours (default: 24)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what alerts would be generated without creating them',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        hours_back = options['check_recent']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No alerts will be created'))
        
        # Get recent samples
        cutoff_time = timezone.now() - timedelta(hours=hours_back)
        recent_samples = WaterSample.objects.filter(timestamp__gte=cutoff_time)
        
        self.stdout.write(f'Checking {recent_samples.count()} samples from last {hours_back} hours')
        
        alerts_created = 0
        
        for sample in recent_samples:
            # Check for water quality issues
            issues = sample.check_water_quality()
            
            if issues:
                # Determine severity based on number and type of issues
                severity = 'low'
                if len(issues) >= 3:
                    severity = 'critical'
                elif len(issues) >= 2:
                    severity = 'high'
                
                # Check if alert already exists for this sample
                existing_alert = Alert.objects.filter(
                    sample=sample,
                    alert_type='water_quality',
                    resolved=False
                ).first()
                
                if not existing_alert:
                    message = f"Water quality issues detected: {'; '.join(issues)}"
                    
                    if not dry_run:
                        Alert.objects.create(
                            station=sample.station,
                            sample=sample,
                            alert_type='water_quality',
                            severity=severity,
                            message=message
                        )
                        alerts_created += 1
                    else:
                        self.stdout.write(f'Would create alert: {message}')
        
        # Check for data gaps (stations with no recent data)
        for station in WaterQualityStation.objects.filter(status='Active'):
            last_sample = station.samples.order_by('-timestamp').first()
            
            if last_sample:
                time_since_last = timezone.now() - last_sample.timestamp
                
                # Alert if no data for more than 7 days
                if time_since_last > timedelta(days=7):
                    existing_gap_alert = Alert.objects.filter(
                        station=station,
                        alert_type='data_gap',
                        resolved=False
                    ).first()
                    
                    if not existing_gap_alert:
                        message = f"No data received for {time_since_last.days} days"
                        
                        if not dry_run:
                            Alert.objects.create(
                                station=station,
                                alert_type='data_gap',
                                severity='medium',
                                message=message
                            )
                            alerts_created += 1
                        else:
                            self.stdout.write(f'Would create data gap alert: {station.name} - {message}')
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'Created {alerts_created} new alerts'))
        else:
            self.stdout.write(self.style.WARNING('Dry run completed - no alerts created')) 