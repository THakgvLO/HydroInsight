from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WaterQualityStationViewSet, WaterSampleViewSet, AlertViewSet, StationSamplesView, APIRootView

router = DefaultRouter()
router.register(r'stations', WaterQualityStationViewSet, basename='station')
router.register(r'samples', WaterSampleViewSet, basename='sample')
router.register(r'alerts', AlertViewSet, basename='alert')

urlpatterns = router.urls + [
    path('', APIRootView.as_view(), name='api-root'),
    path('stations/<int:station_id>/samples/', StationSamplesView.as_view(), name='station-samples'),
    path('analytics/', include('analysis.urls')),
] 