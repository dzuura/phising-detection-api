"""Statistics tracking service"""
import threading
from datetime import datetime
from typing import Dict, Any


class StatsService:
    """Tracks statistics for URL analysis"""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.total_analyzed = 0
        self.phishing_detected = 0
        self.legitimate_detected = 0
        self.confidence_sum = 0.0
        self.session_start = datetime.utcnow().isoformat() + "Z"
    
    def record_analysis(self, is_phishing: bool, confidence: float) -> None:
        """
        Record an analysis result
        
        Args:
            is_phishing: Whether URL was phishing
            confidence: Confidence score
        """
        with self.lock:
            self.total_analyzed += 1
            self.confidence_sum += confidence
            
            if is_phishing:
                self.phishing_detected += 1
            else:
                self.legitimate_detected += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current statistics
        
        Returns:
            Dictionary of statistics
        """
        with self.lock:
            avg_confidence = (
                self.confidence_sum / self.total_analyzed
                if self.total_analyzed > 0
                else 0.0
            )
            
            return {
                "total_analyzed": self.total_analyzed,
                "phishing_detected": self.phishing_detected,
                "legitimate_detected": self.legitimate_detected,
                "avg_confidence": round(avg_confidence, 4),
                "session_start": self.session_start
            }
    
    def reset(self) -> None:
        """Reset statistics"""
        with self.lock:
            self.total_analyzed = 0
            self.phishing_detected = 0
            self.legitimate_detected = 0
            self.confidence_sum = 0.0
            self.session_start = datetime.utcnow().isoformat() + "Z"


# Global stats service instance
stats_service = StatsService()
