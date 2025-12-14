"""
Base evaluator class.
"""

from abc import ABC, abstractmethod
from ..types import Trace, CategoryResult


class BaseEvaluator(ABC):
    """Base class for all evaluators."""
    
    name: str = "base"
    
    @abstractmethod
    def evaluate(self, trace: Trace, system_description: str = "") -> CategoryResult:
        """
        Evaluate a trace and return category result.
        
        Args:
            trace: The trace to evaluate
            system_description: Description of what the system does
        
        Returns:
            CategoryResult with scores and issues
        """
        pass

