"""
Admin interface for monitoring app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import SystemHealth, ErrorLog, PerformanceMetric, UserFeedback


@admin.register(SystemHealth)
class SystemHealthAdmin(admin.ModelAdmin):
    list_display = ['component', 'status', 'last_check', 'created_at']
    list_filter = ['status', 'component', 'last_check']
    search_fields = ['component']
    readonly_fields = ['created_at', 'last_check', 'details_display']
    
    def details_display(self, obj):
        """Display details as formatted JSON."""
        import json
        if obj.details:
            formatted = json.dumps(obj.details, indent=2)
            return format_html('<pre>{}</pre>', formatted)
        return '-'
    details_display.short_description = 'Details'


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'source', 'message_short', 'request_path', 'resolved', 'created_at']
    list_filter = ['level', 'source', 'resolved', 'created_at']
    search_fields = ['message', 'request_path', 'ip_address']
    readonly_fields = ['created_at', 'traceback_display', 'metadata_display']
    actions = ['mark_resolved', 'mark_unresolved']
    
    def message_short(self, obj):
        """Display shortened message."""
        return obj.message[:100] + ('...' if len(obj.message) > 100 else '')
    message_short.short_description = 'Message'
    
    def traceback_display(self, obj):
        """Display traceback with proper formatting."""
        if obj.traceback:
            return format_html('<pre>{}</pre>', obj.traceback)
        return '-'
    traceback_display.short_description = 'Traceback'
    
    def metadata_display(self, obj):
        """Display metadata as formatted JSON."""
        import json
        if obj.metadata:
            formatted = json.dumps(obj.metadata, indent=2)
            return format_html('<pre>{}</pre>', formatted)
        return '-'
    metadata_display.short_description = 'Metadata'
    
    def mark_resolved(self, request, queryset):
        """Mark selected errors as resolved."""
        updated = queryset.update(resolved=True)
        self.message_user(request, f'{updated} error(s) marked as resolved.')
    mark_resolved.short_description = 'Mark selected errors as resolved'
    
    def mark_unresolved(self, request, queryset):
        """Mark selected errors as unresolved."""
        updated = queryset.update(resolved=False)
        self.message_user(request, f'{updated} error(s) marked as unresolved.')
    mark_unresolved.short_description = 'Mark selected errors as unresolved'


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'component', 'value', 'unit', 'recorded_at']
    list_filter = ['metric_type', 'component', 'recorded_at']
    search_fields = ['component']
    readonly_fields = ['recorded_at', 'metadata_display']
    
    def metadata_display(self, obj):
        """Display metadata as formatted JSON."""
        import json
        if obj.metadata:
            formatted = json.dumps(obj.metadata, indent=2)
            return format_html('<pre>{}</pre>', formatted)
        return '-'
    metadata_display.short_description = 'Metadata'


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ['feedback_type', 'message_short', 'page_url', 'resolved', 'created_at']
    list_filter = ['feedback_type', 'resolved', 'created_at']
    search_fields = ['message', 'page_url', 'contact_info']
    readonly_fields = ['created_at', 'metadata_display', 'error_log_link']
    actions = ['mark_resolved', 'mark_unresolved']
    
    def message_short(self, obj):
        """Display shortened message."""
        return obj.message[:100] + ('...' if len(obj.message) > 100 else '')
    message_short.short_description = 'Message'
    
    def metadata_display(self, obj):
        """Display metadata as formatted JSON."""
        import json
        if obj.metadata:
            formatted = json.dumps(obj.metadata, indent=2)
            return format_html('<pre>{}</pre>', formatted)
        return '-'
    metadata_display.short_description = 'Metadata'
    
    def error_log_link(self, obj):
        """Display link to related error log."""
        if obj.error_log:
            url = reverse('admin:monitoring_errorlog_change', args=[obj.error_log.pk])
            return format_html('<a href="{}">View Error Log</a>', url)
        return '-'
    error_log_link.short_description = 'Related Error'
    
    def mark_resolved(self, request, queryset):
        """Mark selected feedback as resolved."""
        updated = queryset.update(resolved=True)
        self.message_user(request, f'{updated} feedback(s) marked as resolved.')
    mark_resolved.short_description = 'Mark selected feedback as resolved'
    
    def mark_unresolved(self, request, queryset):
        """Mark selected feedback as unresolved."""
        updated = queryset.update(resolved=False)
        self.message_user(request, f'{updated} feedback(s) marked as unresolved.')
    mark_unresolved.short_description = 'Mark selected feedback as unresolved'