from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from waterquality.admin_config import admin_site
from .models import WaterQualityStation, WaterSample, Alert


# Register Django built-in models with custom admin site
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)


@admin.register(WaterQualityStation, site=admin_site)
class WaterQualityStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'station_type', 'status', 'number_of_samples', 'created_at']
    list_filter = ['station_type', 'status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(WaterSample, site=admin_site)
class WaterSampleAdmin(admin.ModelAdmin):
    list_display = ['station', 'timestamp', 'ph', 'turbidity', 'dissolved_oxygen', 'temperature', 'get_station_type']
    list_filter = [
        'station__station_type',
        'station__status', 
        ('timestamp', admin.DateFieldListFilter),
    ]
    search_fields = ['station__name', 'station__station_type']
    readonly_fields = ['created_by']
    date_hierarchy = 'timestamp'
    list_per_page = 50
    
    def get_station_type(self, obj):
        return obj.station.station_type if obj.station else '-'
    get_station_type.short_description = 'Station Type'
    get_station_type.admin_order_field = 'station__station_type'


@admin.register(Alert, site=admin_site)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['station', 'alert_type', 'triggered_at', 'resolved']
    list_filter = ['alert_type', 'resolved', 'triggered_at']
    search_fields = ['station__name', 'message']
    readonly_fields = ['triggered_at']
