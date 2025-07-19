from django.urls import path
from .views import (
    AnalyticsDashboardView,
    StationAnalyticsView,
    TrendAnalysisView,
    ComparativeAnalysisView,
    ReportGenerationView
)

urlpatterns = [
    path('dashboard/', AnalyticsDashboardView.as_view(), name='analytics-dashboard'),
    path('stations/<int:station_id>/', StationAnalyticsView.as_view(), name='station-analytics'),
    path('trends/', TrendAnalysisView.as_view(), name='trend-analysis'),
    path('comparison/', ComparativeAnalysisView.as_view(), name='comparative-analysis'),
    path('reports/', ReportGenerationView.as_view(), name='report-generation'),
] 