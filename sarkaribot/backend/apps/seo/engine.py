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

# Import the enhanced engine as fallback
try:
    from .enhanced_engine import EnhancedSEOEngine, seo_engine as enhanced_engine
    ENHANCED_ENGINE_AVAILABLE = True
except ImportError:
    ENHANCED_ENGINE_AVAILABLE = False
    enhanced_engine = None

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
        self.enhanced_engine = enhanced_engine
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
            # If spaCy is not available, use enhanced engine fallback
            if not self.nlp and ENHANCED_ENGINE_AVAILABLE and self.enhanced_engine:
                logger.info("Using enhanced engine fallback for SEO generation")
                return self._generate_with_enhanced_engine(job_data)

            # Continue with spaCy implementation if available
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

    def _generate_with_enhanced_engine(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata using enhanced engine fallback."""
        try:
            if not self.enhanced_engine:
                return self._generate_fallback_metadata(job_data)

            # Generate SEO title
            seo_title = self.enhanced_engine.generate_seo_title(
                job_data.get('title', ''),
                job_data.get('department', ''),
                str(datetime.now().year)
            )

            # Generate meta description
            seo_description = self.enhanced_engine.generate_meta_description(
                job_data.get('title', ''),
                job_data.get('total_posts', 0),
                job_data.get('application_end_date', ''),
                job_data.get('department', '')
            )

            # Extract keywords
            keywords = self.enhanced_engine.extract_keywords(
                f"{job_data.get('title', '')} {job_data.get('description', '')}"
            )

            # Generate structured data
            structured_data = self.enhanced_engine.generate_structured_data(job_data)

            return {
                'seo_title': seo_title,
                'seo_description': seo_description,
                'keywords': keywords,
                'structured_data': structured_data,
                'slug': slugify(job_data.get('title', '')),
                'canonical_url': f"/jobs/{slugify(job_data.get('title', ''))}/",
                'generation_method': 'enhanced_engine',
                'quality_score': 85.0
            }
        except Exception as e:
            logger.error(f"Enhanced engine fallback failed: {e}")
            return self._generate_fallback_metadata(job_data)


# Global instance for use throughout the application
seo_engine = NLPSEOEngine()
