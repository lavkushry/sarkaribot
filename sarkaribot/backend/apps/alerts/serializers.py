"""
Serializers for Job Alert System
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import JobAlert, JobAlertLog, JobBookmark, JobApplication, UserNotificationPreference

User = get_user_model()


class JobAlertSerializer(serializers.ModelSerializer):
    """
    Serializer for JobAlert model.
    """
    user = serializers.StringRelatedField(read_only=True)
    categories = serializers.StringRelatedField(many=True, read_only=True)
    sources = serializers.StringRelatedField(many=True, read_only=True)
    matching_jobs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = JobAlert
        fields = [
            'id', 'user', 'name', 'keywords', 'categories', 'sources',
            'locations', 'qualifications', 'min_salary', 'max_salary',
            'min_age', 'max_age', 'frequency', 'delivery_method',
            'delivery_email', 'delivery_phone', 'webhook_url',
            'is_active', 'last_sent', 'matching_jobs_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'last_sent', 'created_at', 'updated_at']
    
    def get_matching_jobs_count(self, obj):
        """Get count of currently matching jobs."""
        try:
            return obj.get_matching_jobs().count()
        except:
            return 0


class JobAlertCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating JobAlert.
    """
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    source_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = JobAlert
        fields = [
            'name', 'keywords', 'category_ids', 'source_ids',
            'locations', 'qualifications', 'min_salary', 'max_salary',
            'min_age', 'max_age', 'frequency', 'delivery_method',
            'delivery_email', 'delivery_phone', 'webhook_url', 'is_active'
        ]
    
    def validate_name(self, value):
        """Validate alert name."""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Alert name must be at least 3 characters long.")
        return value.strip()
    
    def validate_delivery_email(self, value):
        """Validate email if email delivery is chosen."""
        delivery_method = self.initial_data.get('delivery_method')
        if delivery_method == 'email' and not value:
            raise serializers.ValidationError("Email is required for email delivery.")
        return value
    
    def validate_delivery_phone(self, value):
        """Validate phone if SMS delivery is chosen."""
        delivery_method = self.initial_data.get('delivery_method')
        if delivery_method == 'sms' and not value:
            raise serializers.ValidationError("Phone number is required for SMS delivery.")
        return value
    
    def validate_webhook_url(self, value):
        """Validate webhook URL if webhook delivery is chosen."""
        delivery_method = self.initial_data.get('delivery_method')
        if delivery_method == 'webhook' and not value:
            raise serializers.ValidationError("Webhook URL is required for webhook delivery.")
        return value


class JobAlertUpdateSerializer(JobAlertCreateSerializer):
    """
    Serializer for updating JobAlert.
    """
    name = serializers.CharField(required=False)
    
    class Meta(JobAlertCreateSerializer.Meta):
        pass


class JobAlertLogSerializer(serializers.ModelSerializer):
    """
    Serializer for JobAlertLog model.
    """
    alert_name = serializers.CharField(source='alert.name', read_only=True)
    
    class Meta:
        model = JobAlertLog
        fields = [
            'id', 'alert', 'alert_name', 'jobs_count', 'delivery_method',
            'status', 'error_message', 'sent_at'
        ]
        read_only_fields = ['id', 'sent_at']


class JobBookmarkSerializer(serializers.ModelSerializer):
    """
    Serializer for JobBookmark model.
    """
    user = serializers.StringRelatedField(read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_status = serializers.CharField(source='job.status', read_only=True)
    job_source = serializers.CharField(source='job.source.name', read_only=True)
    job_category = serializers.CharField(source='job.category.name', read_only=True)
    
    class Meta:
        model = JobBookmark
        fields = [
            'id', 'user', 'job', 'job_title', 'job_status', 'job_source',
            'job_category', 'notes', 'reminder_date', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for JobApplication model.
    """
    user = serializers.StringRelatedField(read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_source = serializers.CharField(source='job.source.name', read_only=True)
    job_category = serializers.CharField(source='job.category.name', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'user', 'job', 'job_title', 'job_source', 'job_category',
            'status', 'application_date', 'notes', 'application_id',
            'documents_submitted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for UserNotificationPreference model.
    """
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = UserNotificationPreference
        fields = [
            'user', 'email_job_alerts', 'email_system_updates',
            'email_newsletter', 'email_promotional', 'email_security',
            'sms_job_alerts', 'sms_system_updates', 'sms_security',
            'push_job_alerts', 'push_system_updates', 'push_security',
            'quiet_hours_start', 'quiet_hours_end', 'timezone',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class JobAlertPreviewSerializer(serializers.Serializer):
    """
    Serializer for alert preview/testing.
    """
    keywords = serializers.CharField(required=False, allow_blank=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    source_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    locations = serializers.CharField(required=False, allow_blank=True)
    qualifications = serializers.CharField(required=False, allow_blank=True)
    min_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    min_age = serializers.IntegerField(required=False)
    max_age = serializers.IntegerField(required=False)
