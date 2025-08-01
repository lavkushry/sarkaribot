#!/usr/bin/env python3
"""
Setup script for NLP dependencies in SarkariBot.

This script ensures all required NLP dependencies are properly installed
and configured for the SEO automation engine.
"""

import subprocess
import sys
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_package_installed(package_name: str) -> bool:
    """Check if a Python package is installed."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def install_package(package_name: str, version: str = None) -> bool:
    """Install a Python package using pip."""
    try:
        if version:
            cmd = [sys.executable, "-m", "pip", "install", f"{package_name}=={version}"]
        else:
            cmd = [sys.executable, "-m", "pip", "install", package_name]
        
        logger.info(f"Installing {package_name}...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package_name}: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return False


def install_spacy_model(model_name: str = "en_core_web_sm") -> bool:
    """Install spaCy language model."""
    try:
        # Check if the model is already installed
        import spacy
        try:
            nlp = spacy.load(model_name)
            logger.info(f"spaCy model {model_name} is already installed")
            return True
        except OSError:
            pass
        
        # Install the model
        logger.info(f"Installing spaCy model {model_name}...")
        cmd = [sys.executable, "-m", "spacy", "download", model_name]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Successfully installed spaCy model {model_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install spaCy model {model_name}: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return False
    except ImportError:
        logger.error("spaCy is not installed. Install spaCy first.")
        return False


def download_nltk_data():
    """Download required NLTK data."""
    try:
        import nltk
        
        # Download required NLTK data
        nltk_downloads = [
            'punkt',
            'stopwords',
            'wordnet',
            'averaged_perceptron_tagger',
            'vader_lexicon'
        ]
        
        for dataset in nltk_downloads:
            try:
                logger.info(f"Downloading NLTK dataset: {dataset}")
                nltk.download(dataset, quiet=True)
            except Exception as e:
                logger.warning(f"Failed to download NLTK dataset {dataset}: {e}")
        
        logger.info("NLTK data download completed")
        return True
    except ImportError:
        logger.error("NLTK is not installed. Install NLTK first.")
        return False
    except Exception as e:
        logger.error(f"Failed to download NLTK data: {e}")
        return False


def verify_nlp_setup():
    """Verify that all NLP components are working correctly."""
    logger.info("Verifying NLP setup...")
    
    # Test spaCy
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("Test sentence for spaCy verification.")
        logger.info("✓ spaCy is working correctly")
    except Exception as e:
        logger.error(f"✗ spaCy verification failed: {e}")
        return False
    
    # Test NLTK
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        
        # Test basic NLTK functionality
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize("Test sentence for NLTK verification.")
        logger.info("✓ NLTK is working correctly")
    except Exception as e:
        logger.error(f"✗ NLTK verification failed: {e}")
        return False
    
    # Test SEO engine integration
    try:
        # Add the backend path to Python path for imports
        backend_path = Path(__file__).parent.parent / "sarkaribot" / "backend"
        if backend_path.exists():
            sys.path.insert(0, str(backend_path))
        
        from apps.seo.engine import NLPSEOEngine
        
        engine = NLPSEOEngine()
        test_data = {
            'title': 'Government Job Recruitment 2024',
            'description': 'Apply for this government job opportunity with good salary and benefits.',
            'department': 'Ministry of Railways'
        }
        
        metadata = engine.generate_seo_metadata(test_data)
        
        if metadata and metadata.get('seo_title') and metadata.get('keywords'):
            logger.info("✓ SEO engine is working correctly")
        else:
            logger.error("✗ SEO engine generated incomplete metadata")
            return False
            
    except Exception as e:
        logger.error(f"✗ SEO engine verification failed: {e}")
        return False
    
    logger.info("All NLP components verified successfully!")
    return True


def main():
    """Main setup function."""
    logger.info("Starting NLP dependencies setup for SarkariBot...")
    
    # Required packages with versions
    packages = [
        ('spacy', '3.7.2'),
        ('nltk', '3.8.1'),
        ('scikit-learn', '1.3.0'),
        ('numpy', '1.24.3'),
        ('textblob', '0.17.1')
    ]
    
    # Install packages
    all_installed = True
    for package, version in packages:
        if not check_package_installed(package):
            if not install_package(package, version):
                all_installed = False
        else:
            logger.info(f"✓ {package} is already installed")
    
    if not all_installed:
        logger.error("Some packages failed to install. Please check the errors above.")
        return False
    
    # Install spaCy model
    if not install_spacy_model():
        logger.error("Failed to install spaCy model")
        return False
    
    # Download NLTK data
    if not download_nltk_data():
        logger.error("Failed to download NLTK data")
        return False
    
    # Verify setup
    if not verify_nlp_setup():
        logger.error("NLP setup verification failed")
        return False
    
    logger.info("✓ NLP dependencies setup completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)