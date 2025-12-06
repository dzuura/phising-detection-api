"""TLD one-hot encoding consistent with training data"""
from typing import Dict, List
import json
import os
import numpy as np


class TLDEncoder:
    """Handles TLD one-hot encoding"""
    
    def __init__(self):
        # Load exact TLD list from training data
        # This list contains all 695 unique TLDs from the training dataset
        tld_file = os.path.join(os.path.dirname(__file__), '../../tld_list.json')
        with open(tld_file, 'r') as f:
            all_tlds = json.load(f)
        
        # pd.get_dummies with drop_first=True drops the first TLD
        # So we use TLDs from index 1 onwards (694 TLDs)
        self.known_tlds = all_tlds[1:]  # Skip first TLD to match drop_first=True
        
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
