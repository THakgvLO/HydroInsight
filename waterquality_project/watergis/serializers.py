from rest_framework import serializers
from .models import WaterQualityStation, WaterSample, Alert

class WaterQualityStationSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    
    def get_location(self, obj):
        if obj.location:
            return {
                'coordinates': [obj.location.x, obj.location.y],
                'type': 'Point'
            }
        return None
    
    class Meta:
        model = WaterQualityStation
        fields = ['id', 'name', 'location', 'description', 'station_type', 'status', 
                 'measurement_start_date', 'measurement_end_date', 'number_of_samples', 'created_at']

class WaterSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterSample
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__' 