import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from watergis.models import WaterQualityStation


class Command(BaseCommand):
    help = 'Update coordinates for existing stations based on station type'

    def get_coordinates_for_type(self, station_type):
        """Get coordinates based on station type with better distribution."""
        # South African coordinates with better distribution
        sa_coordinates = [
            (18.4241, -33.9249),  # Cape Town
            (31.0292, -29.8587),  # Durban
            (28.0473, -26.2041),  # Johannesburg
            (27.9260, -26.1952),  # Pretoria
            (25.7479, -28.1878),  # Bloemfontein
            (24.9911, -29.8587),  # Pietermaritzburg
            (22.9375, -30.5595),  # East London
            (25.7479, -28.1878),  # Port Elizabeth
            (26.1952, -28.7282),  # Kimberley
            (26.1952, -29.8587),  # Newcastle
            (27.9260, -26.1952),  # Centurion
            (18.4241, -33.9249),  # Stellenbosch
            (31.0292, -29.8587),  # Richards Bay
            (25.7479, -28.1878),  # Uitenhage
            (26.1952, -28.7282),  # Welkom
        ]
        
        # Use station type to determine which coordinates to use
        station_type_lower = station_type.lower() if station_type else ''
        
        # Assign different coordinate sets based on station type
        if 'river' in station_type_lower:
            return random.choice(sa_coordinates[:5])  # Major cities
        elif 'lake' in station_type_lower:
            return random.choice(sa_coordinates[5:10])  # Medium cities
        elif 'reservoir' in station_type_lower:
            return random.choice(sa_coordinates[10:15])  # Smaller cities
        elif 'stream' in station_type_lower:
            return random.choice(sa_coordinates[:8])  # Various locations
        elif 'coastal' in station_type_lower:
            return random.choice([sa_coordinates[0], sa_coordinates[1], sa_coordinates[7]])  # Coastal cities
        elif 'well' in station_type_lower:
            return random.choice(sa_coordinates[3:8])  # Inland cities
        elif 'spring' in station_type_lower:
            return random.choice(sa_coordinates[5:12])  # Various locations
        elif 'estuary' in station_type_lower:
            return random.choice([sa_coordinates[0], sa_coordinates[1], sa_coordinates[7]])  # Coastal
        elif 'pond' in station_type_lower:
            return random.choice(sa_coordinates[8:15])  # Smaller locations
        elif 'canal' in station_type_lower:
            return random.choice(sa_coordinates[2:7])  # Urban areas
        else:
            # Default: random South African location
            return random.choice(sa_coordinates)
        
        station_type_lower = station_type.lower() if station_type else ''
        for key in coordinates_map:
            if key in station_type_lower:
                return random.choice(coordinates_map[key])
        
        # Default fallback coordinates
        return (28.0473, -26.2041)  # Johannesburg area

    def handle(self, *args, **options):
        stations = WaterQualityStation.objects.all()
        updated_count = 0

        for station in stations:
            # Check if station has default coordinates (0,0) or needs updating
            current_location = station.location
            if (current_location.x == 0 and current_location.y == 0) or \
               (current_location.x == 28.0473 and current_location.y == -26.2041):
                
                # Assign new coordinates based on station type
                lng, lat = self.get_coordinates_for_type(station.station_type)
                station.location = Point(lng, lat)
                station.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated {station.name} ({station.station_type}) to coordinates ({lat}, {lng})'
                    )
                )
                updated_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipped {station.name} - already has coordinates ({current_location.y}, {current_location.x})'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f'Updated coordinates for {updated_count} stations')
        ) 