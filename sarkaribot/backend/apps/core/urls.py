"""
Core URL patterns for SarkariBot.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    path('status/', views.SystemStatusView.as_view(), name='system_status'),
]
