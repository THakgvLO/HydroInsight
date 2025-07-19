from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Avg, Count, Q, Min, Max
from django.utils import timezone
from datetime import timedelta
import json

from .models import StationStatistics, SystemOverview, TrendAnalysis, ComparativeAnalysis
from .services import AnalyticsService
from watergis.models import WaterQualityStation, WaterSample, Alert
from .serializers import (
    StationStatisticsSerializer, 
    SystemOverviewSerializer, 
    TrendAnalysisSerializer,
    ComparativeAnalysisSerializer
)


class AnalyticsDashboardView(APIView):
    """Main analytics dashboard view"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get comprehensive analytics data for dashboard"""
        try:
            # Calculate fresh statistics
            AnalyticsService.calculate_station_statistics()
            AnalyticsService.calculate_system_overview()
            
            # Get system overview
            today = timezone.now().date()
            system_overview = SystemOverview.objects.filter(date=today).first()
            
            # Get top performing stations
            top_stations = StationStatistics.objects.select_related('station').order_by('-quality_score')[:5]
            
            # Get stations with issues
            problematic_stations = StationStatistics.objects.select_related('station').filter(
                quality_score__lt=70
            ).order_by('quality_score')[:5]
            
            # Get recent alerts
            recent_alerts = Alert.objects.select_related('station').order_by('-triggered_at')[:10]
            
            # Get sample trends (all available data, grouped by date)
            daily_samples = WaterSample.objects.extra(
                select={'date': 'DATE(timestamp)'}
            ).values('date').annotate(
                count=Count('id')
            ).order_by('date')[:30]  # Limit to 30 most recent dates
            
            # Get parameter averages
            parameter_averages = WaterSample.objects.aggregate(
                avg_ph=Avg('ph'),
                avg_turbidity=Avg('turbidity'),
                avg_dissolved_oxygen=Avg('dissolved_oxygen'),
                avg_temperature=Avg('temperature')
            )
            
            # Geographic distribution (using sample count ranges for better visualization)
            geographic_stats = []
            
            # Group stations by sample count ranges
            sample_ranges = [
                {'name': 'High Activity (>1000 samples)', 'min': 1000, 'max': None},
                {'name': 'Medium Activity (100-999 samples)', 'min': 100, 'max': 999},
                {'name': 'Low Activity (10-99 samples)', 'min': 10, 'max': 99},
                {'name': 'Inactive (<10 samples)', 'min': 0, 'max': 9}
            ]
            
            for range_info in sample_ranges:
                if range_info['max'] is None:
                    count = WaterQualityStation.objects.filter(
                        number_of_samples__gte=range_info['min']
                    ).count()
                else:
                    count = WaterQualityStation.objects.filter(
                        number_of_samples__gte=range_info['min'],
                        number_of_samples__lte=range_info['max']
                    ).count()
                
                if count > 0:
                    geographic_stats.append({
                        'province': range_info['name'],
                        'station_count': count,
                        'avg_quality': 0  # We'll calculate this if needed
                    })
            
            dashboard_data = {
                'system_overview': SystemOverviewSerializer(system_overview).data if system_overview else None,
                'top_stations': StationStatisticsSerializer(top_stations, many=True).data,
                'problematic_stations': StationStatisticsSerializer(problematic_stations, many=True).data,
                'recent_alerts': [
                    {
                        'id': alert.id,
                        'station_name': alert.station.name,
                        'alert_type': alert.alert_type,
                        'severity': alert.severity,
                        'message': alert.message,
                        'triggered_at': alert.triggered_at,
                        'resolved': alert.resolved
                    } for alert in recent_alerts
                ],
                'daily_samples': list(daily_samples),
                'parameter_averages': parameter_averages,
                'geographic_distribution': list(geographic_stats),
                'last_updated': timezone.now()
            }
            
            return Response(dashboard_data)
            
        except Exception as e:
            return Response(
                {'error': f'Error generating analytics: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StationAnalyticsView(APIView):
    """Station-specific analytics"""
    permission_classes = [AllowAny]
    
    def get(self, request, station_id):
        """Get detailed analytics for a specific station"""
        try:
            station = WaterQualityStation.objects.get(id=station_id)
            
            # Calculate fresh statistics for this station
            AnalyticsService.calculate_station_statistics(station_id)
            
            # Get station statistics
            try:
                stats = station.statistics
                station_stats = StationStatisticsSerializer(stats).data
            except StationStatistics.DoesNotExist:
                station_stats = None
            
            # Get recent samples
            recent_samples = station.samples.all().order_by('-timestamp')[:50]
            
            # Get trend analyses
            trend_analyses = TrendAnalysis.objects.filter(station=station)
            
            # Get parameter history (last 90 days)
            ninety_days_ago = timezone.now() - timedelta(days=90)
            parameter_history = station.samples.filter(
                timestamp__gte=ninety_days_ago
            ).values('timestamp', 'ph', 'turbidity', 'dissolved_oxygen', 'temperature').order_by('timestamp')
            
            # Get alerts for this station
            station_alerts = Alert.objects.filter(station=station).order_by('-triggered_at')
            
            analytics_data = {
                'station': {
                    'id': station.id,
                    'name': station.name,
                    'station_type': station.station_type,
                    'status': station.status,
                    'location': {
                        'lat': station.location.y,
                        'lng': station.location.x
                    }
                },
                'statistics': station_stats,
                'recent_samples': [
                    {
                        'timestamp': sample.timestamp,
                        'ph': sample.ph,
                        'turbidity': sample.turbidity,
                        'dissolved_oxygen': sample.dissolved_oxygen,
                        'temperature': sample.temperature
                    } for sample in recent_samples
                ],
                'trend_analyses': TrendAnalysisSerializer(trend_analyses, many=True).data,
                'parameter_history': list(parameter_history),
                'alerts': [
                    {
                        'id': alert.id,
                        'alert_type': alert.alert_type,
                        'severity': alert.severity,
                        'message': alert.message,
                        'triggered_at': alert.triggered_at,
                        'resolved': alert.resolved
                    } for alert in station_alerts
                ]
            }
            
            return Response(analytics_data)
            
        except WaterQualityStation.DoesNotExist:
            return Response(
                {'error': 'Station not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error generating station analytics: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TrendAnalysisView(APIView):
    """Trend analysis endpoints"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Generate trend analysis for a station and parameter"""
        try:
            station_id = request.data.get('station_id')
            parameter = request.data.get('parameter', 'ph')
            period = request.data.get('period', 'monthly')
            
            if not station_id:
                return Response(
                    {'error': 'station_id is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate trend analysis
            trend_analysis = AnalyticsService.analyze_trends(station_id, parameter, period)
            
            if trend_analysis:
                return Response(TrendAnalysisSerializer(trend_analysis).data)
            else:
                return Response(
                    {'error': 'Insufficient data for trend analysis'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Error generating trend analysis: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ComparativeAnalysisView(APIView):
    """Comparative analysis endpoints"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Generate comparative analysis between stations"""
        try:
            station_ids = request.data.get('station_ids', [])
            parameters = request.data.get('parameters', ['ph', 'turbidity', 'dissolved_oxygen', 'temperature'])
            
            if not station_ids or len(station_ids) < 2:
                return Response(
                    {'error': 'At least 2 station_ids are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate comparison
            comparison = AnalyticsService.compare_stations(station_ids, parameters)
            
            return Response(ComparativeAnalysisSerializer(comparison).data)
            
        except Exception as e:
            return Response(
                {'error': f'Error generating comparative analysis: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReportGenerationView(APIView):
    """Report generation endpoints"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Generate various types of reports"""
        try:
            report_type = request.data.get('report_type', 'system_overview')
            filters = request.data.get('filters', {})
            
            if report_type == 'system_overview':
                report_data = self._generate_system_overview_report()
            elif report_type == 'station_comparison':
                station_ids = filters.get('station_ids', [])
                report_data = self._generate_station_comparison_report(station_ids)
            elif report_type == 'quality_assessment':
                report_data = self._generate_quality_assessment_report(filters)
            else:
                return Response(
                    {'error': 'Invalid report type'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(report_data)
            
        except Exception as e:
            return Response(
                {'error': f'Error generating report: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_system_overview_report(self):
        """Generate system overview report"""
        # Calculate fresh statistics
        AnalyticsService.calculate_station_statistics()
        AnalyticsService.calculate_system_overview()
        
        today = timezone.now().date()
        system_overview = SystemOverview.objects.filter(date=today).first()
        
        # Get quality distribution
        quality_distribution = StationStatistics.objects.values('quality_score').annotate(
            count=Count('id')
        ).order_by('quality_score')
        
        # Get parameter statistics
        parameter_stats = WaterSample.objects.aggregate(
            ph_avg=Avg('ph'),
            ph_min=Min('ph'),
            ph_max=Max('ph'),
            turbidity_avg=Avg('turbidity'),
            turbidity_min=Min('turbidity'),
            turbidity_max=Max('turbidity'),
            dissolved_oxygen_avg=Avg('dissolved_oxygen'),
            dissolved_oxygen_min=Min('dissolved_oxygen'),
            dissolved_oxygen_max=Max('dissolved_oxygen'),
            temperature_avg=Avg('temperature'),
            temperature_min=Min('temperature'),
            temperature_max=Max('temperature')
        )
        
        return {
            'report_type': 'system_overview',
            'generated_at': timezone.now(),
            'system_overview': SystemOverviewSerializer(system_overview).data if system_overview else None,
            'quality_distribution': list(quality_distribution),
            'parameter_statistics': parameter_stats,
            'total_stations': WaterQualityStation.objects.count(),
            'total_samples': WaterSample.objects.count(),
            'total_alerts': Alert.objects.count()
        }
    
    def _generate_station_comparison_report(self, station_ids):
        """Generate station comparison report"""
        if not station_ids:
            # Get top 3 stations by sample count for default comparison
            top_stations = WaterQualityStation.objects.order_by('-number_of_samples')[:3]
            station_ids = [station.id for station in top_stations]
        
        if len(station_ids) < 2:
            return {'error': 'At least 2 stations required for comparison'}
        
        comparison_obj = AnalyticsService.compare_stations(station_ids)
        return {
            'report_type': 'station_comparison',
            'generated_at': timezone.now(),
            'comparison_data': comparison_obj.comparison_data,
            'stations_compared': station_ids,
            'summary': comparison_obj.comparison_data.get('summary', {})
        }
    
    def _generate_quality_assessment_report(self, filters):
        """Generate quality assessment report"""
        # Get date range
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        
        query = WaterSample.objects.all()
        if start_date:
            query = query.filter(timestamp__date__gte=start_date)
        if end_date:
            query = query.filter(timestamp__date__lte=end_date)
        
        # Quality assessment by parameter
        quality_assessment = {
            'ph': {
                'excellent': query.filter(ph__range=(6.5, 8.5)).count(),
                'good': query.filter(ph__range=(6.0, 9.0)).exclude(ph__range=(6.5, 8.5)).count(),
                'poor': query.filter(Q(ph__lt=6.0) | Q(ph__gt=9.0)).count()
            },
            'turbidity': {
                'excellent': query.filter(turbidity__lte=5).count(),
                'good': query.filter(turbidity__range=(5, 10)).count(),
                'poor': query.filter(turbidity__gt=10).count()
            },
            'dissolved_oxygen': {
                'excellent': query.filter(dissolved_oxygen__gte=6).count(),
                'good': query.filter(dissolved_oxygen__range=(4, 6)).count(),
                'poor': query.filter(dissolved_oxygen__lt=4).count()
            }
        }
        
        return {
            'report_type': 'quality_assessment',
            'generated_at': timezone.now(),
            'filters': filters,
            'quality_assessment': quality_assessment,
            'total_samples': query.count()
        }
