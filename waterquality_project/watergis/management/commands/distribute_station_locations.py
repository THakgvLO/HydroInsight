import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from watergis.models import WaterQualityStation

class Command(BaseCommand):
    help = 'Distribute station locations across South Africa'

    def handle(self, *args, **options):
        # South Africa bounding box (approximate)
        # Longitude: 16.5 to 32.9 (East)
        # Latitude: -34.8 to -22.1 (South)
        
        stations = WaterQualityStation.objects.all()
        total_stations = stations.count()
        
        self.stdout.write(f'Distributing {total_stations} stations across South Africa...')
        
        # Create a grid of locations to ensure good distribution
        grid_size = int(total_stations ** 0.5) + 1  # Square root for grid
        
        # South Africa coordinates
        min_lon, max_lon = 16.5, 32.9
        min_lat, max_lat = -34.8, -22.1
        
        # Create grid points
        lon_step = (max_lon - min_lon) / grid_size
        lat_step = (max_lat - min_lat) / grid_size
        
        grid_points = []
        for i in range(grid_size):
            for j in range(grid_size):
                lon = min_lon + (i * lon_step) + (lon_step * 0.5)
                lat = min_lat + (j * lat_step) + (lat_step * 0.5)
                grid_points.append((lon, lat))
        
        # Shuffle grid points for random distribution
        random.shuffle(grid_points)
        
        # Assign locations to stations
        for i, station in enumerate(stations):
            if i < len(grid_points):
                lon, lat = grid_points[i]
                
                # Add some random variation within the grid cell
                lon_variation = random.uniform(-lon_step * 0.3, lon_step * 0.3)
                lat_variation = random.uniform(-lat_step * 0.3, lat_step * 0.3)
                
                final_lon = lon + lon_variation
                final_lat = lat + lat_variation
                
                # Ensure coordinates stay within South Africa
                final_lon = max(min_lon, min(max_lon, final_lon))
                final_lat = max(min_lat, min(max_lat, final_lat))
                
                station.location = Point(final_lon, final_lat)
                station.save()
                
                if i % 100 == 0:
                    self.stdout.write(f'Updated {i} stations...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully distributed {total_stations} stations across South Africa'))
        
        # Show sample of new locations
        self.stdout.write('Sample station locations:')
        for station in WaterQualityStation.objects.all()[:5]:
            self.stdout.write(f'  {station.name}: {station.location}') 