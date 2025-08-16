"""
Workflow Type Detection and Management Utilities
Provides configurable workflow categorization based on content analysis
"""

from typing import List, Dict, Any, Optional
from app.core.config import settings
import re


class WorkflowTypeDetector:
    """
    Detects workflow types based on configurable keywords and patterns
    """
    
    def __init__(self):
        self.categories = settings.DEFAULT_WORKFLOW_CATEGORIES
        self.keywords = settings.WORKFLOW_TYPE_KEYWORDS
        self.high_priority_types = settings.HIGH_PRIORITY_WORKFLOW_TYPES
    
    def detect_workflow_type(
        self, 
        applications: List[str], 
        description: str, 
        steps: List[str]
    ) -> str:
        """
        Detect workflow type based on applications used, description, and steps
        
        Args:
            applications: List of applications used in workflow
            description: Workflow description
            steps: List of workflow steps
            
        Returns:
            Detected workflow type
        """
        # Combine all text for analysis
        combined_text = f"{' '.join(applications)} {description} {' '.join(steps)}".lower()
        
        # Score each category based on keyword matches
        category_scores = {}
        for category, keywords in self.keywords.items():
            score = 0
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = len(re.findall(pattern, combined_text))
                score += matches
            
            if score > 0:
                category_scores[category] = score
        
        # Return the category with highest score, or 'other' if no matches
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        else:
            return "other"
    
    def calculate_priority_score(
        self, 
        workflow_type: str, 
        repetitive_score: float, 
        time_percentage: float = 0.0
    ) -> float:
        """
        Calculate priority score for a workflow
        
        Args:
            workflow_type: Type of workflow
            repetitive_score: How repetitive the workflow is (0-1)
            time_percentage: Percentage of total time spent on this workflow
            
        Returns:
            Priority score (higher = more important)
        """
        base_score = repetitive_score
        
        # Boost score for high-priority workflow types
        if workflow_type in self.high_priority_types:
            base_score *= 1.3
        
        # Factor in time percentage
        time_factor = min(time_percentage / 100.0, 0.5)  # Cap at 0.5
        
        return min(base_score + time_factor, 1.0)  # Cap at 1.0
    
    def get_workflow_categories(self) -> List[str]:
        """Get available workflow categories"""
        return self.categories.copy()
    
    def is_high_priority_type(self, workflow_type: str) -> bool:
        """Check if a workflow type is considered high priority"""
        return workflow_type in self.high_priority_types


def get_workflow_detector() -> WorkflowTypeDetector:
    """Get workflow type detector instance"""
    return WorkflowTypeDetector()