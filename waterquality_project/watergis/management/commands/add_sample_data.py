import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from watergis.models import WaterQualityStation, WaterSample, Alert
from datetime import timedelta


class Command(BaseCommand):
    help = 'Add sample water quality data for stations'

    def handle(self, *args, **options):
        stations = WaterQualityStation.objects.all()
        
        if not stations.exists():
            self.stdout.write(
                self.style.ERROR('No stations found. Please import stations first.')
            )
            return

        samples_created = 0
        alerts_created = 0

        for station in stations:
            # Create 5-15 samples per station
            num_samples = random.randint(5, 15)
            
            for i in range(num_samples):
                # Generate sample data with realistic ranges
                timestamp = timezone.now() - timedelta(hours=random.randint(1, 168))  # Last week
                
                # Realistic water quality parameters
                ph = round(random.uniform(6.5, 8.5), 2)  # Normal pH range
                turbidity = round(random.uniform(0.5, 15.0), 2)  # NTU
                dissolved_oxygen = round(random.uniform(4.0, 12.0), 2)  # mg/L
                temperature = round(random.uniform(10.0, 30.0), 1)  # Celsius
                
                sample = WaterSample.objects.create(
                    station=station,
                    timestamp=timestamp,
                    ph=ph,
                    turbidity=turbidity,
                    dissolved_oxygen=dissolved_oxygen,
                    temperature=temperature,
                    other_data={
                        "conductivity": round(random.uniform(100, 800), 0),
                        "total_dissolved_solids": round(random.uniform(50, 500), 0),
                        "notes": f"Sample {i+1} for {station.name}"
                    }
                )
                samples_created += 1

                # Create alerts for some samples (about 10% chance)
                if random.random() < 0.1:
                    alert_types = [
                        "High Turbidity",
                        "Low Dissolved Oxygen", 
                        "pH Out of Range",
                        "High Temperature"
                    ]
                    
                    alert_type = random.choice(alert_types)
                    
                    if alert_type == "High Turbidity" and turbidity > 10:
                        message = f"Turbidity level {turbidity} NTU exceeds safe threshold"
                    elif alert_type == "Low Dissolved Oxygen" and dissolved_oxygen < 5:
                        message = f"Dissolved oxygen level {dissolved_oxygen} mg/L is below safe threshold"
                    elif alert_type == "pH Out of Range" and (ph < 6.8 or ph > 8.2):
                        message = f"pH level {ph} is outside normal range"
                    elif alert_type == "High Temperature" and temperature > 25:
                        message = f"Water temperature {temperature}°C is above normal range"
                    else:
                        # Create a general alert
                        message = f"Unusual reading detected: {alert_type}"
                    
                    Alert.objects.create(
                        station=station,
                        sample=sample,
                        alert_type=alert_type,
                        message=message,
                        resolved=random.choice([True, False])
                    )
                    alerts_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Sample data created! Samples: {samples_created}, Alerts: {alerts_created}'
            )
        ) 