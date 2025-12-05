"""TLD one-hot encoding consistent with training data"""
from typing import Dict, List
import numpy as np


class TLDEncoder:
    """Handles TLD one-hot encoding"""
    
    def __init__(self):
        # Common TLDs from training data (this should match training exactly)
        # Based on the dataset, these are the most common TLDs
        self.known_tlds = [
            'com', 'org', 'net', 'edu', 'gov', 'mil', 'int',
            'uk', 'de', 'fr', 'it', 'es', 'nl', 'be', 'ch',
            'au', 'ca', 'jp', 'cn', 'in', 'br', 'ru', 'za',
            'io', 'co', 'me', 'tv', 'info', 'biz', 'name',
            'pro', 'mobi', 'asia', 'tel', 'travel', 'jobs',
            'cat', 'aero', 'coop', 'museum', 'dev', 'app'
        ]
        
        # Create TLD to index mapping
        self.tld_to_index = {tld: idx for idx, tld in enumerate(self.known_tlds)}
    
    def encode(self, tld: str) -> List[int]:
        """
        One-hot encode a TLD
        
        Args:
            tld: The top-level domain to encode
            
        Returns:
            List of binary values representing one-hot encoding
        """
        tld = tld.lower().strip()
        
        # Initialize all zeros
        encoding = [0] * len(self.known_tlds)
        
        # Set the appropriate index to 1 if TLD is known
        if tld in self.tld_to_index:
            encoding[self.tld_to_index[tld]] = 1
        # If unknown TLD, all remain 0 (or could use a default encoding)
        
        return encoding
    
    def get_feature_names(self) -> List[str]:
        """Get feature names for TLD encoding"""
        return [f"TLD_{tld}" for tld in self.known_tlds]


# Global TLD encoder instance
tld_encoder = TLDEncoder()
