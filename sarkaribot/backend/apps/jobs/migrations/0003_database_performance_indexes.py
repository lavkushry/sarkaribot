# Generated for database performance optimization
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add optimized database indexes for common query patterns.
    
    This migration adds compound indexes to improve performance for:
    - Status + created_at filtering (most common pattern)
    - Category + status filtering (category pages)
    - Application deadline filtering (urgent jobs)
    - Source + status filtering (source-specific pages)
    - View count optimization (trending jobs)
    - Search optimization (title + status)
    """

    dependencies = [
        ('jobs', '0002_jobposting_breadcrumbs_jobposting_canonical_url_and_more'),
    ]

    operations = [
        # Add compound indexes for JobPosting
        migrations.RunSQL(
            # Composite index for status + created_at (most common query pattern)
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS jobs_jobposting_status_created_at_idx 
            ON jobs_jobposting (status, created_at DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS jobs_jobposting_status_created_at_idx;
            """
        ),
        
        migrations.RunSQL(
            # Composite index for category + status + published_at (category pages)
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS jobs_jobposting_category_status_published_idx 
            ON jobs_jobposting (category_id, status, published_at DESC) 
            WHERE status IN ('announced', 'admit_card', 'answer_key', 'result');
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS jobs_jobposting_category_status_published_idx;
            """
        ),
        
        migrations.RunSQL(
            # Index for urgent/expiring jobs (application_end_date filtering)
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS jobs_jobposting_urgent_jobs_idx 
            ON jobs_jobposting (application_end_date ASC, status) 
            WHERE application_end_date IS NOT NULL AND status IN ('announced', 'admit_card');
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS jobs_jobposting_urgent_jobs_idx;
            """
        ),
        
        migrations.RunSQL(
            # Index for source-specific queries
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS jobs_jobposting_source_status_created_idx 
            ON jobs_jobposting (source_id, status, created_at DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS jobs_jobposting_source_status_created_idx;
            """
        ),
        
        migrations.RunSQL(
            # Index for trending/popular jobs (view_count + recency)
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS jobs_jobposting_trending_idx 
            ON jobs_jobposting (view_count DESC, total_posts DESC, created_at DESC) 
            WHERE status IN ('announced', 'admit_card') AND total_posts IS NOT NULL;
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS jobs_jobposting_trending_idx;
            """
        ),
        
        migrations.RunSQL(
            # Index for featured jobs
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS jobs_jobposting_featured_idx 
            ON jobs_jobposting (is_featured, priority, published_at DESC) 
            WHERE is_featured = true;
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS jobs_jobposting_featured_idx;
            """
        ),
        
        migrations.RunSQL(
            # Full-text search optimization for title + department
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS jobs_jobposting_search_idx 
            ON jobs_jobposting USING gin(to_tsvector('english', title || ' ' || COALESCE(department, '')))
            WHERE status IN ('announced', 'admit_card', 'answer_key', 'result');
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS jobs_jobposting_search_idx;
            """
        ),
        
        # Add indexes for JobMilestone
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS jobs_jobmilestone_job_date_idx 
            ON jobs_jobmilestone (job_posting_id, milestone_date DESC, is_active);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS jobs_jobmilestone_job_date_idx;
            """
        ),
        
        # Add indexes for JobView analytics
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS jobs_jobview_job_created_idx 
            ON jobs_jobview (job_posting_id, created_at DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS jobs_jobview_job_created_idx;
            """
        ),
        
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS jobs_jobview_daily_stats_idx 
            ON jobs_jobview (DATE(created_at), job_posting_id);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS jobs_jobview_daily_stats_idx;
            """
        ),
    ]