from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from watergis.models import WaterQualityStation, WaterSample, Alert
from analysis.models import StationStatistics, SystemOverview, TrendAnalysis, ComparativeAnalysis


class Command(BaseCommand):
    help = 'Set up permissions for different user groups'

    def handle(self, *args, **options):
        self.stdout.write('Setting up user permissions...')
        
        # Get content types
        station_ct = ContentType.objects.get_for_model(WaterQualityStation)
        sample_ct = ContentType.objects.get_for_model(WaterSample)
        alert_ct = ContentType.objects.get_for_model(Alert)
        stats_ct = ContentType.objects.get_for_model(StationStatistics)
        overview_ct = ContentType.objects.get_for_model(SystemOverview)
        trend_ct = ContentType.objects.get_for_model(TrendAnalysis)
        comparison_ct = ContentType.objects.get_for_model(ComparativeAnalysis)
        
        # Get groups
        managers = Group.objects.get(name='Managers')
        analysts = Group.objects.get(name='Analysts')
        operators = Group.objects.get(name='Operators')
        viewers = Group.objects.get(name='Viewers')
        
        # Clear existing permissions
        managers.permissions.clear()
        analysts.permissions.clear()
        operators.permissions.clear()
        viewers.permissions.clear()
        
        # Managers: Full access to everything
        manager_permissions = Permission.objects.filter(
            content_type__in=[station_ct, sample_ct, alert_ct, stats_ct, overview_ct, trend_ct, comparison_ct]
        )
        managers.permissions.set(manager_permissions)
        
        # Analysts: Read access to all data, write access to analytics
        analyst_permissions = Permission.objects.filter(
            content_type__in=[station_ct, sample_ct, alert_ct, stats_ct, overview_ct, trend_ct, comparison_ct],
            codename__startswith='view'
        )
        analyst_permissions |= Permission.objects.filter(
            content_type__in=[stats_ct, overview_ct, trend_ct, comparison_ct],
            codename__startswith='add'
        )
        analyst_permissions |= Permission.objects.filter(
            content_type__in=[stats_ct, overview_ct, trend_ct, comparison_ct],
            codename__startswith='change'
        )
        analysts.permissions.set(analyst_permissions)
        
        # Operators: Read access to stations and samples, write access to samples
        operator_permissions = Permission.objects.filter(
            content_type__in=[station_ct, sample_ct, alert_ct],
            codename__startswith='view'
        )
        operator_permissions |= Permission.objects.filter(
            content_type__in=[sample_ct, alert_ct],
            codename__startswith='add'
        )
        operator_permissions |= Permission.objects.filter(
            content_type__in=[sample_ct, alert_ct],
            codename__startswith='change'
        )
        operators.permissions.set(operator_permissions)
        
        # Viewers: Read-only access to stations and samples
        viewer_permissions = Permission.objects.filter(
            content_type__in=[station_ct, sample_ct],
            codename__startswith='view'
        )
        viewers.permissions.set(viewer_permissions)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up permissions for all user groups')
        )
        
        # Print summary
        self.stdout.write('\nPermission Summary:')
        self.stdout.write(f'Managers: {managers.permissions.count()} permissions')
        self.stdout.write(f'Analysts: {analysts.permissions.count()} permissions')
        self.stdout.write(f'Operators: {operators.permissions.count()} permissions')
        self.stdout.write(f'Viewers: {viewers.permissions.count()} permissions') 