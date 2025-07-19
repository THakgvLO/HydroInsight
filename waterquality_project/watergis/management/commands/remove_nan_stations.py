from django.core.management.base import BaseCommand
from watergis.models import WaterSample, WaterQualityStation

class Command(BaseCommand):
    help = 'Remove samples with NaN or empty station names'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be removed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Find samples with NaN or empty station names
        samples_to_delete = WaterSample.objects.filter(station__name__isnull=True)
        nan_station_count = samples_to_delete.count()
        
        # Also find samples where station name is 'nan' (string)
        nan_string_samples = WaterSample.objects.filter(station__name='nan')
        nan_string_count = nan_string_samples.count()
        
        total_to_delete = nan_station_count + nan_string_count
        
        self.stdout.write(f'Samples with null station names: {nan_station_count}')
        self.stdout.write(f'Samples with "nan" station names: {nan_string_count}')
        self.stdout.write(f'Total samples to delete: {total_to_delete}')
        
        if not dry_run and total_to_delete > 0:
            # Delete samples with null station names
            if nan_station_count > 0:
                samples_to_delete.delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted {nan_station_count} samples with null station names'))
            
            # Delete samples with 'nan' station names
            if nan_string_count > 0:
                nan_string_samples.delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted {nan_string_count} samples with "nan" station names'))
            
            # Update station sample counts
            for station in WaterQualityStation.objects.all():
                station.number_of_samples = station.samples.count()
                station.save()
            
            final_count = WaterSample.objects.count()
            self.stdout.write(self.style.SUCCESS(f'Final sample count: {final_count}'))
        else:
            self.stdout.write(self.style.WARNING('Dry run completed - no changes made')) 