"""
Functional evaluator - Does the agent complete tasks correctly?
"""

from .base import BaseEvaluator
from ..types import Trace, CategoryResult, Score
from ..judge import Judge


class FunctionalEvaluator(BaseEvaluator):
    """Evaluates whether the agent completes tasks correctly."""
    
    name = "functional"
    
    def evaluate(self, trace: Trace, system_description: str = "") -> CategoryResult:
        
        checks = {}
        issues = []
        
        judge = Judge()
        
        # Check 1: Task Completion
        if trace.input and trace.output:
            completion_score = judge.evaluate(
                criteria="Did the agent complete the requested task?",
                input=str(trace.input),
                output=str(trace.output),
                context=system_description,
            )
            checks["task_completion"] = completion_score
            
            if completion_score.value < 0.7:
                issues.append(f"Task may be incomplete: {str(trace.input)[:50]}...")
        
        # Check 2: Output Correctness (if no errors)
        if not trace.error:
            correctness_score = judge.evaluate(
                criteria="Is the output correct and appropriate for the input?",
                input=str(trace.input),
                output=str(trace.output),
                context=system_description,
            )
            checks["correctness"] = correctness_score
            
            if correctness_score.value < 0.7:
                issues.append("Output may be incorrect")
        else:
            checks["correctness"] = Score(0.0, f"Error occurred: {trace.error}")
            issues.append(f"Execution error: {trace.error}")
        
        # Check 3: Completeness
        if trace.input and trace.output:
            completeness_score = judge.evaluate(
                criteria="Does the output fully address all aspects of the input request?",
                input=str(trace.input),
                output=str(trace.output),
                context=system_description,
            )
            checks["completeness"] = completeness_score
            
            if completeness_score.value < 0.7:
                issues.append("Response may be incomplete")
        
        # Calculate category score
        avg_score = sum(s.value for s in checks.values()) / len(checks) if checks else 0
        
        return CategoryResult(
            name=self.name,
            score=avg_score,
            weight=0.20,
            checks=checks,
            issues=issues,
        )

