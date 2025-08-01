# Generated for scraping performance optimization
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add optimized database indexes for scraping operations.
    
    This migration adds indexes to improve performance for:
    - Source scheduling and status tracking
    - Scrape log monitoring and analytics
    - Scraped data processing and quality tracking
    """

    dependencies = [
        ('scraping', '0001_initial'),
    ]

    operations = [
        # ScrapeLog performance indexes
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS scraping_scrapelog_source_started_idx 
            ON scraping_scrapelog (source_id, started_at DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS scraping_scrapelog_source_started_idx;
            """
        ),
        
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS scraping_scrapelog_status_started_idx 
            ON scraping_scrapelog (status, started_at DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS scraping_scrapelog_status_started_idx;
            """
        ),
        
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS scraping_scrapelog_performance_idx 
            ON scraping_scrapelog (scraper_engine, status, duration_seconds DESC) 
            WHERE status = 'completed';
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS scraping_scrapelog_performance_idx;
            """
        ),
        
        # ScrapedData performance indexes
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS scraping_scrapeddata_source_created_idx 
            ON scraping_scrapeddata (source_id, created_at DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS scraping_scrapeddata_source_created_idx;
            """
        ),
        
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS scraping_scrapeddata_processing_idx 
            ON scraping_scrapeddata (processing_status, created_at DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS scraping_scrapeddata_processing_idx;
            """
        ),
        
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS scraping_scrapeddata_quality_idx 
            ON scraping_scrapeddata (data_quality_score DESC, field_count DESC) 
            WHERE processing_status = 'processed';
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS scraping_scrapeddata_quality_idx;
            """
        ),
        
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS scraping_scrapeddata_duplicate_check_idx 
            ON scraping_scrapeddata (source_id, content_hash);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS scraping_scrapeddata_duplicate_check_idx;
            """
        ),
        
        # SourceStatistics indexes for analytics
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS scraping_sourcestatistics_source_date_idx 
            ON scraping_sourcestatistics (source_id, date DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS scraping_sourcestatistics_source_date_idx;
            """
        ),
        
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS scraping_sourcestatistics_performance_idx 
            ON scraping_sourcestatistics (date DESC, success_rate DESC, jobs_found DESC) 
            WHERE scrapes_attempted > 0;
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS scraping_sourcestatistics_performance_idx;
            """
        ),
        
        # ScrapingError indexes for debugging
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS scraping_scrapingerror_log_occurred_idx 
            ON scraping_scrapingerror (scrape_log_id, occurred_at DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS scraping_scrapingerror_log_occurred_idx;
            """
        ),
        
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS scraping_scrapingerror_type_resolved_idx 
            ON scraping_scrapingerror (error_type, resolved, occurred_at DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS scraping_scrapingerror_type_resolved_idx;
            """
        ),
        
        # ProxyConfiguration indexes
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS scraping_proxyconfiguration_performance_idx 
            ON scraping_proxyconfiguration (status, success_rate DESC, average_response_time ASC) 
            WHERE status = 'active';
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS scraping_proxyconfiguration_performance_idx;
            """
        ),
    ]