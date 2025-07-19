from rest_framework import serializers
from .models import StationStatistics, SystemOverview, TrendAnalysis, ComparativeAnalysis
from watergis.serializers import WaterQualityStationSerializer


class StationStatisticsSerializer(serializers.ModelSerializer):
    station = WaterQualityStationSerializer(read_only=True)
    
    class Meta:
        model = StationStatistics
        fields = '__all__'


class SystemOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemOverview
        fields = '__all__'


class TrendAnalysisSerializer(serializers.ModelSerializer):
    station = WaterQualityStationSerializer(read_only=True)
    
    class Meta:
        model = TrendAnalysis
        fields = '__all__'


class ComparativeAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComparativeAnalysis
        fields = '__all__' 