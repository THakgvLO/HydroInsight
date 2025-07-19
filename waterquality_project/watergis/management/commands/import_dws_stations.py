import csv
import os
import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from watergis.models import WaterQualityStation
from datetime import datetime


class Command(BaseCommand):
    help = 'Import DWS Surface Water Monitoring Network stations from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the DWS CSV file')
        parser.add_argument(
            '--assign-coordinates',
            action='store_true',
            help='Automatically assign coordinates based on station type'
        )

    def get_sa_coordinates(self, station_type):
        """Get South African coordinates based on station type."""
        # South African water monitoring coordinates
        sa_coordinates = [
            # Major Rivers
            (20.0, -28.5),   # Orange River
            (27.8, -26.8),   # Vaal River
            (31.5, -24.0),   # Limpopo River
            (20.0, -34.0),   # Breede River
            (30.9, -29.7),   # Umgeni River
            (28.1, -26.9),   # Vaal River (Gauteng)
            (18.4, -33.9),   # Cape Town area
            (31.0, -29.9),   # Durban area
            (25.6, -33.7),   # Port Elizabeth area
            (27.9, -33.0),   # East London area
            (24.7, -30.0),   # Vanderkloof area
            (19.2, -34.1),   # Theewaterskloof area
            (30.2, -29.5),   # Midmar area
            (26.2, -28.7),   # Kimberley area
            (25.7, -28.2),   # Bloemfontein area
        ]
        
        # Use station type to determine location
        station_type_lower = station_type.lower() if station_type else ''
        
        if 'river' in station_type_lower:
            return random.choice(sa_coordinates[:6])  # River locations
        elif 'dam' in station_type_lower or 'reservoir' in station_type_lower:
            return random.choice(sa_coordinates[10:15])  # Dam locations
        elif 'coastal' in station_type_lower or 'estuary' in station_type_lower:
            return random.choice([sa_coordinates[6], sa_coordinates[7], sa_coordinates[8], sa_coordinates[9]])  # Coastal
        elif 'lake' in station_type_lower:
            return random.choice(sa_coordinates[5:10])  # Lake locations
        else:
            return random.choice(sa_coordinates)  # Random SA location

    def parse_date(self, date_str):
        """Parse various date formats."""
        if not date_str or date_str.strip() == '':
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
            import re
            pattern = r'(\d{1,2})-([A-Za-z]{3,9})-(\d{4})'
            match = re.match(pattern, date_str.strip())
            if match:
                day, month, year = match.groups()
                day = int(day)
                year = int(year)
                
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
                    # Parse DWS CSV data
                    station_number = row.get('Station', '').strip()
                    station_name = row.get('Name', '').strip()
                    station_type = row.get('Type', '').strip()
                    open_status = row.get('Open', '').strip()
                    closed_status = row.get('Closed', '').strip()
                    start_date_str = row.get('Start Date', '').strip()
                    end_date_str = row.get('End Date', '').strip()
                    reliable_data = row.get('% Reliable Data', '0').strip()

                    # Skip if no station number
                    if not station_number:
                        continue

                    # Parse dates
                    start_date = self.parse_date(start_date_str)
                    end_date = self.parse_date(end_date_str)
                    
                    # Parse reliable data percentage
                    try:
                        reliable_data = float(reliable_data.replace('%', '')) if reliable_data else 0
                    except ValueError:
                        reliable_data = 0

                    # Determine station status
                    if closed_status and closed_status.lower() != 'null' and closed_status.strip():
                        status = 'Closed'
                    elif open_status and open_status.lower() != 'null' and open_status.strip():
                        status = 'Active'
                    else:
                        status = 'Unknown'

                    # Assign coordinates
                    if assign_coordinates:
                        lng, lat = self.get_sa_coordinates(station_type)
                        location = Point(lng, lat)
                        self.stdout.write(
                            self.style.SUCCESS(f'Assigned coordinates ({lat}, {lng}) for {station_number}')
                        )
                    else:
                        # Use default coordinates
                        location = Point(25.7, -28.2)  # Center of South Africa

                    # Create description
                    description = f"DWS Station: {station_name}"
                    if station_type:
                        description += f", Type: {station_type}"
                    if reliable_data > 0:
                        description += f", Data Reliability: {reliable_data}%"

                    # Create or update station
                    station, created = WaterQualityStation.objects.get_or_create(
                        name=station_number,
                        defaults={
                            'description': description,
                            'location': location,
                            'station_type': station_type or 'Surface Water Monitoring',
                            'status': status,
                            'measurement_start_date': start_date,
                            'measurement_end_date': end_date,
                            'number_of_samples': 0,  # Will be updated when sample data is added
                        }
                    )

                    if created:
                        stations_created += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Created DWS station: {station_number} - {station_name}')
                        )
                    else:
                        # Update existing station
                        station.description = description
                        station.location = location
                        station.station_type = station_type or 'Surface Water Monitoring'
                        station.status = status
                        station.measurement_start_date = start_date
                        station.measurement_end_date = end_date
                        station.save()
                        stations_updated += 1
                        self.stdout.write(
                            self.style.WARNING(f'Updated DWS station: {station_number} - {station_name}')
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing row: {row} - {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'DWS import completed! Created: {stations_created}, Updated: {stations_updated}'
            )
        )
        
        if assign_coordinates:
            self.stdout.write(
                self.style.SUCCESS(
                    'Coordinates were automatically assigned based on station type and South African water bodies.'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'All stations use default coordinates. Use --assign-coordinates flag for automatic assignment.'
                )
            ) 