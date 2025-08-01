"""
URL patterns for monitoring app.
"""
from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    # Health check endpoints
    path('health/', views.health_check, name='health_check'),
    path('metrics/', views.metrics, name='metrics'),
    
    # Admin dashboard endpoints
    path('status/', views.system_status, name='system_status'),
    
    # User feedback endpoint
    path('feedback/', views.error_feedback, name='error_feedback'),
]