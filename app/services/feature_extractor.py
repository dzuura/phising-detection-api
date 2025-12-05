"""Feature extraction from URLs"""
import re
import socket
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class FeatureExtractor:
    """Extracts features from URLs for phishing detection"""
    
    def __init__(self):
        self.timeout = settings.scraping_timeout
        self.max_redirects = settings.max_redirects
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def extract_all_features(self, url: str) -> Dict[str, Any]:
        """
        Extract all features from a URL
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dictionary containing all extracted features
        """
        try:
            # Parse URL
            parsed = urlparse(url)
            
            # Extract URL-based features
            url_features = self._extract_url_features(url, parsed)
            
            # Extract content-based features (with timeout)
            content_features = self._extract_content_features(url)
            
            # Extract network features (redirect, IP, location)
            network_features = self._extract_network_features(url)
            
            # Combine all features
            all_features = {
                **url_features,
                **content_features,
                **network_features,
                "detection_timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            logger.info(f"Successfully extracted features for URL")
            return all_features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}", exc_info=True)
            raise
    
    def _extract_url_features(self, url: str, parsed) -> Dict[str, Any]:
        """Extract features from URL structure"""
        domain = parsed.netloc
        path = parsed.path
        query = parsed.query
        
        # Get TLD
        tld = domain.split('.')[-1] if '.' in domain else ''
        
        # Calculate URL similarity index (simplified version)
        url_similarity = self._calculate_url_similarity(url, domain)
        
        # Calculate character continuation rate
        char_continuation = self._calculate_char_continuation_rate(domain)
        
        features = {
            "url_similarity_index": url_similarity,
            "char_continuation_rate": char_continuation,
            "tld": tld,
            "no_of_dot_in_url": url.count('.'),
            "no_of_dash_in_url": url.count('-'),
            "no_of_at_symbol_in_url": url.count('@'),
            "no_of_slash_in_url": url.count('/'),
            "no_of_percent_in_url": url.count('%'),
            "no_of_hash_in_url": url.count('#'),
            "no_of_underscore_in_url": url.count('_'),
            "no_of_question_mark_in_url": url.count('?'),
            "no_of_equals_in_url": url.count('='),
            "no_of_ampersand_in_url": url.count('&'),
        }
        
        return features
    
    def _calculate_url_similarity(self, url: str, domain: str) -> float:
        """Calculate URL similarity index"""
        # Simplified: check if domain appears in full URL
        if domain in url:
            return 100.0
        return 50.0
    
    def _calculate_char_continuation_rate(self, text: str) -> float:
        """Calculate character continuation rate"""
        if len(text) <= 1:
            return 0.0
        
        # Count consecutive same characters
        continuations = 0
        for i in range(len(text) - 1):
            if text[i] == text[i + 1]:
                continuations += 1
        
        return continuations / (len(text) - 1) if len(text) > 1 else 0.0
    
    def _extract_content_features(self, url: str) -> Dict[str, Any]:
        """Extract features from web page content"""
        default_features = {
            "url_is_live": 0,
            "has_title": 0,
            "has_favicon": 0,
            "has_social_net": 0,
            "has_submit_button": 0,
            "has_hidden_fields": 0,
            "has_description": 0,
            "no_of_js": 0,
            "no_of_self_ref": 0,
            "has_copyright_info": 0,
            "pay": 0,
        }
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                default_features["url_is_live"] = 1
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for title
                if soup.find('title'):
                    default_features["has_title"] = 1
                
                # Check for favicon
                if soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon'):
                    default_features["has_favicon"] = 1
                
                # Check for social media links
                social_patterns = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube']
                links = soup.find_all('a', href=True)
                for link in links:
                    if any(pattern in link['href'].lower() for pattern in social_patterns):
                        default_features["has_social_net"] = 1
                        break
                
                # Check for submit buttons
                if soup.find('input', type='submit') or soup.find('button', type='submit'):
                    default_features["has_submit_button"] = 1
                
                # Check for hidden fields
                if soup.find('input', type='hidden'):
                    default_features["has_hidden_fields"] = 1
                
                # Check for meta description
                if soup.find('meta', attrs={'name': 'description'}):
                    default_features["has_description"] = 1
                
                # Count JavaScript files
                scripts = soup.find_all('script', src=True)
                default_features["no_of_js"] = len(scripts)
                
                # Count self-references
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                self_refs = 0
                for link in links:
                    if domain in link.get('href', ''):
                        self_refs += 1
                default_features["no_of_self_ref"] = self_refs
                
                # Check for copyright info
                text_content = soup.get_text().lower()
                if 'copyright' in text_content or '©' in text_content:
                    default_features["has_copyright_info"] = 1
                
                # Check for payment-related keywords
                payment_keywords = ['payment', 'credit card', 'paypal', 'checkout', 'billing']
                if any(keyword in text_content for keyword in payment_keywords):
                    default_features["pay"] = 1
            
            return default_features
            
        except requests.Timeout:
            logger.warning(f"Timeout while fetching content")
            return default_features
        except Exception as e:
            logger.warning(f"Error extracting content features: {str(e)}")
            return default_features
    
    def _extract_network_features(self, url: str) -> Dict[str, Any]:
        """Extract network-related features (redirects, IP, location)"""
        features = {
            "redirect_chain": [],
            "final_url": url,
            "ip_address": None,
            "location": {
                "country": None,
                "city": None,
                "region": None
            }
        }
        
        try:
            # Track redirects
            session = requests.Session()
            session.max_redirects = self.max_redirects
            
            response = session.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # Get redirect chain
            if response.history:
                features["redirect_chain"] = [resp.url for resp in response.history]
                features["final_url"] = response.url
            
            # Get IP address
            parsed = urlparse(response.url)
            domain = parsed.netloc
            
            try:
                ip_address = socket.gethostbyname(domain)
                features["ip_address"] = ip_address
                
                # Get geolocation (using ip-api.com free service)
                geo_response = requests.get(
                    f"http://ip-api.com/json/{ip_address}",
                    timeout=3
                )
                
                if geo_response.status_code == 200:
                    geo_data = geo_response.json()
                    if geo_data.get('status') == 'success':
                        features["location"] = {
                            "country": geo_data.get('country'),
                            "city": geo_data.get('city'),
                            "region": geo_data.get('regionName')
                        }
            except socket.gaierror:
                logger.warning(f"Could not resolve IP for domain: {domain}")
            except Exception as e:
                logger.warning(f"Error getting geolocation: {str(e)}")
            
        except requests.Timeout:
            logger.warning("Timeout while extracting network features")
        except Exception as e:
            logger.warning(f"Error extracting network features: {str(e)}")
        
        return features
    
    def features_to_vector(self, features: Dict[str, Any]) -> List[float]:
        """
        Convert extracted features to vector for model input
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            List of feature values in correct order for model
        """
        # Order must match training data
        # This is a simplified version - actual implementation needs exact order from training
        vector = [
            features.get("url_similarity_index", 0),
            features.get("char_continuation_rate", 0),
            features.get("no_of_dot_in_url", 0),
            features.get("no_of_dash_in_url", 0),
            features.get("no_of_at_symbol_in_url", 0),
            features.get("no_of_slash_in_url", 0),
            features.get("no_of_percent_in_url", 0),
            features.get("no_of_hash_in_url", 0),
            features.get("no_of_underscore_in_url", 0),
            features.get("url_is_live", 0),
            features.get("has_title", 0),
            features.get("has_favicon", 0),
            features.get("has_social_net", 0),
            features.get("has_submit_button", 0),
            features.get("has_hidden_fields", 0),
            features.get("has_description", 0),
            features.get("no_of_js", 0),
            features.get("no_of_self_ref", 0),
            features.get("has_copyright_info", 0),
            features.get("pay", 0),
        ]
        
        # Add TLD one-hot encoding (simplified - needs actual TLD list from training)
        # This would need to match the exact TLD encoding from training
        
        return vector


# Global feature extractor instance
feature_extractor = FeatureExtractor()
