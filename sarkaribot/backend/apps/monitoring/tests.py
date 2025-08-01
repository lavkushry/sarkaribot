"""
Tests for monitoring app functionality.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
from apps.monitoring.models import ErrorLog, PerformanceMetric, SystemHealth, UserFeedback
from apps.monitoring.tasks import cleanup_old_monitoring_data, system_health_check


class MonitoringModelsTestCase(TestCase):
    """Test monitoring models."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
    
    def test_error_log_creation(self):
        """Test error log creation."""
        error = ErrorLog.objects.create(
            level='error',
            source='django',
            message='Test error message',
            traceback='Test traceback',
            request_path='/test/',
            metadata={'test': 'data'}
        )
        
        self.assertEqual(error.level, 'error')
        self.assertEqual(error.source, 'django')
        self.assertEqual(error.message, 'Test error message')
        self.assertFalse(error.resolved)
        self.assertIsNotNone(error.created_at)
    
    def test_error_log_helper_method(self):
        """Test ErrorLog.log_error helper method."""
        error = ErrorLog.log_error(
            level='warning',
            source='celery',
            message='Test warning',
            metadata={'component': 'test'}
        )
        
        self.assertIsNotNone(error)
        self.assertEqual(error.level, 'warning')
        self.assertEqual(error.source, 'celery')
        self.assertEqual(error.metadata['component'], 'test')
    
    def test_performance_metric_creation(self):
        """Test performance metric creation."""
        metric = PerformanceMetric.objects.create(
            metric_type='response_time',
            value=150.5,
            unit='ms',
            component='api',
            metadata={'endpoint': '/api/jobs/'}
        )
        
        self.assertEqual(metric.metric_type, 'response_time')
        self.assertEqual(metric.value, 150.5)
        self.assertEqual(metric.unit, 'ms')
        self.assertEqual(metric.component, 'api')
    
    def test_system_health_creation(self):
        """Test system health record creation."""
        health = SystemHealth.objects.create(
            component='database',
            status='healthy',
            details={'response_time': 'fast'}
        )
        
        self.assertEqual(health.component, 'database')
        self.assertEqual(health.status, 'healthy')
        self.assertIsNotNone(health.last_check)
    
    def test_user_feedback_creation(self):
        """Test user feedback creation."""
        feedback = UserFeedback.objects.create(
            feedback_type='bug_report',
            message='Found a bug in the search',
            page_url='/search?q=test',
            contact_info='user@example.com'
        )
        
        self.assertEqual(feedback.feedback_type, 'bug_report')
        self.assertEqual(feedback.message, 'Found a bug in the search')
        self.assertFalse(feedback.resolved)


