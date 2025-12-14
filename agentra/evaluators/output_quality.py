"""
Output quality evaluator - Clarity, completeness, format.
"""

from .base import BaseEvaluator
from ..types import Trace, CategoryResult, Score
from ..judge import Judge


class OutputQualityEvaluator(BaseEvaluator):
    """Evaluates the quality of agent outputs."""
    
    name = "output_quality"
    
    def evaluate(self, trace: Trace, system_description: str = "") -> CategoryResult:
        
        checks = {}
        issues = []
        
        if not trace.output:
            return CategoryResult(
                name=self.name,
                score=0.0,
                weight=0.20,
                checks={"no_output": Score(0.0, "No output generated")},
                issues=["No output generated"],
            )
        
        judge = Judge()
        
        # Check 1: Clarity
        clarity_score = judge.evaluate(
            criteria="Is the output clear, well-structured, and easy to understand?",
            input=str(trace.input) if trace.input else "",
            output=str(trace.output),
            context=system_description,
        )
        checks["clarity"] = clarity_score
        
        if clarity_score.value < 0.7:
            issues.append("Output may be unclear or poorly structured")
        
        # Check 2: Completeness
        completeness_score = judge.evaluate(
            criteria="Is the output complete and comprehensive?",
            input=str(trace.input) if trace.input else "",
            output=str(trace.output),
            context=system_description,
        )
        checks["completeness"] = completeness_score
        
        if completeness_score.value < 0.7:
            issues.append("Output may be incomplete")
        
        # Check 3: Format Quality
        format_score = self._evaluate_format(trace)
        checks["format"] = format_score
        
        if format_score.value < 0.7:
            issues.append("Output format may be inconsistent")
        
        # Calculate category score
        avg_score = sum(s.value for s in checks.values()) / len(checks)
        
        return CategoryResult(
            name=self.name,
            score=avg_score,
            weight=0.20,
            checks=checks,
            issues=issues,
        )
    
    def _evaluate_format(self, trace: Trace) -> Score:
        """Evaluate output format quality."""
        output_str = str(trace.output)
        
        # Simple heuristics for format quality
        issues = []
        
        # Check for extremely short outputs (unless that's appropriate)
        if len(output_str.strip()) < 10:
            issues.append("Output is very short")
        
        # Check for excessive repetition (same word repeated many times)
        words = output_str.lower().split()
        if words:
            max_repetition = max(words.count(word) for word in set(words))
            if max_repetition > 10:
                issues.append("Excessive word repetition")
        
        # Check for all caps (shouting)
        if len(output_str) > 20 and output_str.isupper():
            issues.append("Output is all uppercase")
        
        if issues:
            return Score(
                0.6,
                f"Format issues: {', '.join(issues)}",
                details={"issues": issues}
            )
        
        return Score(0.9, "Output format appears good")

