import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from watergis.models import WaterQualityStation
from datetime import datetime


class Command(BaseCommand):
    help = 'Import water quality stations from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        if not os.path.exists(csv_file):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_file}')
            )
            return

        stations_created = 0
        stations_updated = 0

        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    # Parse the CSV data
                    station_number = row.get('StationNumber', '').strip()
                    station_type = row.get('StationType', '').strip()
                    measurement_start = row.get('MeasurementStartDate', '').strip()
                    measurement_end = row.get('MeasurementEndDate', '').strip()
                    num_samples = row.get('Number ofSamples', '0').strip()
                    station_status = row.get('StationStatus', '').strip()

                    # Skip if no station number
                    if not station_number:
                        continue

                    # Try to parse dates with enhanced format support
                    start_date = None
                    end_date = None
                    
                    def parse_date(date_str):
                        if not date_str:
                            return None
                        
                        # Try multiple date formats
                        date_formats = [
                            '%Y-%m-%d',      # 2023-01-01
                            '%d/%m/%Y',      # 01/01/2023
                            '%m/%d/%Y',      # 01/01/2023 (US format)
                            '%d-%m-%Y',      # 01-01-2023
                            '%Y/%m/%d',      # 2023/01/01
                            '%d/%m/%y',      # 01/01/23
                            '%m/%d/%y',      # 01/01/23 (US format)
                            '%d-%b-%Y',      # 30-Nov-2007
                            '%d-%B-%Y',      # 18-September-1995
                        ]
                        
                        # Try standard formats first
                        for fmt in date_formats:
                            try:
                                return datetime.strptime(date_str.strip(), fmt).date()
                            except ValueError:
                                continue
                        
                        # Try with abbreviated month names (case insensitive)
                        try:
                            # Handle formats like "30-Nov-2007" or "18-Sept-1995"
                            import re
                            pattern = r'(\d{1,2})-([A-Za-z]{3,9})-(\d{4})'
                            match = re.match(pattern, date_str.strip())
                            if match:
                                day, month, year = match.groups()
                                day = int(day)
                                year = int(year)
                                
                                # Map common month abbreviations and full names
                                month_map = {
                                    'jan': 1, 'january': 1,
                                    'feb': 2, 'february': 2,
                                    'mar': 3, 'march': 3,
                                    'apr': 4, 'april': 4,
                                    'may': 5,
                                    'jun': 6, 'june': 6,
                                    'jul': 7, 'july': 7,
                                    'aug': 8, 'august': 8,
                                    'sep': 9, 'sept': 9, 'september': 9,
                                    'oct': 10, 'october': 10,
                                    'nov': 11, 'november': 11,
                                    'dec': 12, 'december': 12,
                                }
                                
                                month_num = month_map.get(month.lower())
                                if month_num:
                                    return datetime(year, month_num, day).date()
                        except Exception:
                            pass
                        
                        return None
                    
                    start_date = parse_date(measurement_start)
                    end_date = parse_date(measurement_end)
                    
                    if measurement_start and not start_date:
                        self.stdout.write(
                            self.style.WARNING(f'Could not parse start date: {measurement_start}')
                        )
                    
                    if measurement_end and not end_date:
                        self.stdout.write(
                            self.style.WARNING(f'Could not parse end date: {measurement_end}')
                        )

                    # Parse number of samples
                    try:
                        num_samples = int(num_samples) if num_samples else 0
                    except ValueError:
                        num_samples = 0

                    # Create or update station
                    station, created = WaterQualityStation.objects.get_or_create(
                        name=station_number,
                        defaults={
                            'description': f"Station Type: {station_type}, Status: {station_status}",
                            'location': Point(0, 0),  # Default location, you can update later
                            'station_type': station_type,
                            'status': station_status,
                            'measurement_start_date': start_date,
                            'measurement_end_date': end_date,
                            'number_of_samples': num_samples,
                        }
                    )

                    if created:
                        stations_created += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Created station: {station_number}')
                        )
                    else:
                        # Update existing station
                        station.description = f"Station Type: {station_type}, Status: {station_status}"
                        station.station_type = station_type
                        station.status = station_status
                        station.measurement_start_date = start_date
                        station.measurement_end_date = end_date
                        station.number_of_samples = num_samples
                        station.save()
                        stations_updated += 1
                        self.stdout.write(
                            self.style.WARNING(f'Updated station: {station_number}')
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing row: {row} - {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Import completed! Created: {stations_created}, Updated: {stations_updated}'
            )
        ) 