class MonitoringViewsTestCase(TestCase):
    """Test monitoring views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
    
    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        url = reverse('monitoring:health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertIn('service', data)
        self.assertEqual(data['service'], 'sarkaribot-backend')
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        # Create some test metrics
        PerformanceMetric.objects.create(
            metric_type='response_time',
            value=100,
            unit='ms',
            component='test'
        )
        
        url = reverse('monitoring:metrics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('metrics', data)
    
    def test_error_feedback_endpoint(self):
        """Test error feedback submission."""
        url = reverse('monitoring:error_feedback')
        data = {
            'type': 'bug_report',
            'message': 'Test error report',
            'page_url': '/test/',
            'contact_info': 'test@example.com'
        }
        
        response = self.client.post(
            url,
            data=data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('feedback_id', response_data)
        
        # Verify feedback was created
        feedback = UserFeedback.objects.get(id=response_data['feedback_id'])
        self.assertEqual(feedback.message, 'Test error report')
        self.assertEqual(feedback.contact_info, 'test@example.com')


class MonitoringTasksTestCase(TestCase):
    """Test monitoring tasks."""
    
    def setUp(self):
        """Set up test data."""
        # Create old test data
        old_date = timezone.now() - timedelta(days=35)
        
        self.old_error = ErrorLog.objects.create(
            level='error',
            source='django',
            message='Old error',
            created_at=old_date
        )
        
        self.old_metric = PerformanceMetric.objects.create(
            metric_type='response_time',
            value=100,
            unit='ms',
            component='test',
            recorded_at=old_date
        )
        
        # Create recent data
        self.recent_error = ErrorLog.objects.create(
            level='warning',
            source='django',
            message='Recent error'
        )
    
    def test_cleanup_old_monitoring_data(self):
        """Test cleanup task."""
        # Verify old data exists
        self.assertTrue(ErrorLog.objects.filter(id=self.old_error.id).exists())
        self.assertTrue(PerformanceMetric.objects.filter(id=self.old_metric.id).exists())
        self.assertTrue(ErrorLog.objects.filter(id=self.recent_error.id).exists())
        
        # Run cleanup task
        result = cleanup_old_monitoring_data()
        
        # Verify old data was deleted but recent data remains
        self.assertFalse(ErrorLog.objects.filter(id=self.old_error.id).exists())
        self.assertFalse(PerformanceMetric.objects.filter(id=self.old_metric.id).exists())
        self.assertTrue(ErrorLog.objects.filter(id=self.recent_error.id).exists())
        
        # Verify task result
        self.assertIsInstance(result, dict)
        self.assertIn('errors_deleted', result)
        self.assertIn('metrics_deleted', result)
    
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.cpu_percent')
    def test_system_health_check(self, mock_cpu, mock_disk, mock_memory):
        """Test system health check task."""
        # Mock system metrics
        mock_memory.return_value = MagicMock(percent=50, available=8*1024**3)
        mock_disk.return_value = MagicMock(
            total=100*1024**3, 
            free=50*1024**3, 
            used=50*1024**3
        )
        mock_cpu.return_value = 30.0
        
        # Run health check
        result = system_health_check()
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('timestamp', result)
        self.assertIn('checks', result)
        self.assertIn('overall_status', result)
        
        # Verify checks
        checks = result['checks']
        self.assertIn('database', checks)
        self.assertIn('cache', checks)
        self.assertIn('memory', checks)
        self.assertIn('disk', checks)
        self.assertIn('cpu', checks)
        
        # Verify health record was created
        health_record = SystemHealth.objects.get(component='system_health_task')
        self.assertEqual(health_record.status, result['overall_status'])


class MonitoringMiddlewareTestCase(TestCase):
    """Test monitoring middleware."""
    
    def test_request_tracking_middleware(self):
        """Test request tracking middleware."""
        # Make a request that should be tracked
        response = self.client.get('/api/v1/monitoring/health/')
        
        # Verify response headers
        self.assertIn('X-Response-Time', response)
        self.assertIn('X-DB-Queries', response)
    
    def test_security_headers_middleware(self):
        """Test security headers middleware."""
        response = self.client.get('/api/v1/monitoring/health/')
        
        # Verify security headers
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        self.assertEqual(response['Referrer-Policy'], 'strict-origin-when-cross-origin')
    
    def test_health_check_middleware(self):
        """Test health check middleware fast path."""
        response = self.client.get('/health/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('service', data)
        self.assertEqual(data['service'], 'sarkaribot-backend')


class MonitoringIntegrationTestCase(TestCase):
    """Integration tests for monitoring system."""
    
    def test_error_logging_integration(self):
        """Test that errors are properly logged."""
        # Create a request that generates an error
        request = self.client.request()
        request.path = '/test/'
        request.META = {'HTTP_USER_AGENT': 'Test Agent'}
        
        # Log an error using the helper method
        error = ErrorLog.log_error(
            level='error',
            source='django',
            message='Integration test error',
            request=request
        )
        
        self.assertIsNotNone(error)
        self.assertEqual(error.request_path, '/test/')
        self.assertEqual(error.user_agent, 'Test Agent')
    
    def test_performance_tracking_integration(self):
        """Test performance tracking integration."""
        # Create a performance metric
        PerformanceMetric.objects.create(
            metric_type='response_time',
            value=250.0,
            unit='ms',
            component='integration_test',
            metadata={'test': True}
        )
        
        # Verify metric can be retrieved via API
        response = self.client.get(reverse('monitoring:metrics'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('metrics', data)