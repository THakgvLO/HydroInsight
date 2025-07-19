from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from watergis.models import WaterQualityStation, WaterSample, Alert
from watergis.serializers import WaterQualityStationSerializer, WaterSampleSerializer, AlertSerializer

# Create your views here.

class WaterQualityStationViewSet(viewsets.ModelViewSet):
    queryset = WaterQualityStation.objects.all()[:100]  # Limit to first 100 stations for performance
    serializer_class = WaterQualityStationSerializer

class StationSamplesView(APIView):
    def get(self, request, station_id):
        """Get samples for a specific station"""
        try:
            station = WaterQualityStation.objects.get(id=station_id)
            samples = station.samples.all().order_by('-timestamp')[:1000]  # Limit to 1000 most recent
            serializer = WaterSampleSerializer(samples, many=True)
            return Response(serializer.data)
        except WaterQualityStation.DoesNotExist:
            return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)

class WaterSampleViewSet(viewsets.ModelViewSet):
    queryset = WaterSample.objects.all()
    serializer_class = WaterSampleSerializer

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

class APIRootView(APIView):
    def get(self, request):
        """API Root with HydroNexus Africa branding"""
        return Response({
            'name': 'HydroNexus Africa Water Quality API',
            'version': '1.0.0',
            'description': 'Comprehensive water quality monitoring API for Africa',
            'developer': 'Thakgalo Sehlola',
            'endpoints': {
                'stations': reverse('station-list', request=request),
                'samples': reverse('sample-list', request=request),
                'alerts': reverse('alert-list', request=request),
            },
            'documentation': 'Visit /admin/ for detailed data management'
        })
