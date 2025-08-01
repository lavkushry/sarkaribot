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
        """
        Generate comprehensive schema.org JobPosting structured data.
        
        Implements full JobPosting schema according to schema.org specifications
        for optimal search engine visibility and rich results.
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            Complete schema.org JobPosting structured data
        """
        # Base schema structure
        schema = {
            "@context": "https://schema.org/",
            "@type": "JobPosting",
            "headline": job_data.get('title', ''),
            "title": job_data.get('title', ''),
            "description": self._clean_html_for_schema(job_data.get('description', job_data.get('title', ''))),
            "datePosted": job_data.get('posted_date', datetime.now().isoformat()),
            "employmentType": ["FULL_TIME", "PERMANENT"],
            "jobLocationType": "LOCATION_TYPE_UNSPECIFIED",
            "industry": "Government",
            "occupationalCategory": "Government Jobs",
        }
        
        # Hiring Organization (Enhanced)
        organization_name = job_data.get('department') or job_data.get('source_name', 'Government of India')
        schema["hiringOrganization"] = {
            "@type": "GovernmentOrganization",
            "name": organization_name,
            "url": job_data.get('source_url', ''),
            "logo": job_data.get('organization_logo', ''),
            "description": f"{organization_name} - Government of India",
            "address": {
                "@type": "PostalAddress",
                "addressCountry": "IN",
                "addressLocality": "India"
            }
        }
        
        # Job Location (Enhanced)
        schema["jobLocation"] = {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": job_data.get('location', 'India'),
                "addressRegion": job_data.get('state', ''),
                "addressCountry": "IN"
            }
        }
        
        # Base Salary (if available)
        if job_data.get('salary_min') or job_data.get('salary_max'):
            salary_data = {
                "@type": "MonetaryAmount",
                "currency": "INR"
            }
            
            if job_data.get('salary_min') and job_data.get('salary_max'):
                salary_data["value"] = {
                    "@type": "QuantitativeValue",
                    "minValue": job_data.get('salary_min'),
                    "maxValue": job_data.get('salary_max'),
                    "unitText": "MONTH"
                }
            elif job_data.get('salary_min'):
                salary_data["value"] = {
                    "@type": "QuantitativeValue",
                    "minValue": job_data.get('salary_min'),
                    "unitText": "MONTH"
                }
            elif job_data.get('salary_max'):
                salary_data["value"] = {
                    "@type": "QuantitativeValue",
                    "maxValue": job_data.get('salary_max'),
                    "unitText": "MONTH"
                }
            
            schema["baseSalary"] = salary_data
        
        # Education Requirements
        if job_data.get('qualification'):
            schema["educationRequirements"] = {
                "@type": "EducationalOccupationalCredential",
                "credentialCategory": "degree",
                "educationalLevel": job_data.get('qualification', '')
            }
        
        # Experience Requirements
        if job_data.get('experience'):
            schema["experienceRequirements"] = {
                "@type": "OccupationalExperienceRequirements",
                "monthsOfExperience": job_data.get('experience_months', 0)
            }
        
        # Application Instructions
        application_instructions = []
        if job_data.get('application_link'):
            application_instructions.append(f"Apply online at: {job_data.get('application_link')}")
        if job_data.get('application_fee'):
            application_instructions.append(f"Application fee: ₹{job_data.get('application_fee')}")
        
        if application_instructions:
            schema["applicationContact"] = {
                "@type": "ContactPoint",
                "description": " | ".join(application_instructions)
            }
        
        # Important Dates
        if job_data.get('last_date'):
            schema["validThrough"] = job_data.get('last_date')
        
        if job_data.get('application_start_date'):
            schema["applicationDeadline"] = job_data.get('last_date', '')
        
        # Job Benefits
        benefits = []
        if job_data.get('total_posts'):
            benefits.append(f"{job_data.get('total_posts')} positions available")
        
        if benefits:
            schema["jobBenefits"] = benefits
        
        # Qualifications summary
        qualifications = []
        if job_data.get('min_age') or job_data.get('max_age'):
            age_req = "Age: "
            if job_data.get('min_age'):
                age_req += f"{job_data.get('min_age')} years minimum"
            if job_data.get('max_age'):
                if job_data.get('min_age'):
                    age_req += f" to {job_data.get('max_age')} years maximum"
                else:
                    age_req += f"{job_data.get('max_age')} years maximum"
            qualifications.append(age_req)
        
        if job_data.get('qualification'):
            qualifications.append(f"Education: {job_data.get('qualification')}")
        
        if qualifications:
            schema["qualifications"] = " | ".join(qualifications)
        
        # Additional metadata
        schema["identifier"] = {
            "@type": "PropertyValue",
            "name": "Job ID",
            "value": str(job_data.get('id', ''))
        }
        
        # Keywords for better SEO
        if job_data.get('keywords'):
            schema["keywords"] = job_data.get('keywords')
        
        # Special requirements for government jobs
        schema["specialCommitments"] = ["Government Service", "Public Sector"]
        
        # URL and identifier
        if job_data.get('slug'):
            schema["url"] = f"/jobs/{job_data.get('slug')}/"
        
        return schema
    
    def _clean_html_for_schema(self, text: str) -> str:
        """Clean HTML content for use in structured data."""
        if not text:
            return ""
        
        # Remove HTML tags and decode entities
        import re
        from html import unescape
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', ' ', text)
        # Decode HTML entities
        clean_text = unescape(clean_text)
        # Normalize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text[:500]  # Limit length for schema

    def generate_open_graph_metadata(self, job_data: Dict[str, Any], request_url: str = "") -> Dict[str, Any]:
        """
        Generate OpenGraph metadata for social media sharing.
        
        Args:
            job_data: Dictionary containing job information
            request_url: Full URL of the job page
            
        Returns:
            Dictionary with OpenGraph meta tags
        """
        try:
            title = job_data.get('title', '')
            description = self._clean_html_for_schema(job_data.get('description', ''))
            
            # Generate OG title (95 chars max)
            og_title = title
            if len(og_title) > 95:
                og_title = og_title[:92] + "..."
            
            # Generate OG description (300 chars max)
            og_description = description
            if not og_description:
                og_description = f"Apply for {title}. Check eligibility, notification details and apply online."
            
            if len(og_description) > 300:
                og_description = og_description[:297] + "..."
            
            # Generate OG image URL (placeholder for now)
            og_image = job_data.get('image_url', '/static/images/sarkaribot-job-default.jpg')
            
            og_metadata = {
                'og:type': 'article',
                'og:title': og_title,
                'og:description': og_description,
                'og:image': og_image,
                'og:url': request_url,
                'og:site_name': 'SarkariBot - Government Jobs Portal',
                'og:locale': 'en_IN',
                'article:author': job_data.get('department', 'Government of India'),
                'article:published_time': job_data.get('posted_date', datetime.now().isoformat()),
                'article:section': job_data.get('category', 'Government Jobs'),
                'article:tag': job_data.get('keywords', ''),
            }
            
            # Add job-specific OG tags
            if job_data.get('total_posts'):
                og_metadata['job:posts_available'] = str(job_data.get('total_posts'))
            
            if job_data.get('last_date'):
                og_metadata['job:application_deadline'] = job_data.get('last_date')
            
            if job_data.get('salary_min') or job_data.get('salary_max'):
                salary_range = []
                if job_data.get('salary_min'):
                    salary_range.append(f"₹{job_data.get('salary_min'):,}")
                if job_data.get('salary_max'):
                    salary_range.append(f"₹{job_data.get('salary_max'):,}")
                og_metadata['job:salary'] = " - ".join(salary_range)
            
            return og_metadata
            
        except Exception as e:
            logger.error(f"Error generating OpenGraph metadata: {e}")
            return self._generate_fallback_og_metadata(job_data)

    def generate_twitter_card_metadata(self, job_data: Dict[str, Any], request_url: str = "") -> Dict[str, Any]:
        """
        Generate Twitter Card metadata for enhanced Twitter sharing.
        
        Args:
            job_data: Dictionary containing job information
            request_url: Full URL of the job page
            
        Returns:
            Dictionary with Twitter Card meta tags
        """
        try:
            title = job_data.get('title', '')
            description = self._clean_html_for_schema(job_data.get('description', ''))
            
            # Generate Twitter title (70 chars max)
            twitter_title = title
            if len(twitter_title) > 70:
                twitter_title = twitter_title[:67] + "..."
            
            # Generate Twitter description (200 chars max)
            twitter_description = description
            if not twitter_description:
                twitter_description = f"Apply for {title}. Check details and apply online."
            
            if len(twitter_description) > 200:
                twitter_description = twitter_description[:197] + "..."
            
            # Generate Twitter image
            twitter_image = job_data.get('image_url', '/static/images/sarkaribot-job-card.jpg')
            
            twitter_metadata = {
                'twitter:card': 'summary_large_image',
                'twitter:site': '@SarkariBot',
                'twitter:creator': '@SarkariBot',
                'twitter:title': twitter_title,
                'twitter:description': twitter_description,
                'twitter:image': twitter_image,
                'twitter:url': request_url,
            }
            
            # Add job-specific Twitter data
            if job_data.get('total_posts'):
                twitter_metadata['twitter:label1'] = 'Total Posts'
                twitter_metadata['twitter:data1'] = str(job_data.get('total_posts'))
            
            if job_data.get('last_date'):
                twitter_metadata['twitter:label2'] = 'Last Date'
                twitter_metadata['twitter:data2'] = job_data.get('last_date')
            
            return twitter_metadata
            
        except Exception as e:
            logger.error(f"Error generating Twitter Card metadata: {e}")
            return self._generate_fallback_twitter_metadata(job_data)

    def generate_breadcrumb_schema(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate breadcrumb structured data.
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            BreadcrumbList schema.org structured data
        """
        breadcrumbs = [
            {"name": "Home", "url": "/"},
            {"name": "Government Jobs", "url": "/jobs/"},
        ]
        
        # Add category breadcrumb
        if job_data.get('category'):
            breadcrumbs.append({
                "name": job_data.get('category'),
                "url": f"/category/{job_data.get('category_slug', '')}/"
            })
        
        # Add current job
        job_title = job_data.get('title', '')
        if len(job_title) > 50:
            job_title = job_title[:47] + "..."
        
        breadcrumbs.append({
            "name": job_title,
            "url": f"/jobs/{job_data.get('slug', '')}/"
        })
        
        # Convert to schema.org format
        breadcrumb_list = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": []
        }
        
        for i, breadcrumb in enumerate(breadcrumbs):
            breadcrumb_list["itemListElement"].append({
                "@type": "ListItem",
                "position": i + 1,
                "name": breadcrumb["name"],
                "item": breadcrumb["url"]
            })
        
        return breadcrumb_list
    
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
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug."""
        return slugify(title)

    def _generate_fallback_og_metadata(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic OpenGraph metadata when full generation fails."""
        title = job_data.get('title', 'Government Job')
        return {
            'og:type': 'article',
            'og:title': title,
            'og:description': f"Apply for {title}. Government job opportunity.",
            'og:site_name': 'SarkariBot - Government Jobs Portal',
            'og:locale': 'en_IN',
        }

    def _generate_fallback_twitter_metadata(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic Twitter Card metadata when full generation fails."""
        title = job_data.get('title', 'Government Job')
        return {
            'twitter:card': 'summary',
            'twitter:site': '@SarkariBot',
            'twitter:title': title,
            'twitter:description': f"Apply for {title}. Government job opportunity.",
        }

    def generate_comprehensive_metadata(self, job_data: Dict[str, Any], request_url: str = "") -> Dict[str, Any]:
        """
        Generate complete SEO metadata including structured data, OpenGraph, and Twitter Cards.
        
        This is an enhanced version of generate_seo_metadata that includes all metadata types.
        
        Args:
            job_data: Dictionary containing job information
            request_url: Full URL of the job page for social sharing
            
        Returns:
            Dictionary with comprehensive SEO metadata
        """
        try:
            # Generate base SEO metadata
            base_metadata = self.generate_seo_metadata(job_data)
            
            # Generate enhanced structured data
            enhanced_schema = self._generate_job_schema(job_data)
            breadcrumb_schema = self.generate_breadcrumb_schema(job_data)
            
            # Generate social media metadata
            og_metadata = self.generate_open_graph_metadata(job_data, request_url)
            twitter_metadata = self.generate_twitter_card_metadata(job_data, request_url)
            
            # Combine all metadata
            comprehensive_metadata = {
                **base_metadata,
                'structured_data': enhanced_schema,
                'breadcrumb_schema': breadcrumb_schema,
                'open_graph': og_metadata,
                'twitter_card': twitter_metadata,
                'meta_robots': 'index, follow',
                'canonical_url': request_url or base_metadata.get('canonical_url'),
                'last_modified': job_data.get('updated_at', datetime.now().isoformat()),
            }
            
            # Calculate enhanced quality score
            comprehensive_metadata['quality_score'] = self._calculate_comprehensive_quality_score(
                job_data, comprehensive_metadata
            )
            
            logger.info(f"Generated comprehensive SEO metadata for job: {job_data.get('title', '')}")
            return comprehensive_metadata
            
        except Exception as e:
            logger.error(f"Error generating comprehensive metadata: {e}")
    def _calculate_comprehensive_quality_score(self, job_data: Dict[str, Any], metadata: Dict[str, Any]) -> float:
        """Calculate enhanced SEO quality score including all metadata types."""
        score = 0.0
        
        # Base content quality (40 points)
        base_score = self._calculate_quality_score(job_data, metadata.get('keywords', []))
        score += base_score * 0.4
        
        # Structured data completeness (20 points)
        structured_data = metadata.get('structured_data', {})
        required_schema_fields = [
            'title', 'description', 'datePosted', 'hiringOrganization',
            'jobLocation', 'employmentType'
        ]
        optional_schema_fields = [
            'baseSalary', 'educationRequirements', 'validThrough',
            'qualifications', 'applicationContact'
        ]
        
        schema_score = 0
        for field in required_schema_fields:
            if structured_data.get(field):
                schema_score += 2
        
        for field in optional_schema_fields:
            if structured_data.get(field):
                schema_score += 1
        
        score += min(schema_score, 20)
        
        # OpenGraph metadata quality (20 points)
        og_metadata = metadata.get('open_graph', {})
        required_og_fields = ['og:title', 'og:description', 'og:type', 'og:url']
        og_score = sum(2 for field in required_og_fields if og_metadata.get(field))
        
        optional_og_fields = ['og:image', 'article:published_time', 'article:author']
        og_score += sum(3 for field in optional_og_fields if og_metadata.get(field))
        
        score += min(og_score, 20)
        
        # Twitter Card metadata quality (20 points)
        twitter_metadata = metadata.get('twitter_card', {})
        required_twitter_fields = ['twitter:card', 'twitter:title', 'twitter:description']
        twitter_score = sum(3 for field in required_twitter_fields if twitter_metadata.get(field))
        
        optional_twitter_fields = ['twitter:image', 'twitter:data1', 'twitter:data2']
        twitter_score += sum(2 for field in optional_twitter_fields if twitter_metadata.get(field))
        
        score += min(twitter_score, 20)
        
        return round(min(score, 100.0), 1)

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
