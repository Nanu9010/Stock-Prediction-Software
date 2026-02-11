from django.contrib import admin
from .models import ResearchCall, ResearchCallEvent, ResearchCallVersion

@admin.register(ResearchCall)
class ResearchCallAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'call_type', 'action', 'status', 'entry_price', 'target_1', 'stop_loss', 'created_by', 'created_at')
    list_filter = ('status', 'call_type', 'action', 'instrument_type', 'broker')
    search_fields = ('symbol', 'company_name', 'rationale')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'published_at', 'closed_at', 'created_by')
    fieldsets = (
        ('Basic Info', {
            'fields': ('symbol', 'company_name', 'sector', 'instrument_type', 'broker')
        }),
        ('Call Details', {
            'fields': ('call_type', 'action', 'status')
        }),
        ('Price Levels', {
            'fields': ('entry_price', 'target_1', 'target_2', 'target_3', 'stop_loss')
        }),
        ('Analysis', {
            'fields': ('rationale', 'timeframe_days', 'expected_return_percentage', 'risk_reward_ratio')
        }),
        ('Lifecycle', {
            'fields': ('created_by', 'approved_by', 'published_at', 'expires_at', 'closed_at')
        }),
        ('Outcome', {
            'fields': ('is_successful', 'actual_return_percentage', 'exit_price', 'exit_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ResearchCallEvent)
class ResearchCallEventAdmin(admin.ModelAdmin):
    list_display = ('research_call', 'event_type', 'created_at', 'triggered_by')
    list_filter = ('event_type', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(ResearchCallVersion)
class ResearchCallVersionAdmin(admin.ModelAdmin):
    list_display = ('research_call', 'version_number', 'changed_by', 'created_at')
    readonly_fields = ('created_at',)
