from django.contrib import admin
from .models import Broker, BrokerPerformanceMetrics


@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ('name', 'overall_accuracy', 'total_calls_published', 'total_calls_closed', 'is_active', 'is_verified')
    list_filter = ('is_active', 'is_verified', 'created_at')
    search_fields = ('name', 'sebi_registration_no')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'overall_accuracy', 'total_calls_published', 'total_calls_closed')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'logo')
        }),
        ('Contact & Legal', {
            'fields': ('website_url', 'sebi_registration_no')
        }),
        ('Performance Metrics', {
            'fields': ('overall_accuracy', 'total_calls_published', 'total_calls_closed', 'avg_return_percentage')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(BrokerPerformanceMetrics)
class BrokerPerformanceMetricsAdmin(admin.ModelAdmin):
    list_display = ('broker', 'metric_date', 'accuracy_percentage', 'total_closed_calls', 'successful_calls')
    list_filter = ('metric_date', 'broker')
    search_fields = ('broker__name',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'metric_date'
