"""
Reasoning evaluator - Does the agent reason effectively?
"""

from .base import BaseEvaluator
from ..types import Trace, CategoryResult, Score
from ..judge import Judge


class ReasoningEvaluator(BaseEvaluator):
    """Evaluates the quality of agent reasoning."""
    
    name = "reasoning"
    
    def evaluate(self, trace: Trace, system_description: str = "") -> CategoryResult:
        
        checks = {}
        issues = []
        
        judge = Judge()
        
        # Check 1: Logical Consistency
        if trace.llm_calls:
            # Examine LLM interactions for logical flow
            conversation = self._extract_conversation(trace)
            
            if conversation:
                logic_score = judge.evaluate(
                    criteria="Is the agent's reasoning logical and consistent?",
                    input=str(trace.input) if trace.input else "N/A",
                    output=conversation,
                    context=system_description,
                )
                checks["logical_consistency"] = logic_score
                
                if logic_score.value < 0.7:
                    issues.append("Reasoning may be inconsistent or illogical")
        
        # Check 2: Appropriate Tool Selection
        if trace.tool_calls:
            tool_appropriateness = self._evaluate_tool_selection(trace)
            checks["tool_selection"] = tool_appropriateness
            
            if tool_appropriateness.value < 0.7:
                issues.append("Tool selection may be suboptimal")
        
        # Check 3: Steps to Solution
        steps_efficiency = self._evaluate_efficiency(trace)
        checks["efficiency"] = steps_efficiency
        
        if steps_efficiency.value < 0.7:
            issues.append("Agent may be taking inefficient steps")
        
        # Calculate category score
        avg_score = sum(s.value for s in checks.values()) / len(checks) if checks else 0.5
        
        return CategoryResult(
            name=self.name,
            score=avg_score,
            weight=0.15,
            checks=checks,
            issues=issues,
        )
    
    def _extract_conversation(self, trace: Trace) -> str:
        """Extract conversation text from LLM calls."""
        parts = []
        for call in trace.llm_calls[:3]:  # Limit to first 3 for brevity
            if call.messages:
                last_msg = call.messages[-1] if isinstance(call.messages, list) else {}
                if isinstance(last_msg, dict):
                    parts.append(f"Query: {last_msg.get('content', '')[:200]}")
            parts.append(f"Response: {call.response[:200]}")
        return "\n".join(parts)
    
    def _evaluate_tool_selection(self, trace: Trace) -> Score:
        """Evaluate if tools were used appropriately."""
        # Simple heuristic: check for tool errors
        errors = sum(1 for tc in trace.tool_calls if tc.error)
        error_rate = errors / len(trace.tool_calls) if trace.tool_calls else 0
        
        if error_rate > 0.3:
            return Score(
                value=0.4,
                reason=f"{error_rate:.0%} of tool calls failed",
                details={"error_rate": error_rate}
            )
        elif error_rate > 0.1:
            return Score(
                value=0.7,
                reason=f"{error_rate:.0%} of tool calls failed",
                details={"error_rate": error_rate}
            )
        else:
            return Score(
                value=0.9,
                reason="Tool calls executed successfully",
                details={"error_rate": error_rate}
            )
    
    def _evaluate_efficiency(self, trace: Trace) -> Score:
        """Evaluate efficiency of steps taken."""
        # Simple heuristic: ratio of LLM calls to complexity
        llm_count = len(trace.llm_calls)
        
        if llm_count == 0:
            return Score(0.5, "No LLM calls to evaluate")
        
        if llm_count > 10:
            return Score(
                0.6,
                f"High number of LLM calls ({llm_count}) may indicate inefficiency",
                details={"llm_calls": llm_count}
            )
        elif llm_count > 5:
            return Score(
                0.8,
                f"Moderate number of LLM calls ({llm_count})",
                details={"llm_calls": llm_count}
            )
        else:
            return Score(
                0.9,
                f"Efficient use of LLM calls ({llm_count})",
                details={"llm_calls": llm_count}
            )

