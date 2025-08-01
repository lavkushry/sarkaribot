"""
Core signal handlers for SarkariBot.
"""

import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger(__name__)


@receiver(post_save)
def log_model_creation(sender, instance, created, **kwargs):
    """
    Log when new model instances are created.
    
    Args:
        sender: The model class
        instance: The model instance
        created: Boolean indicating if instance was created
        **kwargs: Additional keyword arguments
    """
    if created:
        logger.info(f"Created new {sender.__name__}: {instance}")


@receiver(pre_delete)
def log_model_deletion(sender, instance, **kwargs):
    """
    Log when model instances are about to be deleted.
    
    Args:
        sender: The model class
        instance: The model instance
        **kwargs: Additional keyword arguments
    """
    logger.warning(f"Deleting {sender.__name__}: {instance}")
