"""
Feature extraction from URLs
Implements all 22 features required by the model
"""
import re
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import requests
from app.core.logging import get_logger

logger = get_logger(__name__)


class FeatureExtractor:
    """Extract all 22 features required by the Random Forest model"""
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.html_content = None
        self.soup = None
        self.url_is_live = False
        self.redirect_chain = []
        self.final_url = None
        self.ip_address = None
        self.location = {}
    
    def extract_all_features(self, url: str) -> Dict[str, Any]:
        """
        Extract all 22 features from URL
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with all 22 features
        """
        features = {}
        
        # Parse URL
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        full_url = url
        
        # Try to fetch HTML content
        self._fetch_html(url)
        
        # Extract URL structure features (don't need HTML)
        features['URLSimilarityIndex'] = self._calculate_url_similarity_index(url)
        features['CharContinuationRate'] = self._calculate_char_continuation_rate(url)
        features['URLCharProb'] = self._calculate_url_char_prob(url)
        features['LetterRatioInURL'] = self._calculate_letter_ratio(url)
        features['DegitRatioInURL'] = self._calculate_digit_ratio(url)
        features['NoOfOtherSpecialCharsInURL'] = self._count_other_special_chars(url)
        features['SpacialCharRatioInURL'] = self._calculate_special_char_ratio(url)
        features['IsHTTPS'] = 1 if parsed.scheme == 'https' else 0
        
        # Additional URL features
        features['NoOfDotInURL'] = url.count('.')
        features['NoOfDashInURL'] = url.count('-')
        features['URLIsLive'] = 1 if self.url_is_live else 0
        
        # Extract content-based features (need HTML)
        if self.url_is_live and self.soup:
            features['HasTitle'] = self._has_title()
            features['DomainTitleMatchScore'] = self._calculate_domain_title_match(domain)
            features['URLTitleMatchScore'] = self._calculate_url_title_match(url)
            features['HasFavicon'] = self._has_favicon()
            features['Robots'] = self._has_robots()
            features['IsResponsive'] = self._is_responsive()
            features['HasDescription'] = self._has_description()
            features['HasSocialNet'] = self._has_social_net()
            features['HasSubmitButton'] = self._has_submit_button()
            features['HasHiddenFields'] = self._has_hidden_fields()
            features['Pay'] = self._has_payment_keywords()
            features['HasCopyrightInfo'] = self._has_copyright()
            features['NoOfJS'] = self._count_js_files()
            features['NoOfSelfRef'] = self._count_self_references(domain)
        else:
            # Default values when URL is not accessible
            features['HasTitle'] = 0
            features['DomainTitleMatchScore'] = 0.0
            features['URLTitleMatchScore'] = 0.0
            features['HasFavicon'] = 0
            features['Robots'] = 0
            features['IsResponsive'] = 0
            features['HasDescription'] = 0
            features['HasSocialNet'] = 0
            features['HasSubmitButton'] = 0
            features['HasHiddenFields'] = 0
            features['Pay'] = 0
            features['HasCopyrightInfo'] = 0
            features['NoOfJS'] = 0
            features['NoOfSelfRef'] = 0
        
        return features
    
    def _fetch_html(self, url: str) -> None:
        """Fetch HTML content from URL and track redirects"""
        try:
            # Track redirects
            self.redirect_chain = []
            
            response = requests.get(
                url, 
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                allow_redirects=True
            )
            
            # Build redirect chain
            if response.history:
                for resp in response.history:
                    self.redirect_chain.append(resp.url)
                self.redirect_chain.append(response.url)
            else:
                self.redirect_chain = [url]
            
            self.final_url = response.url
            
            # Check if successful before processing
            if response.status_code == 200:
                self.html_content = response.text
                self.soup = BeautifulSoup(self.html_content, 'html.parser')
                self.url_is_live = True
                logger.info(f"Successfully fetched HTML from {url}")
                
                # Try to get IP address and location (after successful fetch)
                try:
                    import socket
                    parsed = urlparse(response.url)
                    hostname = parsed.netloc
                    self.ip_address = socket.gethostbyname(hostname)
                    logger.info(f"Resolved IP: {self.ip_address}")
                    
                    # Try to get location info using ip-api.com (free, no key needed)
                    try:
                        geo_response = requests.get(
                            f"http://ip-api.com/json/{self.ip_address}",
                            timeout=2
                        )
                        if geo_response.status_code == 200:
                            geo_data = geo_response.json()
                            if geo_data.get('status') == 'success':
                                self.location = {
                                    'country': geo_data.get('country'),
                                    'region': geo_data.get('regionName'),
                                    'city': geo_data.get('city'),
                                    'isp': geo_data.get('isp'),
                                    'lat': str(geo_data.get('lat')) if geo_data.get('lat') else None,
                                    'lon': str(geo_data.get('lon')) if geo_data.get('lon') else None
                                }
                                logger.info(f"Got location: {self.location.get('city')}, {self.location.get('country')}")
                            else:
                                self.location = {}
                        else:
                            self.location = {}
                    except Exception as e:
                        logger.debug(f"Failed to get location for {self.ip_address}: {str(e)}")
                        self.location = {}
                except Exception as e:
                    logger.debug(f"Failed to get IP address: {str(e)}")
                    self.ip_address = None
                    self.location = {}
            else:
                logger.warning(f"Failed to fetch {url}: Status {response.status_code}")
                self.url_is_live = False
                
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {str(e)}")
            self.url_is_live = False
            self.redirect_chain = []
            self.final_url = url
            self.ip_address = None
            self.location = {}
    
    # ========== URL STRUCTURE FEATURES ==========
    
    def _calculate_url_similarity_index(self, url: str) -> float:
        """
        Calculate URL similarity index
        Based on character frequency distribution
        """
        # Remove protocol and www
        clean_url = re.sub(r'^https?://(www\.)?', '', url)
        
        # Count character frequencies
        char_freq = {}
        for char in clean_url.lower():
            if char.isalnum():
                char_freq[char] = char_freq.get(char, 0) + 1
        
        if not char_freq:
            return 0.0
        
        # Calculate entropy-like measure
        total_chars = sum(char_freq.values())
        unique_chars = len(char_freq)
        
        # Similarity index: higher = more uniform distribution
        if unique_chars == 0:
            return 0.0
        
        avg_freq = total_chars / unique_chars
        variance = sum((freq - avg_freq) ** 2 for freq in char_freq.values()) / unique_chars
        
        # Normalize to 0-100 range
        similarity = 100 / (1 + variance / avg_freq) if avg_freq > 0 else 0
        
        return round(similarity, 2)
    
    def _calculate_char_continuation_rate(self, url: str) -> float:
        """
        Calculate character continuation rate
        Measures how often same character appears consecutively
        """
        if len(url) <= 1:
            return 0.0
        
        # Count consecutive same characters
        continuations = 0
        for i in range(len(url) - 1):
            if url[i] == url[i + 1]:
                continuations += 1
        
        # Calculate rate
        rate = continuations / (len(url) - 1)
        return round(rate, 6)
    
    def _calculate_url_char_prob(self, url: str) -> float:
        """
        Calculate URL character probability
        Based on expected character distribution in legitimate URLs
        """
        # Expected frequencies for legitimate URLs (simplified)
        expected_freq = {
            'letters': 0.60,
            'digits': 0.15,
            'dots': 0.05,
            'slashes': 0.10,
            'hyphens': 0.05,
            'others': 0.05
        }
        
        # Count actual frequencies
        letters = sum(1 for c in url if c.isalpha())
        digits = sum(1 for c in url if c.isdigit())
        dots = url.count('.')
        slashes = url.count('/')
        hyphens = url.count('-')
        others = len(url) - (letters + digits + dots + slashes + hyphens)
        
        total = len(url)
        if total == 0:
            return 0.0
        
        actual_freq = {
            'letters': letters / total,
            'digits': digits / total,
            'dots': dots / total,
            'slashes': slashes / total,
            'hyphens': hyphens / total,
            'others': others / total
        }
        
        # Calculate probability score (lower difference = higher probability)
        diff = sum(abs(actual_freq[k] - expected_freq[k]) for k in expected_freq)
        prob = max(0, 1 - diff)
        
        return round(prob, 6)
    
    def _calculate_letter_ratio(self, url: str) -> float:
        """Calculate ratio of letters in URL"""
        if len(url) == 0:
            return 0.0
        
        letters = sum(1 for c in url if c.isalpha())
        ratio = letters / len(url)
        return round(ratio, 3)
    
    def _calculate_digit_ratio(self, url: str) -> float:
        """Calculate ratio of digits in URL"""
        if len(url) == 0:
            return 0.0
        
        digits = sum(1 for c in url if c.isdigit())
        ratio = digits / len(url)
        return round(ratio, 3)
    
    def _count_other_special_chars(self, url: str) -> int:
        """Count special characters (excluding common URL chars)"""
        # Common URL chars: letters, digits, ., /, -, _, ~, :, ?, #, [, ], @, !, $, &, ', (, ), *, +, ,, ;, =
        common_chars = set('.-_~:/?#[]@!$&\'()*+,;=')
        
        count = 0
        for char in url:
            if not char.isalnum() and char not in common_chars:
                count += 1
        
        return count
    
    def _calculate_special_char_ratio(self, url: str) -> float:
        """Calculate ratio of special characters in URL"""
        if len(url) == 0:
            return 0.0
        
        special_chars = sum(1 for c in url if not c.isalnum())
        ratio = special_chars / len(url)
        return round(ratio, 3)
    
    # ========== CONTENT-BASED FEATURES ==========
    
    def _has_title(self) -> int:
        """Check if page has title tag"""
        if not self.soup:
            return 0
        
        title = self.soup.find('title')
        return 1 if title and title.string and len(title.string.strip()) > 0 else 0
    
    def _calculate_domain_title_match(self, domain: str) -> float:
        """Calculate similarity between domain and title"""
        if not self.soup:
            return 0.0
        
        title = self.soup.find('title')
        if not title or not title.string:
            return 0.0
        
        title_text = title.string.lower().strip()
        domain_clean = domain.replace('www.', '').replace('.com', '').replace('.', ' ')
        
        # Simple word matching
        domain_words = set(domain_clean.split())
        title_words = set(title_text.split())
        
        if not domain_words or not title_words:
            return 0.0
        
        matches = len(domain_words & title_words)
        score = matches / len(domain_words) if domain_words else 0.0
        
        return round(score, 2)
    
    def _calculate_url_title_match(self, url: str) -> float:
        """Calculate similarity between URL and title"""
        if not self.soup:
            return 0.0
        
        title = self.soup.find('title')
        if not title or not title.string:
            return 0.0
        
        title_text = title.string.lower().strip()
        url_clean = re.sub(r'https?://(www\.)?', '', url).replace('/', ' ').replace('-', ' ')
        
        # Simple word matching
        url_words = set(url_clean.split())
        title_words = set(title_text.split())
        
        if not url_words or not title_words:
            return 0.0
        
        matches = len(url_words & title_words)
        score = matches / len(url_words) if url_words else 0.0
        
        return round(score, 2)
    
    def _has_favicon(self) -> int:
        """Check if page has favicon"""
        if not self.soup:
            return 0
        
        # Check for favicon link tags
        favicon = self.soup.find('link', rel=lambda x: x and 'icon' in x.lower())
        return 1 if favicon else 0
    
    def _has_robots(self) -> int:
        """Check if page has robots meta tag"""
        if not self.soup:
            return 0
        
        robots = self.soup.find('meta', attrs={'name': 'robots'})
        return 1 if robots else 0
    
    def _is_responsive(self) -> int:
        """Check if page has viewport meta tag (indicator of responsive design)"""
        if not self.soup:
            return 0
        
        viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        return 1 if viewport else 0
    
    def _has_description(self) -> int:
        """Check if page has meta description"""
        if not self.soup:
            return 0
        
        description = self.soup.find('meta', attrs={'name': 'description'})
        return 1 if description and description.get('content') else 0
    
    def _has_social_net(self) -> int:
        """Check if page has social media links"""
        if not self.soup:
            return 0
        
        social_patterns = [
            'facebook.com', 'twitter.com', 'instagram.com', 
            'linkedin.com', 'youtube.com', 'tiktok.com'
        ]
        
        links = self.soup.find_all('a', href=True)
        for link in links:
            href = link['href'].lower()
            if any(pattern in href for pattern in social_patterns):
                return 1
        
        return 0
    
    def _has_submit_button(self) -> int:
        """Check if page has submit button or input"""
        if not self.soup:
            return 0
        
        # Check for submit buttons
        submit_button = self.soup.find('button', type='submit')
        submit_input = self.soup.find('input', type='submit')
        
        return 1 if submit_button or submit_input else 0
    
    def _has_hidden_fields(self) -> int:
        """Check if page has hidden input fields"""
        if not self.soup:
            return 0
        
        hidden_fields = self.soup.find_all('input', type='hidden')
        return 1 if hidden_fields else 0
    
    def _has_payment_keywords(self) -> int:
        """Check if page contains payment-related keywords"""
        if not self.soup or not self.html_content:
            return 0
        
        payment_keywords = [
            'payment', 'pay', 'credit card', 'debit card', 
            'checkout', 'billing', 'purchase', 'buy now'
        ]
        
        text = self.html_content.lower()
        for keyword in payment_keywords:
            if keyword in text:
                return 1
        
        return 0
    
    def _has_copyright(self) -> int:
        """Check if page has copyright information"""
        if not self.soup or not self.html_content:
            return 0
        
        text = self.html_content.lower()
        
        # Check for copyright symbols and text
        copyright_patterns = ['©', '&copy;', 'copyright', '(c)']
        
        for pattern in copyright_patterns:
            if pattern in text:
                return 1
        
        return 0
    
    def _count_js_files(self) -> int:
        """Count number of JavaScript files"""
        if not self.soup:
            return 0
        
        scripts = self.soup.find_all('script', src=True)
        return len(scripts)
    
    def _count_self_references(self, domain: str) -> int:
        """Count number of links pointing to same domain"""
        if not self.soup:
            return 0
        
        links = self.soup.find_all('a', href=True)
        self_refs = 0
        
        for link in links:
            href = link['href']
            if domain in href or href.startswith('/') or href.startswith('#'):
                self_refs += 1
        
        return self_refs


# Global instance
feature_extractor = FeatureExtractor()
