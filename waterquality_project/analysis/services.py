from django.db.models import Avg, Count, Max, Min, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.gis.geos import Point
import json
import numpy as np
from scipy import stats
from .models import StationStatistics, SystemOverview, TrendAnalysis, ComparativeAnalysis
from watergis.models import WaterQualityStation, WaterSample, Alert


class AnalyticsService:
    """Service class for calculating analytics and statistics"""
    
    @staticmethod
    def calculate_station_statistics(station_id=None):
        """Calculate statistics for a specific station or all stations"""
        if station_id:
            stations = WaterQualityStation.objects.filter(id=station_id)
        else:
            stations = WaterQualityStation.objects.all()
        
        for station in stations:
            # Get samples for this station
            samples = station.samples.all()
            
            if not samples.exists():
                continue
            
            # Calculate time-based counts
            now = timezone.now()
            thirty_days_ago = now - timedelta(days=30)
            ninety_days_ago = now - timedelta(days=90)
            
            total_samples = samples.count()
            samples_30_days = samples.filter(timestamp__gte=thirty_days_ago).count()
            samples_90_days = samples.filter(timestamp__gte=ninety_days_ago).count()
            
            # Calculate averages
            avg_ph = samples.aggregate(Avg('ph'))['ph__avg']
            avg_turbidity = samples.aggregate(Avg('turbidity'))['turbidity__avg']
            avg_dissolved_oxygen = samples.aggregate(Avg('dissolved_oxygen'))['dissolved_oxygen__avg']
            avg_temperature = samples.aggregate(Avg('temperature'))['temperature__avg']
            
            # Calculate quality score (0-100)
            quality_score = AnalyticsService._calculate_quality_score(
                avg_ph, avg_turbidity, avg_dissolved_oxygen, avg_temperature
            )
            
            # Determine trends
            ph_trend = AnalyticsService._calculate_trend(samples, 'ph')
            turbidity_trend = AnalyticsService._calculate_trend(samples, 'turbidity')
            oxygen_trend = AnalyticsService._calculate_trend(samples, 'dissolved_oxygen')
            
            # Get last sample date
            last_sample = samples.order_by('-timestamp').first()
            last_sample_date = last_sample.timestamp if last_sample else None
            
            # Update or create statistics
            stats, created = StationStatistics.objects.get_or_create(
                station=station,
                defaults={
                    'total_samples': total_samples,
                    'samples_last_30_days': samples_30_days,
                    'samples_last_90_days': samples_90_days,
                    'avg_ph': avg_ph,
                    'avg_turbidity': avg_turbidity,
                    'avg_dissolved_oxygen': avg_dissolved_oxygen,
                    'avg_temperature': avg_temperature,
                    'quality_score': quality_score,
                    'last_sample_date': last_sample_date,
                    'ph_trend': ph_trend,
                    'turbidity_trend': turbidity_trend,
                    'oxygen_trend': oxygen_trend,
                }
            )
            
            if not created:
                # Update existing statistics
                stats.total_samples = total_samples
                stats.samples_last_30_days = samples_30_days
                stats.samples_last_90_days = samples_90_days
                stats.avg_ph = avg_ph
                stats.avg_turbidity = avg_turbidity
                stats.avg_dissolved_oxygen = avg_dissolved_oxygen
                stats.avg_temperature = avg_temperature
                stats.quality_score = quality_score
                stats.last_sample_date = last_sample_date
                stats.ph_trend = ph_trend
                stats.turbidity_trend = turbidity_trend
                stats.oxygen_trend = oxygen_trend
                stats.save()
    
    @staticmethod
    def calculate_system_overview():
        """Calculate system-wide overview statistics"""
        today = timezone.now().date()
        
        # Overall statistics
        total_stations = WaterQualityStation.objects.count()
        active_stations = WaterQualityStation.objects.filter(status='active').count()
        total_samples = WaterSample.objects.count()
        samples_today = WaterSample.objects.filter(
            timestamp__date=today
        ).count()
        
        # Quality metrics
        avg_quality_score = StationStatistics.objects.aggregate(
            Avg('quality_score')
        )['quality_score__avg'] or 0.0
        
        stations_with_issues = StationStatistics.objects.filter(
            quality_score__lt=70
        ).count()
        
        critical_alerts = Alert.objects.filter(
            severity='critical',
            resolved=False
        ).count()
        
        # Geographic distribution (using station_type as region for now)
        regions_covered = WaterQualityStation.objects.values('station_type').distinct().count()
        provinces_covered = 1  # Default since we don't have province field
        
        # Data freshness
        stations_updated_today = WaterQualityStation.objects.filter(
            samples__timestamp__date=today
        ).distinct().count()
        
        # Data completeness (stations with recent data)
        recent_cutoff = timezone.now() - timedelta(days=7)
        stations_with_recent_data = WaterQualityStation.objects.filter(
            samples__timestamp__gte=recent_cutoff
        ).distinct().count()
        
        data_completeness = (stations_with_recent_data / total_stations * 100) if total_stations > 0 else 0
        
        # Create or update system overview
        overview, created = SystemOverview.objects.get_or_create(
            date=today,
            defaults={
                'total_stations': total_stations,
                'active_stations': active_stations,
                'total_samples': total_samples,
                'samples_today': samples_today,
                'avg_quality_score': avg_quality_score,
                'stations_with_issues': stations_with_issues,
                'critical_alerts': critical_alerts,
                'regions_covered': regions_covered,
                'provinces_covered': provinces_covered,
                'stations_updated_today': stations_updated_today,
                'data_completeness': data_completeness,
            }
        )
        
        if not created:
            # Update existing overview
            overview.total_stations = total_stations
            overview.active_stations = active_stations
            overview.total_samples = total_samples
            overview.samples_today = samples_today
            overview.avg_quality_score = avg_quality_score
            overview.stations_with_issues = stations_with_issues
            overview.critical_alerts = critical_alerts
            overview.regions_covered = regions_covered
            overview.provinces_covered = provinces_covered
            overview.stations_updated_today = stations_updated_today
            overview.data_completeness = data_completeness
            overview.save()
    
    @staticmethod
    def analyze_trends(station_id, parameter, period='monthly'):
        """Analyze trends for a specific station and parameter"""
        station = WaterQualityStation.objects.get(id=station_id)
        samples = station.samples.all().order_by('timestamp')
        
        if not samples.exists():
            return None
        
        # Prepare time series data
        if period == 'daily':
            # Group by day
            data = samples.values('timestamp__date').annotate(
                avg_value=Avg(parameter)
            ).order_by('timestamp__date')
        elif period == 'weekly':
            # Group by week
            data = samples.extra(
                select={'week': "EXTRACT(week FROM timestamp)"}
            ).values('week').annotate(
                avg_value=Avg(parameter)
            ).order_by('week')
        else:  # monthly
            # Group by month
            data = samples.values('timestamp__year', 'timestamp__month').annotate(
                avg_value=Avg(parameter)
            ).order_by('timestamp__year', 'timestamp__month')
        
        # Convert to lists for analysis
        values = [item['avg_value'] for item in data if item['avg_value'] is not None]
        time_points = list(range(len(values)))
        
        if len(values) < 2:
            return None
        
        # Calculate trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(time_points, values)
        
        # Determine trend direction
        if abs(slope) < 0.01:
            trend_direction = 'stable'
        elif slope > 0:
            trend_direction = 'increasing'
        else:
            trend_direction = 'decreasing'
        
        # Prepare trend data for storage
        trend_data = {
            'time_points': time_points,
            'values': values,
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value ** 2,
            'p_value': p_value
        }
        
        # Simple forecasting (linear extrapolation)
        forecast_points = 3  # Next 3 periods
        forecast_values = []
        for i in range(1, forecast_points + 1):
            forecast_value = slope * (len(values) + i) + intercept
            forecast_values.append(max(0, forecast_value))  # Ensure non-negative
        
        forecast_data = {
            'forecast_periods': list(range(len(values) + 1, len(values) + forecast_points + 1)),
            'forecast_values': forecast_values
        }
        
        # Create or update trend analysis
        trend_analysis, created = TrendAnalysis.objects.get_or_create(
            station=station,
            parameter=parameter,
            period=period,
            defaults={
                'trend_data': trend_data,
                'trend_direction': trend_direction,
                'trend_strength': abs(r_value),
                'forecast_data': forecast_data,
                'data_points': len(values)
            }
        )
        
        if not created:
            trend_analysis.trend_data = trend_data
            trend_analysis.trend_direction = trend_direction
            trend_analysis.trend_strength = abs(r_value)
            trend_analysis.forecast_data = forecast_data
            trend_analysis.data_points = len(values)
            trend_analysis.save()
        
        return trend_analysis
    
    @staticmethod
    def compare_stations(station_ids, parameters=None):
        """Compare multiple stations"""
        if parameters is None:
            parameters = ['ph', 'turbidity', 'dissolved_oxygen', 'temperature']
        
        stations = WaterQualityStation.objects.filter(id__in=station_ids)
        comparison_data = {
            'stations': [],
            'parameters': {},
            'summary': {}
        }
        
        for station in stations:
            station_data = {
                'id': station.id,
                'name': station.name,
                'station_type': station.station_type,
                'status': station.status,
                'location': {
                    'lat': station.location.y,
                    'lng': station.location.x
                }
            }
            
            # Get station statistics
            try:
                stats = station.statistics
                station_data['statistics'] = {
                    'total_samples': stats.total_samples,
                    'quality_score': stats.quality_score,
                    'avg_ph': stats.avg_ph,
                    'avg_turbidity': stats.avg_turbidity,
                    'avg_dissolved_oxygen': stats.avg_dissolved_oxygen,
                    'avg_temperature': stats.avg_temperature,
                }
            except StationStatistics.DoesNotExist:
                station_data['statistics'] = None
            
            comparison_data['stations'].append(station_data)
        
        # Parameter comparisons
        for param in parameters:
            param_data = []
            for station in stations:
                samples = station.samples.all()
                if samples.exists():
                    avg_value = samples.aggregate(Avg(param))[f'{param}__avg']
                    param_data.append({
                        'station_id': station.id,
                        'station_name': station.name,
                        'average': avg_value,
                        'min': samples.aggregate(Min(param))[f'{param}__min'],
                        'max': samples.aggregate(Max(param))[f'{param}__max'],
                        'count': samples.count()
                    })
            
            comparison_data['parameters'][param] = param_data
        
        # Summary statistics
        comparison_data['summary'] = {
            'total_stations': len(stations),
            'total_samples': sum(s['statistics']['total_samples'] for s in comparison_data['stations'] if s['statistics']),
            'avg_quality_score': np.mean([s['statistics']['quality_score'] for s in comparison_data['stations'] if s['statistics']]) if any(s['statistics'] for s in comparison_data['stations']) else 0
        }
        
        # Store comparison
        comparison = ComparativeAnalysis.objects.create(
            analysis_type='station_comparison',
            comparison_data=comparison_data,
            description=f"Comparison of {len(stations)} stations"
        )
        
        return comparison
    
    @staticmethod
    def _calculate_quality_score(ph, turbidity, dissolved_oxygen, temperature):
        """Calculate a quality score (0-100) based on parameter values"""
        score = 100
        
        # pH scoring (ideal range: 6.5-8.5)
        if ph is not None:
            if 6.5 <= ph <= 8.5:
                score -= 0
            elif 6.0 <= ph <= 9.0:
                score -= 10
            elif 5.5 <= ph <= 9.5:
                score -= 20
            else:
                score -= 30
        
        # Turbidity scoring (lower is better, ideal < 5 NTU)
        if turbidity is not None:
            if turbidity <= 5:
                score -= 0
            elif turbidity <= 10:
                score -= 10
            elif turbidity <= 20:
                score -= 20
            else:
                score -= 30
        
        # Dissolved oxygen scoring (higher is better, ideal > 6 mg/L)
        if dissolved_oxygen is not None:
            if dissolved_oxygen >= 6:
                score -= 0
            elif dissolved_oxygen >= 4:
                score -= 10
            elif dissolved_oxygen >= 2:
                score -= 20
            else:
                score -= 30
        
        # Temperature scoring (ideal range: 10-25°C)
        if temperature is not None:
            if 10 <= temperature <= 25:
                score -= 0
            elif 5 <= temperature <= 30:
                score -= 5
            else:
                score -= 15
        
        return max(0, score)
    
    @staticmethod
    def _calculate_trend(samples, parameter):
        """Calculate trend direction for a parameter"""
        if samples.count() < 2:
            return 'stable'
        
        # Get recent vs older samples
        recent_samples = samples.order_by('-timestamp')[:10]
        older_samples = samples.order_by('-timestamp')[10:20]
        
        if not older_samples.exists():
            return 'stable'
        
        recent_avg = recent_samples.aggregate(Avg(parameter))[f'{parameter}__avg']
        older_avg = older_samples.aggregate(Avg(parameter))[f'{parameter}__avg']
        
        if recent_avg is None or older_avg is None:
            return 'stable'
        
        # Calculate percentage change
        change_percent = ((recent_avg - older_avg) / older_avg) * 100
        
        if abs(change_percent) < 5:
            return 'stable'
        elif change_percent > 0:
            return 'increasing'
        else:
            return 'decreasing' 