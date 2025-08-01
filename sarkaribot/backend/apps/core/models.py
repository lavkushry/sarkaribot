"""
Core models for SarkariBot project.

This module contains shared models and abstract base classes
used across the application.
"""

from django.db import models
from django.utils import timezone
import uuid


class TimestampedModel(models.Model):
    """
    Abstract base class that provides timestamp fields.
    
    All models should inherit from this to get consistent
    created_at and updated_at timestamps.
    """
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated"
    )
    
    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract base class that provides UUID primary key.
    
    Use this for models that need UUID instead of auto-incrementing IDs.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract base class that provides soft delete functionality.
    
    Records are not actually deleted from the database but marked
    as deleted with a timestamp.
    """
    
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the record was soft deleted"
    )
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete the record instead of hard delete."""
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def hard_delete(self, using=None, keep_parents=False):
        """Actually delete the record from the database."""
        super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.save()
    
    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft deleted."""
        return self.deleted_at is not None
