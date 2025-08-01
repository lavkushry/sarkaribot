"""
SEO-optimized views for SarkariBot job pages.

This module contains Django template views for server-side rendering
of job detail and category pages with proper SEO metadata following
the Knowledge.md URL architecture: /{category}/{job-slug}/
"""

from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views.generic import DetailView, ListView
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import timedelta
import logging

from .models import JobPosting, JobCategory

logger = logging.getLogger(__name__)


class JobDetailSEOView(DetailView):
    """
    SEO-optimized job detail view.
    
    Renders individual job postings with full SEO metadata
    following the /{category}/{job-slug}/ URL pattern.
    """
    
    model = JobPosting
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'
    slug_field = 'slug'
    slug_url_kwarg = 'job_slug'
    
    def get_queryset(self):
        """Filter by category and active status."""
        return JobPosting.objects.filter(
            status__in=['announced', 'admit_card', 'answer_key', 'result'],
            category__slug=self.kwargs['category_slug']
        ).select_related('source', 'category').prefetch_related('milestones')
    
    def get_object(self, queryset=None):
        """Get job object and increment view count."""
        obj = super().get_object(queryset)
        
        # Increment view count
        try:
            obj.increment_view_count()
        except Exception as e:
            logger.warning(f"Failed to increment view count for job {obj.pk}: {e}")
        
        return obj
    
    def get_context_data(self, **kwargs):
        """Add additional context for SEO and display."""
        context = super().get_context_data(**kwargs)
        job = self.object
        
        # SEO metadata
        context.update({
            'seo_title': job.seo_title or f"{job.title} - Apply Online | SarkariBot",
            'seo_description': job.seo_description or f"Apply for {job.title}. Check eligibility, last date, and direct application link.",
            'keywords': job.keywords,
            'canonical_url': self.request.build_absolute_uri(),
            'structured_data': job.structured_data,
            'open_graph_tags': job.open_graph_tags,
        })
        
        # Breadcrumbs
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': job.category.name, 'url': f"/{job.category.slug}/"},
            {'name': job.title, 'url': ''}
        ]
        
        # Related jobs
        related_jobs = JobPosting.objects.filter(
            category=job.category,
            status__in=['announced', 'admit_card', 'answer_key', 'result']
        ).exclude(pk=job.pk)[:5]
        context['related_jobs'] = related_jobs
        
        # Job milestones
        context['milestones'] = job.milestones.filter(is_active=True).order_by('-milestone_date')[:10]
        
        return context


class CategoryListSEOView(ListView):
    """
    SEO-optimized category listing view.
    
    Renders job listings for a specific category
    following the /{category}/ URL pattern.
    """
    
    model = JobPosting
    template_name = 'jobs/category_list.html'
    context_object_name = 'jobs'
    paginate_by = 20
    
    def get_queryset(self):
        """Filter jobs by category and active status."""
        category_slug = self.kwargs['category_slug']
        
        # Validate category exists
        self.category = get_object_or_404(JobCategory, slug=category_slug, is_active=True)
        
        return JobPosting.objects.filter(
            category=self.category,
            status__in=['announced', 'admit_card', 'answer_key', 'result']
        ).select_related('source', 'category').order_by('-created_at', '-published_at')
    
    def get_context_data(self, **kwargs):
        """Add category and SEO context."""
        context = super().get_context_data(**kwargs)
        
        # SEO metadata
        seo_title = f"{self.category.name} - Government Jobs 2025 | SarkariBot"
        seo_description = f"Latest {self.category.name.lower()} notifications. Check eligibility, apply online, download admit cards and results."
        
        context.update({
            'category': self.category,
            'seo_title': seo_title,
            'seo_description': seo_description,
            'canonical_url': self.request.build_absolute_uri(),
        })
        
        # Breadcrumbs
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': '/'},
            {'name': self.category.name, 'url': ''}
        ]
        
        # Category statistics
        context['job_stats'] = {
            'total_jobs': self.get_queryset().count(),
            'jobs_today': self.get_queryset().filter(
                created_at__date=timezone.now().date()
            ).count(),
            'deadline_soon': self.get_queryset().filter(
                application_end_date__lte=timezone.now().date() + timedelta(days=7)
            ).count(),
        }
        
        return context


def job_detail_redirect_view(request, category_slug, job_slug):
    """
    Handle job detail page with proper URL structure.
    
    This view ensures the URL follows /{category}/{job-slug}/ pattern
    and renders the job detail with full SEO optimization.
    """
    
    # Get the job object
    job = get_object_or_404(
        JobPosting.objects.select_related('source', 'category'),
        slug=job_slug,
        category__slug=category_slug,
        status__in=['announced', 'admit_card', 'answer_key', 'result']
    )
    
    # Increment view count
    try:
        job.increment_view_count()
    except Exception as e:
        logger.warning(f"Failed to increment view count for job {job.pk}: {e}")
    
    # Prepare context for rendering
    context = {
        'job': job,
        'seo_title': job.seo_title or f"{job.title} - Apply Online | SarkariBot",
        'seo_description': job.seo_description or f"Apply for {job.title}. Check eligibility, last date, and direct application link.",
        'keywords': job.keywords,
        'canonical_url': request.build_absolute_uri(),
        'structured_data': job.structured_data,
        'open_graph_tags': job.open_graph_tags,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': job.category.name, 'url': f"/{job.category.slug}/"},
            {'name': job.title, 'url': ''}
        ],
    }
    
    # Get related jobs
    related_jobs = JobPosting.objects.filter(
        category=job.category,
        status__in=['announced', 'admit_card', 'answer_key', 'result']
    ).exclude(pk=job.pk).select_related('source', 'category')[:5]
    context['related_jobs'] = related_jobs
    
    # Get job milestones
    milestones = job.milestones.filter(is_active=True).order_by('-milestone_date')[:10]
    context['milestones'] = milestones
    
    return render(request, 'jobs/job_detail.html', context)


def category_list_view(request, category_slug):
    """
    Handle category listing page with proper URL structure.
    
    This view ensures the URL follows /{category}/ pattern
    and renders the category listing with SEO optimization.
    """
    
    # Get the category
    category = get_object_or_404(JobCategory, slug=category_slug, is_active=True)
    
    # Get jobs for this category
    jobs_queryset = JobPosting.objects.filter(
        category=category,
        status__in=['announced', 'admit_card', 'answer_key', 'result']
    ).select_related('source', 'category').order_by('-created_at', '-published_at')
    
    # Pagination
    paginator = Paginator(jobs_queryset, 20)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)
    
    # SEO metadata
    seo_title = f"{category.name} - Government Jobs 2025 | SarkariBot"
    seo_description = f"Latest {category.name.lower()} notifications. Check eligibility, apply online, download admit cards and results."
    
    # Prepare context
    context = {
        'category': category,
        'jobs': jobs,
        'seo_title': seo_title,
        'seo_description': seo_description,
        'canonical_url': request.build_absolute_uri(),
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': category.name, 'url': ''}
        ],
        'job_stats': {
            'total_jobs': jobs_queryset.count(),
            'jobs_today': jobs_queryset.filter(
                created_at__date=timezone.now().date()
            ).count(),
            'deadline_soon': jobs_queryset.filter(
                application_end_date__lte=timezone.now().date() + timedelta(days=7)
            ).count(),
        }
    }
    
    return render(request, 'jobs/category_list.html', context)