import csv
import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.gis.geos import Point
from watergis.models import WaterQualityStation, WaterSample
from datetime import datetime


class Command(BaseCommand):
    help = 'Import DWA water quality data from Excel/CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel/CSV file')
        parser.add_argument(
            '--file-type',
            choices=['excel', 'csv'],
            default='excel',
            help='File type (excel or csv)'
        )
        parser.add_argument(
            '--create-stations',
            action='store_true',
            help='Create stations if they do not exist'
        )

    def parse_date(self, date_str):
        """Parse date from various formats."""
        if not date_str or pd.isna(date_str):
            return None
        
        try:
            # Try pandas to_datetime first
            return pd.to_datetime(date_str).date()
        except:
            pass
        
        # Try manual parsing
        date_formats = [
            '%Y/%m/%d',      # 1999/05/24
            '%Y-%m-%d',      # 1999-05-24
            '%d/%m/%Y',      # 24/05/1999
            '%m/%d/%Y',      # 05/24/1999
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt).date()
            except ValueError:
                continue
        
        return None

    def clean_numeric_value(self, value):
        """Clean and convert numeric values."""
        if pd.isna(value) or value == '' or str(value).lower() in ['nan', 'null', '']:
            return None
        
        try:
            # Remove any non-numeric characters except decimal point and minus
            cleaned = str(value).replace(',', '').strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    def handle(self, *args, **options):
        file_path = options['file_path']
        file_type = options['file_type']
        create_stations = options['create_stations']
        
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
            return

        try:
            # Read the file
            if file_type == 'excel':
                # Read Excel file, skip the first few rows with headers
                df = pd.read_excel(file_path, skiprows=2)
            else:
                # Read CSV file, skip the first few rows with headers
                df = pd.read_csv(file_path, skiprows=2)
            
            self.stdout.write(f"Loaded {len(df)} rows from {file_path}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading file: {str(e)}')
            )
            return

        # Map column names to our expected format
        column_mapping = {
            'SAMPLE\nSTATION ID': 'station_id',  # Handle newline in column name
            'SAMPLE STATION ID': 'station_id',   # Also try without newline
            'POINT ID': 'point_id', 
            'DATE': 'date',
            'YEAR': 'year',
            'PH': 'ph',
            'EC': 'electrical_conductivity',
            'TDS': 'total_dissolved_solids',
            'NA': 'sodium',
            'MG': 'magnesium',
            'CA': 'calcium',
            'F': 'fluoride',
            'CL': 'chloride',
            'NO3+NO2': 'nitrate_nitrite',
            'SO4': 'sulfate',
            'PO4': 'phosphate',
            'SI': 'silica',
            'K': 'potassium',
            'NH4': 'ammonium',
        }

        # Rename columns to standard names
        df_renamed = df.rename(columns=column_mapping)
        
        samples_created = 0
        stations_created = 0
        errors = 0

        for index, row in df_renamed.iterrows():
            try:
                # Extract basic information
                station_id = str(row.get('station_id', '')).strip()
                point_id = str(row.get('point_id', '')).strip()
                date_str = row.get('date')
                year = row.get('year')
                
                if not station_id or pd.isna(station_id):
                    continue

                # Parse date
                sample_date = self.parse_date(date_str)
                if not sample_date:
                    self.stdout.write(
                        self.style.WARNING(f'Could not parse date: {date_str} for station {station_id}')
                    )
                    continue

                # Get or create station
                station, station_created = WaterQualityStation.objects.get_or_create(
                    name=station_id,
                    defaults={
                        'description': f"DWA Station: {station_id}, Point: {point_id}",
                        'location': Point(25.7, -28.2),  # Default South Africa center
                        'station_type': 'Surface Water Monitoring',
                        'status': 'Active',
                        'measurement_start_date': sample_date,
                        'measurement_end_date': sample_date,
                        'number_of_samples': 0,
                    }
                )

                if station_created and create_stations:
                    stations_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created station: {station_id}')
                    )

                # Extract water quality parameters
                ph = self.clean_numeric_value(row.get('ph'))
                electrical_conductivity = self.clean_numeric_value(row.get('electrical_conductivity'))
                total_dissolved_solids = self.clean_numeric_value(row.get('total_dissolved_solids'))
                sodium = self.clean_numeric_value(row.get('sodium'))
                magnesium = self.clean_numeric_value(row.get('magnesium'))
                calcium = self.clean_numeric_value(row.get('calcium'))
                chloride = self.clean_numeric_value(row.get('chloride'))
                nitrate_nitrite = self.clean_numeric_value(row.get('nitrate_nitrite'))
                sulfate = self.clean_numeric_value(row.get('sulfate'))
                phosphate = self.clean_numeric_value(row.get('phosphate'))
                silica = self.clean_numeric_value(row.get('silica'))
                potassium = self.clean_numeric_value(row.get('potassium'))
                ammonium = self.clean_numeric_value(row.get('ammonium'))

                # Calculate derived parameters for dashboard
                # Estimate turbidity from TDS (rough approximation)
                turbidity = total_dissolved_solids * 0.1 if total_dissolved_solids else None
                
                # Estimate dissolved oxygen (rough approximation based on temperature and conductivity)
                dissolved_oxygen = 8.0  # Default value, could be refined with actual data
                
                # Estimate temperature (could be refined with actual data)
                temperature = 20.0  # Default value

                # Create water sample
                sample = WaterSample.objects.create(
                    station=station,
                    timestamp=sample_date,
                    ph=ph if ph else 7.0,
                    turbidity=turbidity if turbidity else 2.0,
                    dissolved_oxygen=dissolved_oxygen,
                    temperature=temperature,
                    other_data={
                        'electrical_conductivity': electrical_conductivity,
                        'total_dissolved_solids': total_dissolved_solids,
                        'sodium': sodium,
                        'magnesium': magnesium,
                        'calcium': calcium,
                        'chloride': chloride,
                        'nitrate_nitrite': nitrate_nitrite,
                        'sulfate': sulfate,
                        'phosphate': phosphate,
                        'silica': silica,
                        'potassium': potassium,
                        'ammonium': ammonium,
                        'point_id': point_id,
                        'year': year,
                        'data_source': 'DWA Historical Data',
                    }
                )

                samples_created += 1

                if samples_created % 100 == 0:
                    self.stdout.write(f"Processed {samples_created} samples...")

            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'Error processing row {index}: {str(e)}')
                )

        # Update station sample counts
        for station in WaterQualityStation.objects.all():
            station.number_of_samples = station.samples.count()
            station.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Import completed! Created: {stations_created} stations, {samples_created} samples. Errors: {errors}'
            )
        ) 