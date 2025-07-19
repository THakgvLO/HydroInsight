from django.core.management.base import BaseCommand
from watergis.models import WaterQualityStation, WaterSample, Alert


class Command(BaseCommand):
    help = 'Remove all sample stations and their associated data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting'
        )

    def handle(self, *args, **options):
        # Count existing data
        station_count = WaterQualityStation.objects.count()
        sample_count = WaterSample.objects.count()
        alert_count = Alert.objects.count()
        
        self.stdout.write(f"Current data:")
        self.stdout.write(f"  Stations: {station_count}")
        self.stdout.write(f"  Samples: {sample_count}")
        self.stdout.write(f"  Alerts: {alert_count}")
        
        if not options['confirm']:
            confirm = input("Are you sure you want to delete ALL data? (yes/no): ")
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING("Operation cancelled."))
                return
        
        # Delete all data
        Alert.objects.all().delete()
        WaterSample.objects.all().delete()
        WaterQualityStation.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted {station_count} stations, {sample_count} samples, and {alert_count} alerts."
            )
        ) 