"""
Performance evaluator - Speed, efficiency, resource usage.
"""

from .base import BaseEvaluator
from ..types import Trace, CategoryResult, Score


class PerformanceEvaluator(BaseEvaluator):
    """Evaluates performance metrics."""
    
    name = "performance"
    
    def evaluate(self, trace: Trace, system_description: str = "") -> CategoryResult:
        
        checks = {}
        issues = []
        
        # Check 1: Total Duration
        duration_score = self._evaluate_duration(trace)
        checks["duration"] = duration_score
        
        if duration_score.value < 0.7:
            issues.append(f"Slow execution: {trace.duration_ms/1000:.1f}s")
        
        # Check 2: Token Efficiency
        token_score = self._evaluate_tokens(trace)
        checks["token_efficiency"] = token_score
        
        if token_score.value < 0.7:
            issues.append(f"High token usage: {trace.total_tokens:,} tokens")
        
        # Check 3: Error Rate
        error_score = self._evaluate_errors(trace)
        checks["error_rate"] = error_score
        
        if error_score.value < 0.9:
            issues.append("Errors occurred during execution")
        
        # Calculate category score
        avg_score = sum(s.value for s in checks.values()) / len(checks)
        
        return CategoryResult(
            name=self.name,
            score=avg_score,
            weight=0.15,
            checks=checks,
            issues=issues,
        )
    
    def _evaluate_duration(self, trace: Trace) -> Score:
        """Evaluate execution duration."""
        duration_sec = trace.duration_ms / 1000
        
        if duration_sec < 5:
            return Score(0.9, f"Fast execution ({duration_sec:.1f}s)")
        elif duration_sec < 15:
            return Score(0.7, f"Moderate execution time ({duration_sec:.1f}s)")
        elif duration_sec < 30:
            return Score(0.5, f"Slow execution ({duration_sec:.1f}s)")
        else:
            return Score(0.3, f"Very slow execution ({duration_sec:.1f}s)")
    
    def _evaluate_tokens(self, trace: Trace) -> Score:
        """Evaluate token usage efficiency."""
        tokens = trace.total_tokens
        
        if tokens == 0:
            return Score(1.0, "No LLM calls")
        
        if tokens < 1000:
            return Score(0.9, f"Efficient token usage ({tokens:,} tokens)")
        elif tokens < 5000:
            return Score(0.7, f"Moderate token usage ({tokens:,} tokens)")
        elif tokens < 20000:
            return Score(0.5, f"High token usage ({tokens:,} tokens)")
        else:
            return Score(0.3, f"Very high token usage ({tokens:,} tokens)")
    
    def _evaluate_errors(self, trace: Trace) -> Score:
        """Evaluate error rate."""
        if trace.error:
            return Score(0.0, f"Trace failed with error: {trace.error}")
        
        # Check tool call errors
        tool_errors = sum(1 for tc in trace.tool_calls if tc.error)
        
        if tool_errors == 0:
            return Score(1.0, "No errors")
        elif tool_errors == 1:
            return Score(0.8, f"{tool_errors} tool call failed")
        else:
            return Score(0.6, f"{tool_errors} tool calls failed")

