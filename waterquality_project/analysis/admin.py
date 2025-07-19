from django.contrib import admin
from waterquality.admin_config import admin_site
from .models import StationStatistics, SystemOverview, TrendAnalysis, ComparativeAnalysis


@admin.register(StationStatistics, site=admin_site)
class StationStatisticsAdmin(admin.ModelAdmin):
    list_display = ['station', 'quality_score', 'total_samples', 'last_sample_date']
    list_filter = ['quality_score', 'last_sample_date']
    search_fields = ['station__name']
    readonly_fields = ['last_calculated']


@admin.register(SystemOverview, site=admin_site)
class SystemOverviewAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_stations', 'active_stations', 'total_samples', 'avg_quality_score']
    list_filter = ['date']
    readonly_fields = ['date']


@admin.register(TrendAnalysis, site=admin_site)
class TrendAnalysisAdmin(admin.ModelAdmin):
    list_display = ['station', 'parameter', 'trend_direction', 'trend_strength', 'period']
    list_filter = ['parameter', 'trend_direction', 'period']
    search_fields = ['station__name']
    readonly_fields = ['analysis_date']


@admin.register(ComparativeAnalysis, site=admin_site)
class ComparativeAnalysisAdmin(admin.ModelAdmin):
    list_display = ['analysis_type', 'created_at']
    list_filter = ['analysis_type', 'created_at']
    readonly_fields = ['created_at']
