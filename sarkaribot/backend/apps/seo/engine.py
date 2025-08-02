"""
SEO Automation Engine for SarkariBot.

Implements NLP-powered metadata generation using spaCy for keyword extraction
and content analysis according to Knowledge.md specifications.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.utils.text import slugify
from django.utils.html import strip_tags
from collections import Counter

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
        'further', 'then', 'once', 'application', 'notification', 'recruitment',
        'examination', 'apply'
    }

logger = logging.getLogger(__name__)


class NLPSEOEngine:
    """
    NLP-powered SEO automation engine using spaCy with enhanced fallback.

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
            logger.warning(
                "Could not load 'en_core_web_sm' model. "
                "Falling back to basic keyword extraction. "
                "For better performance, run 'python -m spacy download en_core_web_sm'"
            )
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

            # Ensure lengths are within limits
            if len(seo_title) > self.seo_title_max_length:
                seo_title = seo_title[:self.seo_title_max_length-3] + "..."

            if len(seo_description) > self.seo_description_max_length:
                seo_description = seo_description[:self.seo_description_max_length-3] + "..."

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
                'canonical_url': f"/jobs/{slug}/",
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
                    not token.is_punct and 
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

        # Remove punctuation and split into words
        text = re.sub(r'[^\w\s]', '', text)
        words = [word for word in text.split() if word not in STOP_WORDS and len(word) > 3]

        # Get most common words
        word_counts = Counter(words)
        
        # Add government-specific keywords
        govt_keywords = ['government', 'sarkari', 'recruitment', 'exam', 'notification', 
                        'apply', 'eligibility', 'vacancy', 'job', 'post']
        
        keywords = []
        for word, count in word_counts.most_common(10):
            if word not in keywords:
                keywords.append(word)
        
        # Ensure government keywords are included
        for govt_word in govt_keywords:
            if govt_word in text and govt_word not in keywords:
                keywords.append(govt_word)
        
        return keywords[:self.seo_keywords_max_count]

    def _filter_keywords(self, keywords: List[str], job_data: Dict[str, Any]) -> List[str]:
        """Filter and rank keywords by relevance."""
        # Remove very common words
        filtered = [k for k in keywords if k not in STOP_WORDS and len(k) > 2]
        
        # Sort by relevance (prioritize job-specific terms)
        govt_terms = ['government', 'sarkari', 'recruitment', 'notification', 'exam']
        job_specific = [k for k in filtered if any(term in k for term in govt_terms)]
        others = [k for k in filtered if k not in job_specific]
        
        return job_specific + others[:self.seo_keywords_max_count]

    def _generate_seo_title(self, job_data: Dict[str, Any]) -> str:
        """Generate SEO-optimized title."""
        title = job_data.get('title', 'Government Job')
        current_year = datetime.now().year
        
        # Add year if not present
        if str(current_year) not in title:
            title += f" {current_year}"
        
        # Add call-to-action
        if len(title) < 50:
            title += " - Apply Online"
        
        return title

    def _generate_seo_description(self, job_data: Dict[str, Any]) -> str:
        """Generate SEO-optimized meta description."""
        title = job_data.get('title', 'Government Job')
        department = job_data.get('department', '')
        total_posts = job_data.get('total_posts')
        
        description = f"Apply for {title}"
        
        if total_posts:
            description += f" - {total_posts} posts"
        
        if department:
            description += f" in {department}"
        
        description += ". Check eligibility, last date, and apply online for this government job opportunity."
        
        return description

    def _generate_job_schema(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema.org JobPosting structured data."""
        schema = {
            "@context": "https://schema.org/",
            "@type": "JobPosting",
            "title": job_data.get('title', ''),
            "description": job_data.get('description', ''),
            "employmentType": "FULL_TIME",
            "industry": "Government",
        }
        
        if job_data.get('department'):
            schema["hiringOrganization"] = {
                "@type": "Organization",
                "name": job_data['department']
            }
        
        if job_data.get('total_posts'):
            schema["totalJobOpenings"] = job_data['total_posts']
        
        if job_data.get('application_end_date'):
            schema["validThrough"] = job_data['application_end_date']
        
        return schema

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug."""
        return slugify(title)

    def _calculate_quality_score(self, job_data: Dict[str, Any], keywords: List[str]) -> float:
        """Calculate metadata quality score."""
        score = 50.0  # Base score
        
        if job_data.get('description'):
            score += 20.0
        
        if len(keywords) >= 5:
            score += 15.0
        
        if job_data.get('department'):
            score += 10.0
        
        if job_data.get('total_posts'):
            score += 5.0
        
        return min(score, 100.0)

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
# This ensures consistent class naming across the codebase
seo_engine = NLPSEOEngine()

# Legacy alias for backward compatibility
SEOEngine = NLPSEOEngine
