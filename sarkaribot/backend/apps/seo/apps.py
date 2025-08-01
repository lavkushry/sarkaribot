"""
SEO App Configuration for SarkariBot.

Production-ready configuration for the NLP-powered SEO automation engine
with comprehensive initialization, validation, and signal handling.
"""

from django.apps import AppConfig
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)


class SeoConfig(AppConfig):
    """Configuration for the SEO automation app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.seo'
    verbose_name = 'SEO Automation'
    
    def ready(self):
        """
        Initialize SEO app when Django starts.
        
        This method handles:
        - Signal registration for automatic SEO metadata generation
        - NLP model validation and initialization 
        - SEO engine startup configuration
        - Health checks for SEO dependencies
        """
        try:
            # Import signal handlers for SEO automation
            self._register_signals()
            
            # Initialize and validate NLP dependencies
            self._validate_nlp_dependencies()
            
            # Initialize SEO engine
            self._initialize_seo_engine()
            
            # Setup SEO logging
            self._setup_seo_logging()
            
            logger.info("SEO automation app initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SEO app: {e}")
            if settings.DEBUG:
                raise
    
    def _register_signals(self):
        """Register signal handlers for SEO automation."""
        try:
            # Import signals to register handlers
            from apps.seo import signals  # noqa
            logger.debug("SEO signal handlers registered")
        except ImportError as e:
            logger.warning(f"SEO signals not found: {e}")
    
    def _validate_nlp_dependencies(self):
        """Validate NLP dependencies and spaCy model availability."""
        try:
            # Check if spaCy is available
            import spacy
            
            # Check if the required model is available
            model_name = getattr(settings, 'SPACY_MODEL', 'en_core_web_sm')
            
            try:
                # Try to load the model to validate it's installed
                nlp = spacy.load(model_name)
                logger.info(f"spaCy model '{model_name}' loaded successfully")
                
                # Validate model components
                if not nlp.has_pipe('ner'):
                    logger.warning("spaCy model missing Named Entity Recognition component")
                if not nlp.has_pipe('tagger'):
                    logger.warning("spaCy model missing Part-of-Speech tagger component")
                    
            except OSError:
                logger.error(f"spaCy model '{model_name}' not found. "
                           f"Install with: python -m spacy download {model_name}")
                if not settings.DEBUG:
                    # In production, we might want to use a fallback
                    logger.warning("Falling back to basic keyword extraction")
                else:
                    raise
                    
        except ImportError:
            logger.error("spaCy not installed. SEO engine will use basic text processing")
            if settings.DEBUG and getattr(settings, 'ENABLE_SEO_AUTOMATION', True):
                logger.warning("Install spaCy for full NLP functionality: pip install spacy")
    
    def _initialize_seo_engine(self):
        """Initialize and validate the SEO engine."""
        try:
            from apps.seo.engine import seo_engine
            
            # Test engine functionality with basic input
            test_data = {
                'id': 1,
                'title': 'Test Job Posting',
                'description': 'Test job description for validation',
                'category': {'name': 'Test Category', 'slug': 'test-category'}
            }
            
            # Attempt basic metadata generation to validate engine
            metadata = seo_engine.generate_seo_metadata(test_data)
            
            if metadata and metadata.get('seo_title') and metadata.get('seo_description'):
                logger.info("SEO engine initialized and validated successfully")
            else:
                logger.warning("SEO engine validation returned incomplete metadata")
                
        except Exception as e:
            logger.error(f"Failed to initialize SEO engine: {e}")
            if settings.DEBUG:
                raise
    
    def _setup_seo_logging(self):
        """Setup specialized logging for SEO operations."""
        try:
            # Configure SEO-specific logging if not already configured
            seo_logger = logging.getLogger('apps.seo')
            
            if not seo_logger.handlers and settings.DEBUG:
                # In development, add console handler if none exists
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                seo_logger.addHandler(handler)
                seo_logger.setLevel(logging.DEBUG)
                
            logger.debug("SEO logging configured")
            
        except Exception as e:
            logger.warning(f"Failed to setup SEO logging: {e}")
    
    @classmethod
    def validate_seo_settings(cls):
        """
        Validate SEO-related Django settings.
        
        Returns:
            List of validation errors or empty list if all valid
        """
        errors = []
        
        # Check required settings
        if not hasattr(settings, 'SARKARIBOT_SETTINGS'):
            errors.append("SARKARIBOT_SETTINGS not configured")
        else:
            sarkaribot_settings = settings.SARKARIBOT_SETTINGS
            
            if not sarkaribot_settings.get('ENABLE_SEO_AUTOMATION', True):
                logger.warning("SEO automation is disabled in settings")
            
            if not sarkaribot_settings.get('GENERATE_SITEMAP', True):
                logger.info("Sitemap generation is disabled")
        
        # Check SEO-specific settings
        if not hasattr(settings, 'SEO_TITLE_MAX_LENGTH'):
            errors.append("SEO_TITLE_MAX_LENGTH not configured")
        
        if not hasattr(settings, 'SEO_DESCRIPTION_MAX_LENGTH'):
            errors.append("SEO_DESCRIPTION_MAX_LENGTH not configured")
        
        if not hasattr(settings, 'SEO_KEYWORDS_LIMIT'):
            errors.append("SEO_KEYWORDS_LIMIT not configured")
        
        # Check cache configuration for SEO performance
        if not hasattr(settings, 'CACHES') or 'default' not in settings.CACHES:
            errors.append("Cache configuration missing - required for SEO performance")
        
        return errors
