import csv
import os
import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from watergis.models import WaterQualityStation
from datetime import datetime


class Command(BaseCommand):
    help = 'Import water quality stations from CSV file with automatic coordinate assignment'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument(
            '--assign-coordinates',
            action='store_true',
            help='Automatically assign coordinates based on station type'
        )

    def get_default_coordinates(self, station_type):
        """Assign default coordinates based on station type."""
        # Default coordinates for different water body types
        # These are example coordinates - you can customize these
        coordinates_map = {
            'river': [
                (28.0473, -26.2041),  # Johannesburg area
                (18.4241, -33.9249),  # Cape Town area
                (31.0292, -29.8587),  # Durban area
                (27.9260, -26.1952),  # Pretoria area
                (25.7479, -28.1878),  # Bloemfontein area
            ],
            'lake': [
                (28.0473, -26.2041),
                (18.4241, -33.9249),
                (31.0292, -29.8587),
            ],
            'reservoir': [
                (28.0473, -26.2041),
                (18.4241, -33.9249),
                (31.0292, -29.8587),
            ],
            'stream': [
                (28.0473, -26.2041),
                (18.4241, -33.9249),
                (31.0292, -29.8587),
            ],
            'coastal': [
                (18.4241, -33.9249),  # Cape Town coastal
                (31.0292, -29.8587),  # Durban coastal
                (25.7479, -28.1878),  # Port Elizabeth coastal
            ],
            'well': [
                (28.0473, -26.2041),
                (18.4241, -33.9249),
                (31.0292, -29.8587),
            ],
            'spring': [
                (28.0473, -26.2041),
                (18.4241, -33.9249),
                (31.0292, -29.8587),
            ],
            'estuary': [
                (18.4241, -33.9249),
                (31.0292, -29.8587),
            ],
            'pond': [
                (28.0473, -26.2041),
                (18.4241, -33.9249),
                (31.0292, -29.8587),
            ],
            'canal': [
                (28.0473, -26.2041),
                (18.4241, -33.9249),
                (31.0292, -29.8587),
            ],
        }
        
        # Determine station type category
        station_type_lower = station_type.lower()
        for key in coordinates_map:
            if key in station_type_lower:
                return random.choice(coordinates_map[key])
        
        # Default fallback coordinates
        return (28.0473, -26.2041)  # Johannesburg area

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        assign_coordinates = options['assign_coordinates']
        
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

                    # Try to parse dates with more formats
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

                    # Assign coordinates
                    if assign_coordinates:
                        lng, lat = self.get_default_coordinates(station_type)
                        location = Point(lng, lat)
                        self.stdout.write(
                            self.style.SUCCESS(f'Assigned coordinates ({lat}, {lng}) for {station_number}')
                        )
                    else:
                        # Use default coordinates
                        location = Point(28.0473, -26.2041)

                    # Create or update station
                    station, created = WaterQualityStation.objects.get_or_create(
                        name=station_number,
                        defaults={
                            'description': f"Station Type: {station_type}, Status: {station_status}",
                            'location': location,
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
                        station.location = location
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
        
        if assign_coordinates:
            self.stdout.write(
                self.style.SUCCESS(
                    'Coordinates were automatically assigned based on station type.'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'All stations use default coordinates. Use --assign-coordinates flag for automatic assignment.'
                )
            ) 