"""
URL configuration for SarkariBot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
# from rest_framework.documentation import include_docs_urls

# Import sitemaps (will be created later)
# from apps.jobs.sitemaps import JobPostingSitemap, JobCategorySitemap

# Sitemap configuration (will be activated later)
# sitemaps = {
#     'jobs': JobPostingSitemap,
#     'categories': JobCategorySitemap,
# }

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation (commented out temporarily)
    # path('api/docs/', include_docs_urls(title='SarkariBot API', description='Complete API for SarkariBot')),
    
    # API Routes - Main job functionality
    path('', include('apps.jobs.urls')),
    
    # Additional API modules
    path('api/v1/sources/', include('apps.sources.urls')),
    path('api/v1/scraping/', include('apps.scraping.urls')),
    path('api/v1/seo/', include('apps.seo.urls')),
    path('api/v1/core/', include('apps.core.urls')),
    
    # Stage 4 Advanced Features (temporarily commented until properly configured)
    # path('api/v1/analytics/', include('apps.analytics.urls')),
    # path('api/v1/ai-search/', include('apps.ai_search.urls')),
    # path('api/v1/monitoring/', include('apps.monitoring.urls')),
    # path('api/v1/alerts/', include('apps.alerts.urls')),
    
    # Django REST Framework browsable API
    path('api-auth/', include('rest_framework.urls')),
    
    # Sitemap (will be activated later)
    # path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
    #      name='django.contrib.sitemaps.views.sitemap'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Custom admin configuration
admin.site.site_header = 'SarkariBot Administration'
admin.site.site_title = 'SarkariBot Admin'
admin.site.index_title = 'Welcome to SarkariBot Administration'
