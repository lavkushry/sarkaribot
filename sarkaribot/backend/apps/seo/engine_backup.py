"""
SEO Automation Engine for SarkariBot.

Implements NLP-powered metadata generation using spaCy for keyword extraction
and content analysis according to Knowledge.md specifications.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from django.utils.text import slugify

# Try to import spaCy with fallback
try:
    import spacy
    from spacy.lang.en.stop_words import STOP_WORDS
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    STOP_WORDS = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 
        'your', 'yours', 'yourself', 'he', 'him', 'his', 'himself', 'she', 'her', 
        'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their',
        'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
        'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
        'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
        'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after', 'above',
        'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
        'further', 'then', 'once'
    }


logger = logging.getLogger(__name__)


class NLPSEOEngine:
    """
    NLP-powered SEO automation engine using spaCy.
    
    Implements the specifications from Knowledge.md for automatic
    metadata generation, keyword extraction, and content optimization.
    """
    
    def __init__(self):
        """Initialize the NLP engine with spaCy model."""
        self.nlp = None
        self._load_nlp_model()
        
        # SEO configuration from Knowledge.md
        self.seo_title_max_length = getattr(settings, 'SEO_TITLE_MAX_LENGTH', 60)
        self.seo_description_max_length = getattr(settings, 'SEO_DESCRIPTION_MAX_LENGTH', 160)
        self.seo_keywords_max_count = getattr(settings, 'SEO_KEYWORDS_MAX_COUNT', 7)
    
    def _load_nlp_model(self) -> None:
        """Load spaCy English model with fallback."""
        if not SPACY_AVAILABLE:
            logger.warning("spaCy not available - using basic text processing")
            self.nlp = None
            return
            
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Successfully loaded spaCy English model")
        except OSError:
            try:
                # Fallback to basic English model
                self.nlp = spacy.blank("en")
                logger.warning("Using basic spaCy model - install en_core_web_sm for better performance")
            except Exception as e:
                logger.error(f"Failed to initialize spaCy: {e}")
                self.nlp = None
    
    def generate_seo_metadata(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate SEO-optimized metadata using NLP as per Knowledge.md specifications.
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            Dictionary with SEO metadata including title, description, keywords
            
        Raises:
            ValueError: If required job data is missing
        """
        try:
            if not job_data.get('title'):
                raise ValueError("Job title is required for SEO metadata generation")
            
            logger.info(f"Generating SEO metadata for job: {job_data['title']}")
            
            # Extract keywords using spaCy NLP
            keywords = self._extract_keywords(job_data)
            
            # Generate SEO title (50-60 characters as per Knowledge.md)
            seo_title = self._generate_seo_title(job_data)
            
            # Generate meta description (150-160 characters as per Knowledge.md)
            seo_description = self._generate_seo_description(job_data)
            
            # Generate structured data (schema.org JobPosting)
            structured_data = self._generate_job_schema(job_data)
            
            # Generate URL slug
            slug = self._generate_slug(job_data['title'])
            
            metadata = {
                'seo_title': seo_title[:self.seo_title_max_length],
                'seo_description': seo_description[:self.seo_description_max_length],
                'keywords': keywords[:self.seo_keywords_max_count],
                'structured_data': structured_data,
                'slug': slug,
                'canonical_url': f"/{job_data.get('category', 'jobs')}/{slug}/",
                'generation_method': 'auto_nlp',
                'quality_score': self._calculate_quality_score(job_data, keywords)
            }
            
            logger.info(f"Generated SEO metadata with quality score: {metadata['quality_score']}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error generating SEO metadata: {e}")
            return self._generate_fallback_metadata(job_data)
    
    def _extract_keywords(self, job_data: Dict[str, Any]) -> List[str]:
        """Extract keywords using spaCy NLP pipeline or fallback method."""
        if not self.nlp:
            return self._extract_keywords_fallback(job_data)
        
        try:
            # Combine title and description for analysis
            text = job_data.get('title', '') + " " + job_data.get('description', '')
            doc = self.nlp(text)
            
            keywords = set()
            
            # Extract named entities (organizations, locations, etc.)
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'GPE', 'PERSON']:
                    keywords.add(ent.text.lower())
            
            # Extract noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:  # Limit to 3-word phrases
                    keywords.add(chunk.text.lower())
            
            # Extract important single words
            for token in doc:
                if (token.pos_ in ['NOUN', 'ADJ'] and 
                    not token.is_stop and 
                    len(token.text) > 2):
                    keywords.add(token.lemma_.lower())
            
            # Filter out common words and sort by importance
            filtered_keywords = self._filter_keywords(list(keywords), job_data)
            
            return filtered_keywords
            
        except Exception as e:
            logger.error(f"Error in spaCy keyword extraction: {e}")
            return self._extract_keywords_fallback(job_data)
    
    def _extract_keywords_fallback(self, job_data: Dict[str, Any]) -> List[str]:
        """Fallback keyword extraction without spaCy."""
        text = (job_data.get('title', '') + " " + 
                job_data.get('description', '') + " " +
                job_data.get('department', '')).lower()
        
        # Government-specific keywords
        govt_keywords = [
            'government', 'sarkari', 'recruitment', 'vacancy', 'notification',
            'application', 'exam', 'selection', 'job', 'post', 'position'
        ]
        
        # Extract words that appear in government context
        words = re.findall(r'\b\w{3,}\b', text)
        keywords = []
        
        for word in words:
            if (word not in STOP_WORDS and 
                len(word) > 2 and 
                word.isalpha() and
                len(keywords) < 10):
                keywords.append(word)
        
        # Add government-specific terms if found
        for govt_word in govt_keywords:
            if govt_word in text and govt_word not in keywords:
                keywords.append(govt_word)
        
        return keywords[:7]  # Return top 7 keywords
    
    def _filter_keywords(self, keywords: List[str], job_data: Dict[str, Any]) -> List[str]:
        """Filter and rank keywords by relevance."""
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        
        # Score keywords based on occurrence and position
        keyword_scores = {}
        for keyword in keywords:
            score = 0
            
            # Higher score for title keywords
            if keyword in title:
                score += 5
            
            # Score for description keywords
            score += description.count(keyword)
            
            # Bonus for government-related terms
            if any(term in keyword for term in ['government', 'sarkari', 'recruitment']):
                score += 3
            
            keyword_scores[keyword] = score
        
        # Sort by score and return top keywords
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        return [kw[0] for kw in sorted_keywords[:7]]
    
    def _generate_seo_title(self, job_data: Dict[str, Any]) -> str:
        """Generate SEO-optimized title."""
        title = job_data.get('title', '')
        department = job_data.get('department', '')
        year = datetime.now().year
        
        # Start with the job title
        seo_title = title
        
        # Add year for freshness
        if str(year) not in seo_title:
            seo_title += f" {year}"
        
        # Add department if space allows
        if department and len(seo_title) + len(department) + 3 < self.seo_title_max_length:
            seo_title += f" - {department}"
        
        # Add call-to-action if space allows
        if len(seo_title) + 12 < self.seo_title_max_length:
            seo_title += " | Apply Now"
        
        return seo_title
    
    def _generate_seo_description(self, job_data: Dict[str, Any]) -> str:
        """Generate SEO-optimized meta description."""
        title = job_data.get('title', '')
        description = job_data.get('description', '')
        qualification = job_data.get('qualification', '')
        last_date = job_data.get('last_date', '')
        
        # Start with action phrase
        desc_parts = [f"Apply for {title}."]
        
        # Add qualification if available
        if qualification:
            desc_parts.append(f"Eligibility: {qualification[:30]}.")
        
        # Add application deadline
        if last_date:
            desc_parts.append(f"Last date: {last_date}.")
        
        # Add call-to-action
        desc_parts.append("Check details & apply online!")
        
        seo_description = " ".join(desc_parts)
        
        # Truncate if too long
        if len(seo_description) > self.seo_description_max_length:
            seo_description = seo_description[:self.seo_description_max_length-3] + "..."
        
        return seo_description
    
    def _generate_job_schema(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema.org JobPosting structured data."""
        return {
            "@context": "https://schema.org/",
            "@type": "JobPosting",
            "title": job_data.get('title', ''),
            "description": job_data.get('description', job_data.get('title', '')),
            "datePosted": job_data.get('posted_date', datetime.now().isoformat()),
            "employmentType": "FULL_TIME",
            "hiringOrganization": {
                "@type": "Organization",
                "name": job_data.get('department', 'Government of India')
            },
            "jobLocation": {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": job_data.get('location', 'India'),
                    "addressCountry": "IN"
                }
            },
            "qualifications": job_data.get('qualification', ''),
            "validThrough": job_data.get('last_date', '')
        }
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug."""
        return slugify(title)
    
    def _calculate_quality_score(self, job_data: Dict[str, Any], keywords: List[str]) -> float:
        """Calculate SEO quality score."""
        score = 0.0
        
        # Title quality (25 points)
        title = job_data.get('title', '')
        if 10 <= len(title) <= 70:
            score += 25
        elif len(title) > 0:
            score += 15
        
        # Description quality (25 points)
        description = job_data.get('description', '')
        if len(description) > 50:
            score += 25
        elif len(description) > 0:
            score += 15
        
        # Keywords quality (25 points)
        if len(keywords) >= 5:
            score += 25
        elif len(keywords) >= 3:
            score += 20
        elif len(keywords) > 0:
            score += 10
        
        # Data completeness (25 points)
        required_fields = ['title', 'description', 'department', 'qualification']
        completed_fields = sum(1 for field in required_fields if job_data.get(field))
        score += (completed_fields / len(required_fields)) * 25
        
        return round(score, 1)
    
    def _generate_fallback_metadata(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic metadata when NLP processing fails."""
        title = job_data.get('title', 'Government Job')
        year = datetime.now().year
        
        return {
            'seo_title': f"{title} {year} - Apply Online",
            'seo_description': f"Apply for {title}. Check eligibility, notification details and apply online for this government job opportunity.",
            'keywords': ['government job', 'sarkari naukri', 'recruitment', f'{year} jobs'],
            'structured_data': self._generate_job_schema(job_data),
            'slug': self._generate_slug(title),
            'canonical_url': f"/jobs/{self._generate_slug(title)}/",
            'generation_method': 'fallback',
            'quality_score': 50.0
        }


# Global instance for use throughout the application
seo_engine = NLPSEOEngine()


logger = logging.getLogger(__name__)


class NLPSEOEngine:
    """
    NLP-powered SEO automation engine using spaCy.
    
    Implements the specifications from Knowledge.md for automatic
    metadata generation, keyword extraction, and content optimization.
    """
    
    def __init__(self):
        """Initialize the NLP engine with spaCy model."""
        self.nlp = None
        self._load_nlp_model()
        
        # SEO configuration from Knowledge.md
        self.seo_title_max_length = getattr(settings, 'SEO_TITLE_MAX_LENGTH', 60)
        self.seo_description_max_length = getattr(settings, 'SEO_DESCRIPTION_MAX_LENGTH', 160)
        self.seo_keywords_max_count = getattr(settings, 'SEO_KEYWORDS_MAX_COUNT', 7)
    
    def _load_nlp_model(self) -> None:
        """Load spaCy English model with fallback."""
        if not SPACY_AVAILABLE:
            logger.warning("spaCy not available - using basic text processing")
            self.nlp = None
            return
            
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Successfully loaded spaCy English model")
        except OSError:
            try:
                # Fallback to basic English model
                self.nlp = spacy.blank("en")
                logger.warning("Using basic spaCy model - install en_core_web_sm for better performance")
            except Exception as e:
                logger.error(f"Failed to initialize spaCy: {e}")
                self.nlp = None
    
    def generate_seo_metadata(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate SEO-optimized metadata using NLP as per Knowledge.md specifications.
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            Dictionary with SEO metadata including title, description, keywords
            
        Raises:
            ValueError: If required job data is missing
        """
        try:
            if not job_data.get('title'):
                raise ValueError("Job title is required for SEO metadata generation")
            
            logger.info(f"Generating SEO metadata for job: {job_data['title']}")
            
            # Extract keywords using spaCy NLP
            keywords = self._extract_keywords(job_data)
            
            # Generate SEO title (50-60 characters as per Knowledge.md)
            seo_title = self._generate_seo_title(job_data)
            
            # Generate meta description (150-160 characters as per Knowledge.md)
            seo_description = self._generate_seo_description(job_data)
            
            # Generate structured data (schema.org JobPosting)
            structured_data = self._generate_job_schema(job_data)
            
            # Generate URL slug
            slug = self._generate_slug(job_data['title'])
            
            metadata = {
                'seo_title': seo_title[:self.seo_title_max_length],
                'seo_description': seo_description[:self.seo_description_max_length],
                'keywords': keywords[:self.seo_keywords_max_count],
                'structured_data': structured_data,
                'slug': slug,
                'canonical_url': f"/{job_data.get('category', 'jobs')}/{slug}/",
                'generation_method': 'auto_nlp',
                'quality_score': self._calculate_quality_score(job_data, keywords)
            }
            
            logger.info(f"Generated SEO metadata with quality score: {metadata['quality_score']}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error generating SEO metadata: {e}")
            return self._generate_fallback_metadata(job_data)
    
    def _extract_keywords(self, job_data: Dict[str, Any]) -> List[str]:
        """
        Extract keywords using spaCy NLP pipeline as specified in Knowledge.md.
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            List of extracted keywords
        """
        if not self.nlp:
            return self._extract_keywords_fallback(job_data)
        
        try:
            # Combine title and description for analysis
            text = job_data.get('title', '') + " " + job_data.get('description', '')
            doc = self.nlp(text)
            
            keywords = set()
            
            # Extract noun chunks (key phrases)
            for chunk in doc.noun_chunks:
                if len(chunk.text) > 3 and chunk.text.lower() not in STOP_WORDS:
                    keywords.add(chunk.text.lower().strip())
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'GPE', 'WORK_OF_ART'] and len(ent.text) > 3:
                    keywords.add(ent.text.lower().strip())
            
            # Add important domain-specific keywords
            domain_keywords = self._extract_domain_keywords(job_data)
            keywords.update(domain_keywords)
            
            # Sort by relevance and return top keywords
            keyword_list = list(keywords)
            keyword_list.sort(key=lambda x: self._calculate_keyword_relevance(x, job_data), reverse=True)
            
            return keyword_list[:self.seo_keywords_max_count]
            
        except Exception as e:
            logger.error(f"Error in NLP keyword extraction: {e}")
            return self._extract_keywords_fallback(job_data)
    
    def _extract_domain_keywords(self, job_data: Dict[str, Any]) -> List[str]:
        """Extract domain-specific government job keywords."""
        domain_keywords = []
        
        # Add source organization
        if job_data.get('source'):
            domain_keywords.append(job_data['source'].lower())
        
        # Add department if available
        if job_data.get('department'):
            domain_keywords.append(job_data['department'].lower())
        
        # Add qualification keywords
        if job_data.get('qualification'):
            qual_keywords = ['graduate', 'diploma', '12th', '10th', 'degree', 'engineering']
            for keyword in qual_keywords:
                if keyword in job_data['qualification'].lower():
                    domain_keywords.append(keyword)
        
        # Add current year for freshness
        current_year = str(datetime.now().year)
        domain_keywords.append(current_year)
        
        return domain_keywords
    
    def _calculate_keyword_relevance(self, keyword: str, job_data: Dict[str, Any]) -> float:
        """Calculate relevance score for a keyword."""
        score = 0.0
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        
        # Higher score for keywords in title
        if keyword in title:
            score += 3.0
        
        # Medium score for keywords in description
        if keyword in description:
            score += 1.0
        
        # Bonus for government-related terms
        gov_terms = ['government', 'recruitment', 'notification', 'exam', 'result', 'apply']
        if any(term in keyword for term in gov_terms):
            score += 2.0
        
        return score
    
    def _generate_seo_title(self, job_data: Dict[str, Any]) -> str:
        """
        Generate SEO-optimized title following Knowledge.md patterns.
        
        Patterns:
        - {Job Title} {Year} - Apply Online | SarkariBot
        - {Department} {Position} {Year} Notification - {Post Count} Posts
        """
        current_year = datetime.now().year
        title = job_data.get('title', '')
        
        # Pattern 1: Standard job title with year
        if len(title) <= 40:  # Leave room for suffix
            seo_title = f"{title} {current_year} - Apply Online | SarkariBot"
        else:
            # Truncate title if too long
            truncated_title = title[:35] + "..."
            seo_title = f"{truncated_title} {current_year} - SarkariBot"
        
        return seo_title
    
    def _generate_seo_description(self, job_data: Dict[str, Any]) -> str:
        """
        Generate SEO meta description following Knowledge.md patterns.
        
        Pattern: Include key details: job title, last date, number of posts
        """
        title = job_data.get('title', '')
        last_date = job_data.get('application_end_date') or job_data.get('last_date', 'TBD')
        total_posts = job_data.get('total_posts', '')
        current_year = datetime.now().year
        
        # Format last date
        if last_date and last_date != 'TBD':
            try:
                if isinstance(last_date, str):
                    date_obj = datetime.strptime(last_date, '%Y-%m-%d')
                else:
                    date_obj = last_date
                formatted_date = date_obj.strftime('%d %B %Y')
            except:
                formatted_date = str(last_date)
        else:
            formatted_date = 'TBD'
        
        # Build description
        description_parts = [f"Apply for {title}."]
        
        if formatted_date != 'TBD':
            description_parts.append(f"Last date: {formatted_date}.")
        
        if total_posts:
            description_parts.append(f"{total_posts} posts available.")
        
        description_parts.append(f"Eligibility, syllabus, and direct apply link. {current_year} government job.")
        
        description = " ".join(description_parts)
        return description
    
    def _generate_job_schema(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate JSON-LD structured data for JobPosting schema.org as per Knowledge.md.
        """
        current_date = datetime.now().isoformat()
        
        schema = {
            "@context": "https://schema.org",
            "@type": "JobPosting",
            "title": job_data.get('title', ''),
            "description": job_data.get('description', ''),
            "datePosted": job_data.get('notification_date') or current_date,
            "employmentType": "FULL_TIME",
            "jobLocationType": "TELECOMMUTE",
            "hiringOrganization": {
                "@type": "Organization",
                "name": job_data.get('source', 'Government of India'),
                "url": job_data.get('source_url', 'https://sarkaribot.com')
            },
            "jobLocation": {
                "@type": "Place",
                "addressLocality": "India",
                "addressCountry": "IN"
            }
        }
        
        # Add optional fields
        if job_data.get('application_end_date'):
            schema["validThrough"] = job_data['application_end_date']
        
        if job_data.get('total_posts'):
            schema["totalJobOpenings"] = job_data['total_posts']
        
        if job_data.get('qualification'):
            schema["educationRequirements"] = job_data['qualification']
        
        if job_data.get('min_age') or job_data.get('max_age'):
            age_req = []
            if job_data.get('min_age'):
                age_req.append(f"Minimum age: {job_data['min_age']}")
            if job_data.get('max_age'):
                age_req.append(f"Maximum age: {job_data['max_age']}")
            schema["experienceRequirements"] = ", ".join(age_req)
        
        return schema
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from job title."""
        # Clean title and create slug
        cleaned_title = re.sub(r'[^\w\s-]', '', title)
        slug = slugify(cleaned_title)
        
        # Ensure reasonable length
        if len(slug) > 50:
            slug = slug[:50].rstrip('-')
        
        return slug
    
    def _calculate_quality_score(self, job_data: Dict[str, Any], keywords: List[str]) -> float:
        """Calculate content quality score (0-100)."""
        score = 0.0
        
        # Title quality (20 points)
        if job_data.get('title'):
            title_len = len(job_data['title'])
            if 30 <= title_len <= 100:
                score += 20
            elif title_len > 15:
                score += 10
        
        # Description quality (30 points)
        if job_data.get('description'):
            desc_len = len(job_data['description'])
            if desc_len > 200:
                score += 30
            elif desc_len > 100:
                score += 20
            elif desc_len > 50:
                score += 10
        
        # Required fields presence (30 points)
        required_fields = ['source', 'category', 'application_end_date']
        filled_required = sum(1 for field in required_fields if job_data.get(field))
        score += (filled_required / len(required_fields)) * 30
        
        # Keywords quality (20 points)
        if keywords:
            if len(keywords) >= 5:
                score += 20
            elif len(keywords) >= 3:
                score += 15
            elif len(keywords) >= 1:
                score += 10
        
        return min(score, 100.0)
    
    def _extract_keywords_fallback(self, job_data: Dict[str, Any]) -> List[str]:
        """Fallback keyword extraction without NLP."""
        keywords = []
        
        # Simple keyword extraction from title
        title = job_data.get('title', '')
        title_words = [word.lower() for word in title.split() if len(word) > 3]
        keywords.extend(title_words[:3])
        
        # Add domain keywords
        keywords.extend(self._extract_domain_keywords(job_data))
        
        return keywords[:self.seo_keywords_max_count]
    
    def _generate_fallback_metadata(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic SEO metadata without NLP."""
        title = job_data.get('title', 'Government Job')
        current_year = datetime.now().year
        
        return {
            'seo_title': f"{title} {current_year} - SarkariBot",
            'seo_description': f"Apply for {title}. Latest government job notification.",
            'keywords': self._extract_keywords_fallback(job_data),
            'structured_data': self._generate_job_schema(job_data),
            'slug': self._generate_slug(title),
            'canonical_url': f"/jobs/{self._generate_slug(title)}/",
            'generation_method': 'fallback',
            'quality_score': 50.0
        }


# Global instance for use throughout the application
seo_engine = NLPSEOEngine()


class SEOEngine:
    """
    NLP-powered SEO automation engine.
    
    Uses spaCy for natural language processing to generate
    SEO-optimized metadata, keywords, and structured data.
    """
    
    def __init__(self):
        """Initialize the SEO engine with spaCy model."""
        try:
            # Load spaCy English model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except IOError:
            logger.error("spaCy model 'en_core_web_sm' not found. Installing...")
            self._install_spacy_model()
            self.nlp = spacy.load("en_core_web_sm")
        
        # SEO configuration
        self.max_title_length = 60
        self.max_description_length = 160
        self.max_keywords = 8
        
        # Government job-specific terms for better keyword extraction
        self.government_terms = {
            'organizations': [
                'SSC', 'UPSC', 'RRB', 'IBPS', 'SBI', 'LIC', 'DRDO', 'ISRO',
                'ONGC', 'BHEL', 'SAIL', 'NTPC', 'BSNL', 'NHM', 'AIIMS',
                'CRPF', 'BSF', 'CISF', 'ITBP', 'SSB', 'NSG', 'SPG'
            ],
            'positions': [
                'officer', 'clerk', 'assistant', 'manager', 'engineer', 'doctor',
                'nurse', 'teacher', 'inspector', 'constable', 'driver', 'guard',
                'technician', 'specialist', 'analyst', 'consultant', 'advisor'
            ],
            'qualifications': [
                'graduate', 'postgraduate', 'diploma', 'ITI', 'B.Tech', 'M.Tech',
                'MBBS', 'B.Ed', 'M.Ed', 'CA', 'CS', 'CMA', 'LLB', 'MBA'
            ],
            'exam_types': [
                'written exam', 'interview', 'skill test', 'physical test',
                'medical exam', 'document verification', 'typing test'
            ]
        }
        
        # Add custom entities to spaCy pipeline
        self._add_custom_entities()
    
    def _install_spacy_model(self):
        """Install spaCy English model if not available."""
        import subprocess
        import sys
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "spacy", "download", "en_core_web_sm"
            ])
            logger.info("spaCy model installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install spaCy model: {e}")
            raise
    
    def _add_custom_entities(self):
        """Add custom entity recognition for government job terms."""
        # Add custom patterns for better entity recognition
        from spacy.matcher import Matcher
        
        self.matcher = Matcher(self.nlp.vocab)
        
        # Add patterns for government organizations
        org_patterns = []
        for org in self.government_terms['organizations']:
            org_patterns.append([{"LOWER": org.lower()}])
        
        self.matcher.add("GOVT_ORG", org_patterns)
        
        # Add patterns for job positions
        position_patterns = []
        for pos in self.government_terms['positions']:
            position_patterns.append([{"LOWER": pos.lower()}])
        
        self.matcher.add("JOB_POSITION", position_patterns)
    
    def generate_seo_metadata(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive SEO metadata for a job posting.
        
        Args:
            job_data: Dictionary containing job posting data
            
        Returns:
            Dictionary with SEO metadata including title, description, keywords, etc.
        """
        logger.debug(f"Generating SEO metadata for: {job_data.get('title', 'Unknown')}")
        
        try:
            # Extract and process text content
            title = job_data.get('title', '')
            description = job_data.get('description', '')
            department = job_data.get('department', '')
            
            # Process text with spaCy
            doc = self.nlp(f"{title} {description} {department}")
            
            # Generate components
            seo_title = self._generate_seo_title(job_data, doc)
            seo_description = self._generate_seo_description(job_data, doc)
            keywords = self._extract_keywords(doc, job_data)
            structured_data = self._generate_structured_data(job_data)
            
            # Generate additional SEO elements
            meta_tags = self._generate_meta_tags(job_data, keywords)
            og_tags = self._generate_open_graph_tags(job_data, seo_title, seo_description)
            
            return {
                'seo_title': seo_title,
                'seo_description': seo_description,
                'keywords': keywords,
                'structured_data': structured_data,
                'meta_tags': meta_tags,
                'open_graph_tags': og_tags,
                'canonical_url': self._generate_canonical_url(job_data),
                'breadcrumbs': self._generate_breadcrumbs(job_data),
                'last_modified': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error generating SEO metadata: {e}")
            return self._fallback_seo_metadata(job_data)
    
    def _generate_seo_title(self, job_data: Dict[str, Any], doc: spacy.Doc) -> str:
        """
        Generate SEO-optimized title.
        
        Args:
            job_data: Job posting data
            doc: spaCy processed document
            
        Returns:
            SEO-optimized title
        """
        title = job_data.get('title', '')
        department = job_data.get('department', '')
        current_year = datetime.now().year
        
        # Clean and optimize title
        optimized_title = self._clean_title(title)
        
        # Add year for freshness
        if str(current_year) not in optimized_title:
            optimized_title = f"{optimized_title} {current_year}"
        
        # Add call-to-action
        if 'apply' not in optimized_title.lower():
            optimized_title = f"{optimized_title} - Apply Online"
        
        # Add brand
        if 'sarkaribot' not in optimized_title.lower():
            optimized_title = f"{optimized_title} | SarkariBot"
        
        # Ensure length limit
        if len(optimized_title) > self.max_title_length:
            # Truncate while preserving important terms
            optimized_title = self._truncate_title(optimized_title, self.max_title_length)
        
        return optimized_title
    
    def _generate_seo_description(self, job_data: Dict[str, Any], doc: spacy.Doc) -> str:
        """
        Generate SEO-optimized meta description.
        
        Args:
            job_data: Job posting data
            doc: spaCy processed document
            
        Returns:
            SEO-optimized meta description
        """
        title = job_data.get('title', '')
        department = job_data.get('department', '')
        posts = job_data.get('total_posts', '')
        last_date = job_data.get('application_end_date', '')
        qualification = job_data.get('qualification', '')
        
        # Build description components
        components = []
        
        # Main job info
        if posts:
            components.append(f"Apply for {posts} {title} posts")
        else:
            components.append(f"Apply for {title}")
        
        # Department
        if department:
            components.append(f"at {department}")
        
        # Last date
        if last_date:
            if isinstance(last_date, (date, datetime)):
                last_date_str = last_date.strftime('%d %b %Y')
            else:
                last_date_str = str(last_date)
            components.append(f"Last date: {last_date_str}")
        
        # Qualification
        if qualification:
            qual_short = self._shorten_qualification(qualification)
            components.append(f"Eligibility: {qual_short}")
        
        # Call to action
        components.append("Check eligibility, syllabus & apply online")
        
        # Join components
        description = '. '.join(components)
        
        # Add current year for freshness
        current_year = datetime.now().year
        if str(current_year) not in description:
            description = f"{description}. Latest {current_year} government jobs"
        
        # Ensure length limit
        if len(description) > self.max_description_length:
            description = self._truncate_description(description, self.max_description_length)
        
        return description
    
    def _extract_keywords(self, doc: spacy.Doc, job_data: Dict[str, Any]) -> List[str]:
        """
        Extract relevant keywords using NLP.
        
        Args:
            doc: spaCy processed document
            job_data: Job posting data
            
        Returns:
            List of relevant keywords
        """
        keywords = []
        
        # Extract named entities
        entities = [ent.text.lower() for ent in doc.ents 
                   if ent.label_ in ['ORG', 'PERSON', 'GPE', 'EVENT']]
        keywords.extend(entities)
        
        # Extract noun chunks (important phrases)
        noun_chunks = [chunk.text.lower() for chunk in doc.noun_chunks 
                      if len(chunk.text) > 3 and chunk.text.lower() not in STOP_WORDS]
        keywords.extend(noun_chunks)
        
        # Add government-specific terms found in content
        text_lower = doc.text.lower()
        for category, terms in self.government_terms.items():
            for term in terms:
                if term.lower() in text_lower:
                    keywords.append(term.lower())
        
        # Add manual keywords based on job data
        manual_keywords = self._get_manual_keywords(job_data)
        keywords.extend(manual_keywords)
        
        # Clean and filter keywords
        keywords = self._clean_keywords(keywords)
        
        # Count frequency and select top keywords
        keyword_counts = Counter(keywords)
        top_keywords = [kw for kw, count in keyword_counts.most_common(self.max_keywords)]
        
        return top_keywords
    
    def _get_manual_keywords(self, job_data: Dict[str, Any]) -> List[str]:
        """Get manually curated keywords based on job data."""
        keywords = []
        
        # Always include generic government job terms
        keywords.extend(['government job', 'sarkari naukri', 'government recruitment'])
        
        # Add year
        current_year = datetime.now().year
        keywords.append(f'government jobs {current_year}')
        
        # Add department/organization
        department = job_data.get('department', '')
        if department:
            keywords.append(department.lower())
            keywords.append(f'{department.lower()} recruitment')
        
        # Add state if available
        location = job_data.get('location', '')
        if location:
            keywords.append(location.lower())
        
        # Add qualification level
        qualification = job_data.get('qualification', '')
        if qualification:
            if any(term in qualification.lower() for term in ['graduate', 'degree']):
                keywords.append('graduate jobs')
            if '12th' in qualification or 'intermediate' in qualification.lower():
                keywords.append('12th pass jobs')
            if '10th' in qualification:
                keywords.append('10th pass jobs')
        
        return keywords
    
    def _clean_keywords(self, keywords: List[str]) -> List[str]:
        """Clean and normalize keywords."""
        cleaned = []
        
        for keyword in keywords:
            # Convert to lowercase and strip
            kw = keyword.lower().strip()
            
            # Skip if too short or is stop word
            if len(kw) < 3 or kw in STOP_WORDS:
                continue
            
            # Remove special characters except spaces and hyphens
            kw = re.sub(r'[^\w\s-]', '', kw)
            
            # Skip if empty after cleaning
            if not kw.strip():
                continue
            
            # Skip duplicates
            if kw not in cleaned:
                cleaned.append(kw)
        
        return cleaned
    
    def _generate_structured_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate JSON-LD structured data for job posting.
        
        Args:
            job_data: Job posting data
            
        Returns:
            Dictionary containing structured data
        """
        structured_data = {
            "@context": "https://schema.org/",
            "@type": "JobPosting",
            "title": job_data.get('title', ''),
            "description": job_data.get('description', ''),
            "identifier": {
                "@type": "PropertyValue",
                "name": "Job ID",
                "value": str(job_data.get('id', ''))
            },
            "datePosted": self._format_date(job_data.get('notification_date')),
            "validThrough": self._format_date(job_data.get('application_end_date')),
            "employmentType": "FULL_TIME",
            "hiringOrganization": {
                "@type": "Organization",
                "name": job_data.get('department', 'Government of India'),
                "sameAs": job_data.get('source', {}).get('base_url', '')
            },
            "jobLocation": {
                "@type": "Place",
                "addressLocality": job_data.get('location', 'India'),
                "addressCountry": "IN"
            },
            "baseSalary": self._format_salary(job_data),
            "educationRequirements": job_data.get('qualification', ''),
            "experienceRequirements": "As per notification",
            "skills": self._extract_skills(job_data.get('description', '')),
            "url": job_data.get('source_url', ''),
            "applicationContact": {
                "@type": "ContactPoint",
                "contactType": "Application Information",
                "url": job_data.get('application_link', '')
            }
        }
        
        # Add age requirements if available
        min_age = job_data.get('min_age')
        max_age = job_data.get('max_age')
        if min_age or max_age:
            age_req = f"Age: {min_age or 'N/A'} to {max_age or 'N/A'} years"
            structured_data["qualifications"] = age_req
        
        # Add number of positions if available
        if job_data.get('total_posts'):
            structured_data["totalJobOpenings"] = job_data['total_posts']
        
        return structured_data
    
    def _format_date(self, date_value: Any) -> Optional[str]:
        """Format date for structured data."""
        if not date_value:
            return None
        
        if isinstance(date_value, (date, datetime)):
            return date_value.strftime('%Y-%m-%d')
        
        # Try to parse string date
        try:
            parsed_date = datetime.strptime(str(date_value), '%Y-%m-%d')
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    def _format_salary(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format salary information for structured data."""
        salary_min = job_data.get('salary_min')
        salary_max = job_data.get('salary_max')
        
        if not (salary_min or salary_max):
            return None
        
        salary_data = {
            "@type": "MonetaryAmount",
            "currency": "INR",
            "value": {
                "@type": "QuantitativeValue"
            }
        }
        
        if salary_min and salary_max:
            salary_data["value"]["minValue"] = salary_min
            salary_data["value"]["maxValue"] = salary_max
        elif salary_min:
            salary_data["value"]["value"] = salary_min
        elif salary_max:
            salary_data["value"]["value"] = salary_max
        
        return salary_data
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description."""
        if not description:
            return []
        
        # Common government job skills
        skill_patterns = [
            r'computer\s+knowledge',
            r'typing\s+speed',
            r'ms\s+office',
            r'data\s+entry',
            r'communication\s+skills',
            r'leadership',
            r'teamwork',
            r'problem\s+solving',
            r'analytical\s+skills',
            r'time\s+management'
        ]
        
        skills = []
        description_lower = description.lower()
        
        for pattern in skill_patterns:
            if re.search(pattern, description_lower):
                skill = pattern.replace(r'\s+', ' ').replace('\\', '')
                skills.append(skill.title())
        
        return skills[:5]  # Limit to 5 skills
    
    def _generate_meta_tags(self, job_data: Dict[str, Any], keywords: List[str]) -> Dict[str, str]:
        """Generate additional meta tags."""
        return {
            'robots': 'index, follow',
            'keywords': ', '.join(keywords),
            'author': 'SarkariBot',
            'language': 'en-IN',
            'geo.region': 'IN',
            'geo.country': 'India',
            'article:author': 'SarkariBot',
            'article:section': 'Government Jobs',
            'article:tag': ', '.join(keywords[:5])
        }
    
    def _generate_open_graph_tags(self, job_data: Dict[str, Any], title: str, description: str) -> Dict[str, str]:
        """Generate Open Graph meta tags for social media."""
        return {
            'og:type': 'article',
            'og:title': title,
            'og:description': description,
            'og:url': job_data.get('source_url', ''),
            'og:site_name': 'SarkariBot',
            'og:locale': 'en_IN',
            'twitter:card': 'summary',
            'twitter:title': title,
            'twitter:description': description,
            'twitter:site': '@SarkariBot'
        }
    
    def _generate_canonical_url(self, job_data: Dict[str, Any]) -> str:
        """Generate canonical URL for the job posting."""
        slug = job_data.get('slug', '')
        if slug:
            return f"https://sarkaribot.com/jobs/{slug}"
        return job_data.get('source_url', '')
    
    def _generate_breadcrumbs(self, job_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate breadcrumb navigation data."""
        breadcrumbs = [
            {"name": "Home", "url": "/"},
            {"name": "Government Jobs", "url": "/jobs/"},
        ]
        
        # Add category if available
        category = job_data.get('category', {})
        if category:
            category_name = category.get('name', 'Latest Jobs')
            category_slug = category.get('slug', 'latest-jobs')
            breadcrumbs.append({
                "name": category_name,
                "url": f"/jobs/category/{category_slug}/"
            })
        
        # Add current job
        title = job_data.get('title', 'Job Details')
        breadcrumbs.append({
            "name": title[:50] + "..." if len(title) > 50 else title,
            "url": f"/jobs/{job_data.get('slug', '')}"
        })
        
        return breadcrumbs
    
    def _clean_title(self, title: str) -> str:
        """Clean and optimize title text."""
        if not title:
            return ''
        
        # Remove common prefixes that don't add SEO value
        prefixes_to_remove = [
            'recruitment for', 'recruitment of', 'notification for',
            'advertisement for', 'vacancy for', 'apply for'
        ]
        
        title_lower = title.lower()
        for prefix in prefixes_to_remove:
            if title_lower.startswith(prefix):
                title = title[len(prefix):].strip()
                break
        
        # Proper capitalization
        title = ' '.join(word.capitalize() for word in title.split())
        
        return title
    
    def _truncate_title(self, title: str, max_length: int) -> str:
        """Truncate title while preserving important terms."""
        if len(title) <= max_length:
            return title
        
        # Try to truncate at word boundary
        truncated = title[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:  # If we can keep 80% of the content
            return truncated[:last_space] + '...'
        
        return truncated[:max_length-3] + '...'
    
    def _truncate_description(self, description: str, max_length: int) -> str:
        """Truncate description while preserving meaning."""
        if len(description) <= max_length:
            return description
        
        # Try to end at sentence boundary
        truncated = description[:max_length]
        last_period = truncated.rfind('.')
        
        if last_period > max_length * 0.7:  # If we can keep 70% of the content
            return truncated[:last_period + 1]
        
        # Try to end at word boundary
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:
            return truncated[:last_space] + '...'
        
        return truncated[:max_length-3] + '...'
    
    def _shorten_qualification(self, qualification: str) -> str:
        """Create a shortened version of qualification for meta description."""
        if not qualification:
            return ''
        
        # Common abbreviations
        abbreviations = {
            'bachelor': "Bachelor's",
            'master': "Master's",
            'graduation': 'Graduate',
            'post graduation': 'Postgraduate',
            'intermediate': '12th',
            'higher secondary': '12th',
            'senior secondary': '12th',
            'matriculation': '10th'
        }
        
        qual_lower = qualification.lower()
        for full_term, abbrev in abbreviations.items():
            if full_term in qual_lower:
                return abbrev
        
        # If no abbreviation found, return first 30 characters
        return qualification[:30] + '...' if len(qualification) > 30 else qualification
    
    def _fallback_seo_metadata(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic SEO metadata when NLP processing fails."""
        title = job_data.get('title', 'Government Job')
        current_year = datetime.now().year
        
        return {
            'seo_title': f"{title} {current_year} - Apply Online | SarkariBot",
            'seo_description': f"Apply for {title}. Check eligibility, last date & apply online. Latest {current_year} government job notification.",
            'keywords': ['government job', 'sarkari naukri', f'{current_year} jobs'],
            'structured_data': {
                "@context": "https://schema.org/",
                "@type": "JobPosting",
                "title": title,
                "description": job_data.get('description', ''),
                "employmentType": "FULL_TIME"
            },
            'meta_tags': {'robots': 'index, follow'},
            'open_graph_tags': {
                'og:type': 'article',
                'og:title': title,
                'og:site_name': 'SarkariBot'
            },
            'canonical_url': job_data.get('source_url', ''),
            'breadcrumbs': [{"name": "Home", "url": "/"}],
            'last_modified': datetime.now().isoformat(),
        }
