from django.core.management.base import BaseCommand
from analysis.services import AnalyticsService
from watergis.models import WaterQualityStation


class Command(BaseCommand):
    help = 'Calculate analytics and statistics for all stations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--station-id',
            type=int,
            help='Calculate analytics for a specific station only'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recalculation of all analytics'
        )

    def handle(self, *args, **options):
        station_id = options.get('station_id')
        force = options.get('force')

        self.stdout.write(
            self.style.SUCCESS('Starting analytics calculation...')
        )

        try:
            if station_id:
                # Calculate for specific station
                self.stdout.write(f'Calculating analytics for station {station_id}...')
                AnalyticsService.calculate_station_statistics(station_id)
                self.stdout.write(
                    self.style.SUCCESS(f'Analytics calculated for station {station_id}')
                )
            else:
                # Calculate for all stations
                total_stations = WaterQualityStation.objects.count()
                self.stdout.write(f'Calculating analytics for {total_stations} stations...')
                
                AnalyticsService.calculate_station_statistics()
                self.stdout.write(
                    self.style.SUCCESS('Station statistics calculated')
                )

            # Calculate system overview
            self.stdout.write('Calculating system overview...')
            AnalyticsService.calculate_system_overview()
            self.stdout.write(
                self.style.SUCCESS('System overview calculated')
            )

            self.stdout.write(
                self.style.SUCCESS('Analytics calculation completed successfully!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error calculating analytics: {str(e)}')
            ) 