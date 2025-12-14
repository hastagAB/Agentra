"""
Tool usage evaluator - Does the agent use tools effectively?
"""

from .base import BaseEvaluator
from ..types import Trace, CategoryResult, Score


class ToolUsageEvaluator(BaseEvaluator):
    """Evaluates tool/function usage quality."""
    
    name = "tool_usage"
    
    def evaluate(self, trace: Trace, system_description: str = "") -> CategoryResult:
        
        checks = {}
        issues = []
        
        if not trace.tool_calls:
            # No tools used - not necessarily bad
            return CategoryResult(
                name=self.name,
                score=0.8,
                weight=0.15,
                checks={"no_tools": Score(0.8, "No tools were called")},
                issues=[],
            )
        
        # Check 1: Tool Success Rate
        success_rate = self._calculate_success_rate(trace)
        checks["success_rate"] = success_rate
        
        if success_rate.value < 0.7:
            issues.append(f"Tool success rate is low: {success_rate.value:.0%}")
        
        # Check 2: Tool Diversity (using multiple tools appropriately)
        diversity_score = self._evaluate_diversity(trace)
        checks["diversity"] = diversity_score
        
        # Check 3: Tool Latency
        latency_score = self._evaluate_latency(trace)
        checks["latency"] = latency_score
        
        if latency_score.value < 0.7:
            issues.append("Tool calls are slow")
        
        # Calculate category score
        avg_score = sum(s.value for s in checks.values()) / len(checks)
        
        return CategoryResult(
            name=self.name,
            score=avg_score,
            weight=0.15,
            checks=checks,
            issues=issues,
        )
    
    def _calculate_success_rate(self, trace: Trace) -> Score:
        """Calculate tool call success rate."""
        total = len(trace.tool_calls)
        errors = sum(1 for tc in trace.tool_calls if tc.error)
        success_rate = (total - errors) / total if total > 0 else 1.0
        
        return Score(
            value=success_rate,
            reason=f"{errors} of {total} tool calls failed" if errors > 0 else "All tool calls succeeded",
            details={"total": total, "errors": errors, "success_rate": success_rate}
        )
    
    def _evaluate_diversity(self, trace: Trace) -> Score:
        """Evaluate tool diversity (not calling same tool repeatedly unnecessarily)."""
        if not trace.tool_calls:
            return Score(1.0, "N/A")
        
        tool_names = [tc.name for tc in trace.tool_calls]
        unique_tools = len(set(tool_names))
        total_calls = len(tool_names)
        
        diversity_ratio = unique_tools / total_calls if total_calls > 0 else 1.0
        
        if diversity_ratio > 0.7:
            return Score(0.9, f"Good tool diversity ({unique_tools} unique tools)")
        elif diversity_ratio > 0.4:
            return Score(0.7, f"Moderate tool diversity ({unique_tools} unique tools)")
        else:
            return Score(0.5, f"Low tool diversity - may be overusing specific tools")
    
    def _evaluate_latency(self, trace: Trace) -> Score:
        """Evaluate tool call latency."""
        if not trace.tool_calls:
            return Score(1.0, "N/A")
        
        avg_latency = sum(tc.duration_ms for tc in trace.tool_calls) / len(trace.tool_calls)
        
        if avg_latency < 500:  # < 0.5s
            return Score(0.9, f"Fast tool calls (avg {avg_latency:.0f}ms)")
        elif avg_latency < 2000:  # < 2s
            return Score(0.7, f"Moderate tool latency (avg {avg_latency:.0f}ms)")
        else:
            return Score(0.5, f"Slow tool calls (avg {avg_latency:.0f}ms)")

