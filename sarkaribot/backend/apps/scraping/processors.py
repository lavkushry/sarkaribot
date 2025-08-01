"""
Data processing utilities for scraped content.

This module handles validation, cleaning, and transformation of scraped
data into structured format for job postings.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
import re
import hashlib
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes raw scraped data into structured job posting data.
    
    Handles data validation, cleaning, and transformation to ensure
    consistent data quality across all scraped sources.
    """
    
    def __init__(self):
        """Initialize the data processor with validation rules."""
        self.date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})',  # DD Month YYYY
            r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})', # Month DD, YYYY
        ]
        
        self.number_patterns = [
            r'(\d+)',  # Simple number
            r'(\d{1,3}(?:,\d{3})*)',  # Number with commas
            r'(\d+(?:\.\d{2})?)',  # Decimal number
        ]
        
        # Common department abbreviations and full names
        self.department_mapping = {
            'SSC': 'Staff Selection Commission',
            'UPSC': 'Union Public Service Commission',
            'RRB': 'Railway Recruitment Board',
            'IBPS': 'Institute of Banking Personnel Selection',
            'SBI': 'State Bank of India',
            'LIC': 'Life Insurance Corporation',
            'DRDO': 'Defence Research and Development Organisation',
            'ISRO': 'Indian Space Research Organisation',
            'ONGC': 'Oil and Natural Gas Corporation',
            'BHEL': 'Bharat Heavy Electricals Limited',
            'SAIL': 'Steel Authority of India Limited',
            'NTPC': 'National Thermal Power Corporation',
            'BSNL': 'Bharat Sanchar Nigam Limited',
            'NHM': 'National Health Mission',
            'AIIMS': 'All India Institute of Medical Sciences',
        }
    
    def process_item(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single scraped item into structured job posting data.
        
        Args:
            raw_data: Raw scraped data dictionary
            
        Returns:
            Dict containing processed and validated job posting data
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        try:
            logger.debug(f"Processing item: {raw_data.get('title', 'Unknown')}")
            
            processed_data = {
                # Required fields
                'title': self._clean_title(raw_data.get('title', '')),
                'description': self._clean_description(raw_data.get('description', '')),
                'source_url': self._validate_url(raw_data.get('url', '')),
                
                # Optional core fields
                'department': self._extract_department(raw_data),
                'total_posts': self._extract_number(raw_data.get('posts', raw_data.get('vacancies', ''))),
                'qualification': self._clean_text(raw_data.get('qualification', raw_data.get('eligibility', ''))),
                
                # Date fields
                'notification_date': self._parse_date(raw_data.get('notification_date', raw_data.get('published_date'))),
                'application_end_date': self._parse_date(raw_data.get('last_date', raw_data.get('application_end_date'))),
                'exam_date': self._parse_date(raw_data.get('exam_date')),
                
                # Financial information
                'application_fee': self._extract_fee(raw_data.get('fee', raw_data.get('application_fee'))),
                'salary_min': self._extract_salary_range(raw_data.get('salary', ''))[0],
                'salary_max': self._extract_salary_range(raw_data.get('salary', ''))[1],
                
                # Age limits
                'min_age': self._extract_age_range(raw_data.get('age_limit', ''))[0],
                'max_age': self._extract_age_range(raw_data.get('age_limit', ''))[1],
                
                # Links
                'application_link': self._validate_url(raw_data.get('apply_link', raw_data.get('application_link', ''))),
                'notification_pdf': self._validate_url(raw_data.get('notification_pdf', raw_data.get('pdf_link', ''))),
                
                # Location information
                'location': self._clean_text(raw_data.get('location', '')),
                'state': self._extract_state(raw_data.get('location', '')),
                
                # Additional metadata
                'content_hash': self._generate_content_hash(raw_data),
                'raw_data_keys': list(raw_data.keys()),
                'processing_timestamp': datetime.now().isoformat(),
            }
            
            # Validate required fields
            self._validate_processed_data(processed_data)
            
            # Clean up None values and empty strings
            processed_data = {k: v for k, v in processed_data.items() 
                            if v is not None and v != ''}
            
            logger.debug(f"Successfully processed item: {processed_data.get('title')}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process item: {e}")
            raise ValueError(f"Data processing failed: {e}")
    
    def _clean_title(self, title: str) -> str:
        """
        Clean and normalize job title.
        
        Args:
            title: Raw job title
            
        Returns:
            Cleaned job title
        """
        if not title:
            return ''
        
        # Remove extra whitespace and normalize
        title = ' '.join(title.split())
        
        # Remove common prefixes that don't add value
        prefixes_to_remove = [
            'recruitment for',
            'recruitment of',
            'notification for',
            'advertisement for',
            'vacancy for',
            'apply for',
        ]
        
        title_lower = title.lower()
        for prefix in prefixes_to_remove:
            if title_lower.startswith(prefix):
                title = title[len(prefix):].strip()
                break
        
        # Capitalize properly
        title = ' '.join(word.capitalize() if word.lower() not in ['of', 'for', 'and', 'in', 'at', 'to'] 
                        else word.lower() for word in title.split())
        
        # Ensure first word is capitalized
        if title:
            title = title[0].upper() + title[1:]
        
        return title[:255]  # Limit length
    
    def _clean_description(self, description: str) -> str:
        """
        Clean and format job description.
        
        Args:
            description: Raw job description
            
        Returns:
            Cleaned job description
        """
        if not description:
            return ''
        
        # Remove HTML tags if present
        description = re.sub(r'<[^>]+>', '', description)
        
        # Normalize whitespace
        description = ' '.join(description.split())
        
        # Remove excessive repetition
        sentences = description.split('. ')
        unique_sentences = []
        for sentence in sentences:
            if sentence.strip() and sentence not in unique_sentences:
                unique_sentences.append(sentence.strip())
        
        return '. '.join(unique_sentences)
    
    def _clean_text(self, text: str) -> str:
        """
        General text cleaning utility.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ''
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove special characters except common punctuation
        text = re.sub(r'[^\w\s\.\,\-\(\)\/]', '', text)
        
        return text.strip()
    
    def _extract_department(self, raw_data: Dict[str, Any]) -> str:
        """
        Extract and normalize department/organization name.
        
        Args:
            raw_data: Raw scraped data
            
        Returns:
            Normalized department name
        """
        # Check various possible field names
        department_fields = ['department', 'organization', 'ministry', 'board', 'commission']
        
        for field in department_fields:
            if field in raw_data and raw_data[field]:
                dept = str(raw_data[field]).strip()
                
                # Check if it's an abbreviation we can expand
                dept_upper = dept.upper()
                if dept_upper in self.department_mapping:
                    return self.department_mapping[dept_upper]
                
                return self._clean_text(dept)
        
        # Try to extract from title or description
        title = raw_data.get('title', '')
        for abbrev, full_name in self.department_mapping.items():
            if abbrev.lower() in title.lower():
                return full_name
        
        return ''
    
    def _extract_number(self, text: str) -> Optional[int]:
        """
        Extract numeric value from text.
        
        Args:
            text: Text containing number
            
        Returns:
            Extracted number or None
        """
        if not text:
            return None
        
        text = str(text).strip()
        
        # Try different number patterns
        for pattern in self.number_patterns:
            match = re.search(pattern, text)
            if match:
                number_str = match.group(1).replace(',', '')
                try:
                    return int(number_str)
                except ValueError:
                    continue
        
        return None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """
        Parse date from various formats.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Parsed date object or None
        """
        if not date_str:
            return None
        
        date_str = str(date_str).strip()
        
        # Try different date patterns
        for pattern in self.date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    groups = match.groups()
                    
                    if len(groups) == 3:
                        # Determine format and parse accordingly
                        if pattern.startswith(r'(\d{4})'):  # YYYY-MM-DD format
                            year, month, day = groups
                            return date(int(year), int(month), int(day))
                        elif pattern.startswith(r'(\d{1,2})'):  # DD-MM-YYYY format
                            day, month, year = groups
                            return date(int(year), int(month), int(day))
                        elif 'Month' in pattern or '[A-Za-z]' in pattern:
                            # Handle month name formats
                            return self._parse_month_name_date(groups)
                
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _parse_month_name_date(self, groups: tuple) -> Optional[date]:
        """
        Parse date with month names.
        
        Args:
            groups: Regex groups containing date parts
            
        Returns:
            Parsed date or None
        """
        month_mapping = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12,
        }
        
        try:
            if len(groups) == 3:
                day_str, month_str, year_str = groups
                
                # Handle different patterns
                if month_str.isdigit():
                    day, month, year = int(day_str), int(month_str), int(year_str)
                else:
                    month_name = month_str.lower()
                    if month_name in month_mapping:
                        day, month, year = int(day_str), month_mapping[month_name], int(year_str)
                    else:
                        return None
                
                return date(year, month, day)
        
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _extract_fee(self, fee_str: Optional[str]) -> Optional[Decimal]:
        """
        Extract application fee amount.
        
        Args:
            fee_str: Fee string
            
        Returns:
            Fee amount as Decimal or None
        """
        if not fee_str:
            return None
        
        fee_str = str(fee_str).lower().strip()
        
        # Check for "free" or "no fee"
        if any(word in fee_str for word in ['free', 'no fee', 'nil', 'exempt']):
            return Decimal('0.00')
        
        # Extract numeric value
        number_match = re.search(r'(\d+(?:\.\d{2})?)', fee_str)
        if number_match:
            try:
                return Decimal(number_match.group(1))
            except (ValueError, TypeError):
                pass
        
        return None
    
    def _extract_salary_range(self, salary_str: str) -> tuple[Optional[int], Optional[int]]:
        """
        Extract salary range from text.
        
        Args:
            salary_str: Salary information string
            
        Returns:
            Tuple of (min_salary, max_salary)
        """
        if not salary_str:
            return None, None
        
        salary_str = str(salary_str).lower().strip()
        
        # Look for range patterns like "25000-50000" or "25000 to 50000"
        range_patterns = [
            r'(\d+(?:,\d{3})*)\s*[-to]+\s*(\d+(?:,\d{3})*)',
            r'between\s+(\d+(?:,\d{3})*)\s+and\s+(\d+(?:,\d{3})*)',
            r'from\s+(\d+(?:,\d{3})*)\s+to\s+(\d+(?:,\d{3})*)',
        ]
        
        for pattern in range_patterns:
            match = re.search(pattern, salary_str)
            if match:
                try:
                    min_sal = int(match.group(1).replace(',', ''))
                    max_sal = int(match.group(2).replace(',', ''))
                    return min_sal, max_sal
                except (ValueError, TypeError):
                    continue
        
        # Look for single value
        single_match = re.search(r'(\d+(?:,\d{3})*)', salary_str)
        if single_match:
            try:
                salary = int(single_match.group(1).replace(',', ''))
                return salary, salary
            except (ValueError, TypeError):
                pass
        
        return None, None
    
    def _extract_age_range(self, age_str: str) -> tuple[Optional[int], Optional[int]]:
        """
        Extract age range from text.
        
        Args:
            age_str: Age limit string
            
        Returns:
            Tuple of (min_age, max_age)
        """
        if not age_str:
            return None, None
        
        age_str = str(age_str).lower().strip()
        
        # Look for range patterns
        range_patterns = [
            r'(\d+)\s*[-to]+\s*(\d+)',
            r'between\s+(\d+)\s+and\s+(\d+)',
            r'from\s+(\d+)\s+to\s+(\d+)',
            r'minimum\s+(\d+).*maximum\s+(\d+)',
        ]
        
        for pattern in range_patterns:
            match = re.search(pattern, age_str)
            if match:
                try:
                    min_age = int(match.group(1))
                    max_age = int(match.group(2))
                    return min_age, max_age
                except (ValueError, TypeError):
                    continue
        
        # Look for maximum age only
        max_patterns = [
            r'maximum\s+(\d+)',
            r'max\s+(\d+)',
            r'up\s+to\s+(\d+)',
            r'below\s+(\d+)',
        ]
        
        for pattern in max_patterns:
            match = re.search(pattern, age_str)
            if match:
                try:
                    max_age = int(match.group(1))
                    return None, max_age
                except (ValueError, TypeError):
                    continue
        
        # Look for minimum age only
        min_patterns = [
            r'minimum\s+(\d+)',
            r'min\s+(\d+)',
            r'above\s+(\d+)',
            r'over\s+(\d+)',
        ]
        
        for pattern in min_patterns:
            match = re.search(pattern, age_str)
            if match:
                try:
                    min_age = int(match.group(1))
                    return min_age, None
                except (ValueError, TypeError):
                    continue
        
        return None, None
    
    def _extract_state(self, location_str: str) -> str:
        """
        Extract state from location string.
        
        Args:
            location_str: Location text
            
        Returns:
            State name if found
        """
        if not location_str:
            return ''
        
        # List of Indian states and UTs
        states = [
            'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh',
            'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jharkhand', 'karnataka',
            'kerala', 'madhya pradesh', 'maharashtra', 'manipur', 'meghalaya',
            'mizoram', 'nagaland', 'odisha', 'punjab', 'rajasthan', 'sikkim',
            'tamil nadu', 'telangana', 'tripura', 'uttar pradesh', 'uttarakhand',
            'west bengal', 'andaman and nicobar islands', 'chandigarh',
            'dadra and nagar haveli', 'daman and diu', 'delhi', 'jammu and kashmir',
            'ladakh', 'lakshadweep', 'puducherry'
        ]
        
        location_lower = location_str.lower()
        
        for state in states:
            if state in location_lower:
                return state.title()
        
        return ''
    
    def _validate_url(self, url: str) -> str:
        """
        Validate and clean URL.
        
        Args:
            url: URL string to validate
            
        Returns:
            Cleaned URL or empty string if invalid
        """
        if not url:
            return ''
        
        url = url.strip()
        
        # Add protocol if missing
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if url_pattern.match(url):
            return url
        
        return ''
    
    def _generate_content_hash(self, raw_data: Dict[str, Any]) -> str:
        """
        Generate a hash of the content for duplicate detection.
        
        Args:
            raw_data: Raw scraped data
            
        Returns:
            SHA256 hash of the content
        """
        # Create a string representation of key content fields
        content_fields = ['title', 'description', 'last_date', 'posts', 'qualification']
        content_parts = []
        
        for field in content_fields:
            if field in raw_data and raw_data[field]:
                content_parts.append(str(raw_data[field]).strip().lower())
        
        content_string = '|'.join(content_parts)
        
        # Generate hash
        return hashlib.sha256(content_string.encode('utf-8')).hexdigest()[:16]
    
    def _validate_processed_data(self, processed_data: Dict[str, Any]) -> None:
        """
        Validate processed data to ensure required fields are present.
        
        Args:
            processed_data: Processed data dictionary
            
        Raises:
            ValueError: If validation fails
        """
        # Check required fields
        required_fields = ['title', 'source_url']
        
        for field in required_fields:
            if not processed_data.get(field):
                raise ValueError(f"Required field '{field}' is missing or empty")
        
        # Validate title length
        title = processed_data.get('title', '')
        if len(title) < 10:
            raise ValueError(f"Title too short: '{title}'")
        
        if len(title) > 255:
            processed_data['title'] = title[:255]
        
        # Validate URL format
        url = processed_data.get('source_url', '')
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL format: '{url}'")


class ValidationError(Exception):
    """Custom exception for data validation errors."""
    pass
