# Generated for sources performance optimization
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add optimized database indexes for government sources.
    
    This migration adds indexes to improve performance for:
    - Source management and scheduling
    - Statistics tracking and reporting
    - Active source filtering
    """

    dependencies = [
        ('sources', '0001_initial'),
    ]

    operations = [
        # GovernmentSource performance indexes
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS sources_governmentsource_active_status_idx 
            ON sources_governmentsource (active, status) 
            WHERE active = true;
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS sources_governmentsource_active_status_idx;
            """
        ),
        
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS sources_governmentsource_scrape_scheduling_idx 
            ON sources_governmentsource (last_scraped ASC, scrape_frequency, active) 
            WHERE active = true AND status = 'active';
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS sources_governmentsource_scrape_scheduling_idx;
            """
        ),
        
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS sources_governmentsource_name_active_idx 
            ON sources_governmentsource (name, active) 
            WHERE active = true;
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS sources_governmentsource_name_active_idx;
            """
        ),
        
        # SourceStatistics performance indexes
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS sources_sourcestatistics_source_date_idx 
            ON sources_sourcestatistics (source_id, date DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS sources_sourcestatistics_source_date_idx;
            """
        ),
        
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS sources_sourcestatistics_date_performance_idx 
            ON sources_sourcestatistics (date DESC, scrapes_successful DESC, jobs_found DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS sources_sourcestatistics_date_performance_idx;
            """
        ),
        
        # SourceCategory indexes
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS sources_sourcecategory_position_name_idx 
            ON sources_sourcecategory (position, name);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS sources_sourcecategory_position_name_idx;
            """
        ),
    ]