"""
Core utilities and helper functions for SarkariBot.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from django.utils.text import slugify
from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_unique_slug(
    title: str, 
    model_class, 
    slug_field: str = 'slug',
    max_length: int = 255
) -> str:
    """
    Generate a unique slug for a model instance.
    
    Args:
        title: The title to generate slug from
        model_class: The Django model class
        slug_field: The name of the slug field
        max_length: Maximum length of the slug
        
    Returns:
        A unique slug string
        
    Raises:
        ValueError: If unable to generate unique slug
    """
    base_slug = slugify(title)[:max_length-10]  # Reserve space for counter
    
    if not base_slug:
        base_slug = 'item'
    
    slug = base_slug
    counter = 1
    
    # Check if slug already exists
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
        
        # Prevent infinite loop
        if counter > 1000:
            raise ValueError(f"Unable to generate unique slug for: {title}")
    
    return slug


def clean_html_text(text: str) -> str:
    """
    Clean HTML tags and normalize whitespace from text.
    
    Args:
        text: Raw text that may contain HTML
        
    Returns:
        Cleaned text with HTML removed and normalized whitespace
    """
    if not text:
        return ""
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    
    # Normalize whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text


def extract_date_from_text(text: str) -> Optional[datetime]:
    """
    Extract date from text using various patterns.
    
    Args:
        text: Text containing potential date information
        
    Returns:
        Extracted datetime object or None if no date found
    """
    if not text:
        return None
    
    # Common date patterns in government notifications
    date_patterns = [
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # DD-MM-YYYY or DD/MM/YYYY
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # YYYY-MM-DD or YYYY/MM/DD
        r'(\d{1,2}\s+\w+\s+\d{4})',       # DD Month YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            try:
                # Try different parsing formats
                for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d', '%d %B %Y', '%d %b %Y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
            except Exception as e:
                logger.warning(f"Error parsing date '{date_str}': {e}")
                continue
    
    return None


def extract_dates(text: str) -> List[datetime]:
    """
    Extract all dates from text using various patterns.
    
    Args:
        text: Text containing potential date information
        
    Returns:
        List of extracted datetime objects
    """
    if not text:
        return []
    
    dates = []
    
    # Common date patterns in government notifications
    date_patterns = [
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # DD-MM-YYYY or DD/MM/YYYY
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # YYYY-MM-DD or YYYY/MM/DD
        r'(\d{1,2}\s+\w+\s+\d{4})',       # DD Month YYYY
    ]
    
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            date_str = match.group(1)
            try:
                # Try different parsing formats
                for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d', '%d %B %Y', '%d %b %Y']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        dates.append(parsed_date)
                        break
                    except ValueError:
                        continue
            except Exception as e:
                logger.warning(f"Error parsing date '{date_str}': {e}")
                continue
    
    return dates


def normalize_text(text: str) -> str:
    """
    Normalize text by cleaning whitespace, removing special characters.
    
    Args:
        text: Raw text to normalize
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
    
    # Remove multiple consecutive punctuation
    text = re.sub(r'[.,!?;:]{2,}', '.', text)
    
    return text


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number format.
    
    Args:
        phone: Raw phone number string
        
    Returns:
        Normalized phone number
    """
    if not phone:
        return ""
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle Indian phone numbers
    if len(digits) == 10:
        return f"+91{digits}"
    elif len(digits) == 12 and digits.startswith('91'):
        return f"+{digits}"
    
    return digits


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def calculate_age_limit(min_age: int, max_age: int, reference_date: Optional[datetime] = None) -> Dict[str, datetime]:
    """
    Calculate birth date range for age limits.
    
    Args:
        min_age: Minimum age requirement
        max_age: Maximum age requirement
        reference_date: Reference date for calculation (defaults to today)
        
    Returns:
        Dictionary with min_birth_date and max_birth_date
    """
    if reference_date is None:
        reference_date = timezone.now()
    
    max_birth_date = reference_date.replace(year=reference_date.year - min_age)
    min_birth_date = reference_date.replace(year=reference_date.year - max_age - 1)
    
    return {
        'min_birth_date': min_birth_date,
        'max_birth_date': max_birth_date
    }


def format_currency(amount: float, currency: str = 'INR') -> str:
    """
    Format currency amount in Indian format.
    
    Args:
        amount: Amount to format
        currency: Currency code (default: INR)
        
    Returns:
        Formatted currency string
    """
    if currency == 'INR':
        # Indian numbering system (lakhs, crores)
        if amount >= 10000000:  # 1 crore
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:  # 1 lakh
            return f"₹{amount/100000:.2f} L"
        else:
            return f"₹{amount:,.2f}"
    
    return f"{currency} {amount:,.2f}"


def get_financial_year(date: Optional[datetime] = None) -> str:
    """
    Get financial year for a given date.
    
    Args:
        date: Date to get financial year for (defaults to today)
        
    Returns:
        Financial year string (e.g., "2024-25")
    """
    if date is None:
        date = timezone.now()
    
    if date.month >= 4:  # April onwards
        start_year = date.year
        end_year = date.year + 1
    else:  # January to March
        start_year = date.year - 1
        end_year = date.year
    
    return f"{start_year}-{str(end_year)[-2:]}"


class PerformanceMonitor:
    """
    Context manager for monitoring function performance.
    
    Usage:
        with PerformanceMonitor("operation_name") as monitor:
            # Your code here
            pass
    """
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = timezone.now()
        logger.info(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = timezone.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            logger.info(f"Completed {self.operation_name} in {duration:.2f} seconds")
        else:
            logger.error(f"Failed {self.operation_name} after {duration:.2f} seconds: {exc_val}")
    
    @property
    def duration(self) -> Optional[float]:
        """Get the duration of the monitored operation in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
