# Generated for SarkariBot SEO advanced indexing strategy
# Adds composite and partial indexes for common query patterns

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo', '0002_initial'),
    ]

    operations = [
        # SitemapEntry advanced indexes
        migrations.RunSQL(
            # Add partial index for active sitemap entries only
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS seo_sitemap_active_priority_partial "
            "ON seo_sitemapentry (priority DESC, last_modified DESC) "
            "WHERE is_active = true;",
            reverse_sql="DROP INDEX IF EXISTS seo_sitemap_active_priority_partial;"
        ),
        
        # SEOMetadata advanced indexes
        migrations.AddIndex(
            model_name='seometadata',
            index=models.Index(fields=['title'], name='seo_seometa_title_idx'),
        ),
        migrations.AddIndex(
            model_name='seometadata',
            index=models.Index(fields=['canonical_url'], name='seo_seometa_canonical_url_idx'),
        ),
        migrations.AddIndex(
            model_name='seometadata',
            index=models.Index(fields=['content_type', '-created_at'], name='seo_seometa_content_type_created_idx'),
        ),
        migrations.AddIndex(
            model_name='seometadata',
            index=models.Index(fields=['og_type'], name='seo_seometa_og_type_idx'),
        ),
        
        # Add partial index for SEOMetadata with quality scores
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS seo_seometa_quality_score_partial "
            "ON seo_seometadata (quality_score DESC, created_at DESC) "
            "WHERE quality_score IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS seo_seometa_quality_score_partial;"
        ),
        
        # KeywordTracking advanced indexes
        migrations.AddIndex(
            model_name='keywordtracking',
            index=models.Index(fields=['target_url'], name='seo_keyword_target_url_idx'),
        ),
        migrations.AddIndex(
            model_name='keywordtracking',
            index=models.Index(fields=['-search_volume', 'difficulty_score'], name='seo_keyword_volume_difficulty_idx'),
        ),
        migrations.AddIndex(
            model_name='keywordtracking',
            index=models.Index(fields=['best_position', 'current_position'], name='seo_keyword_position_tracking_idx'),
        ),
        
        # Add partial index for target keywords only
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS seo_keyword_target_partial "
            "ON seo_keywordtracking (current_position, search_volume DESC) "
            "WHERE is_target_keyword = true;",
            reverse_sql="DROP INDEX IF EXISTS seo_keyword_target_partial;"
        ),
        
        # SEOAuditLog advanced indexes
        migrations.AddIndex(
            model_name='seoauditlog',
            index=models.Index(fields=['triggered_by'], name='seo_audit_triggered_by_idx'),
        ),
        migrations.AddIndex(
            model_name='seoauditlog',
            index=models.Index(fields=['processing_time', 'items_processed'], name='seo_audit_performance_idx'),
        ),
        migrations.AddIndex(
            model_name='seoauditlog',
            index=models.Index(fields=['status'], name='seo_audit_status_idx'),
        ),
        
        # Add partial index for recent audit logs (last 30 days)
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS seo_audit_recent_partial "
            "ON seo_seoauditlog (created_at DESC, status) "
            "WHERE created_at >= CURRENT_DATE - INTERVAL '30 days';",
            reverse_sql="DROP INDEX IF EXISTS seo_audit_recent_partial;"
        ),
        
        # Add composite index for sitemap generation optimization
        migrations.AddIndex(
            model_name='sitemapentry',
            index=models.Index(fields=['-priority', 'change_frequency', '-last_modified'], name='seo_sitemap_generation_idx'),
        ),
    ]