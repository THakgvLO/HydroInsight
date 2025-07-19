import pandas as pd
from django.core.management.base import BaseCommand
from django.utils import timezone
from watergis.models import WaterQualityStation, WaterSample
from datetime import datetime, time
import re

class Command(BaseCommand):
    help = 'Clean water quality data by removing NaN values and fixing timestamps'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Get all samples
        samples = WaterSample.objects.all()
        total_samples = samples.count()
        
        self.stdout.write(f'Total samples before cleaning: {total_samples}')
        
        # Track what we'll clean
        samples_to_delete = []
        samples_to_update = []
        
        # Time word to time mapping
        time_mapping = {
            'midnight': '00:00',
            'noon': '12:00',
            'morning': '08:00',
            'afternoon': '14:00',
            'evening': '18:00',
            'night': '22:00',
            'dawn': '06:00',
            'dusk': '19:00',
            'early morning': '06:00',
            'late evening': '21:00',
            'early afternoon': '13:00',
            'late afternoon': '16:00',
        }
        
        for sample in samples:
            should_delete = False
            should_update = False
            
            # Check for NaN values in numeric fields - only delete if ALL required fields are null
            required_fields = ['ph', 'turbidity', 'dissolved_oxygen', 'temperature']
            null_count = 0
            
            for field in required_fields:
                value = getattr(sample, field)
                if value is None or (isinstance(value, float) and (value != value or value == float('inf') or value == float('-inf'))):
                    null_count += 1
            
            # Only delete if all required fields are null
            if null_count == len(required_fields):
                should_delete = True
            
            # Check timestamp format and convert if needed
            if sample.timestamp:
                timestamp_str = str(sample.timestamp)
                
                # Check if timestamp contains time words
                for word, time_str in time_mapping.items():
                    if word.lower() in timestamp_str.lower():
                        # Extract date part and combine with time
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', timestamp_str)
                        if date_match:
                            date_part = date_match.group(1)
                            try:
                                time_obj = datetime.strptime(time_str, '%H:%M').time()
                                new_datetime = datetime.combine(
                                    datetime.strptime(date_part, '%Y-%m-%d').date(),
                                    time_obj
                                )
                                sample.timestamp = new_datetime
                                should_update = True
                            except:
                                pass
                        break
            
            # Round turbidity to one decimal place
            if sample.turbidity is not None and not (sample.turbidity != sample.turbidity):
                sample.turbidity = round(sample.turbidity, 1)
                should_update = True
            
            if should_delete:
                samples_to_delete.append(sample.id)
            elif should_update:
                samples_to_update.append(sample)
        
        self.stdout.write(f'Samples to delete (NaN values): {len(samples_to_delete)}')
        self.stdout.write(f'Samples to update (timestamp fixes): {len(samples_to_update)}')
        
        if not dry_run:
            # Delete samples with NaN values
            if samples_to_delete:
                WaterSample.objects.filter(id__in=samples_to_delete).delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted {len(samples_to_delete)} samples with NaN values'))
            
            # Update samples with fixed timestamps
            if samples_to_update:
                for sample in samples_to_update:
                    sample.save()
                self.stdout.write(self.style.SUCCESS(f'Updated {len(samples_to_update)} samples with fixed timestamps'))
            
            # Update station sample counts
            for station in WaterQualityStation.objects.all():
                station.number_of_samples = station.samples.count()
                station.save()
            
            final_count = WaterSample.objects.count()
            self.stdout.write(self.style.SUCCESS(f'Final sample count: {final_count}'))
        else:
            self.stdout.write(self.style.WARNING('Dry run completed - no changes made')) 