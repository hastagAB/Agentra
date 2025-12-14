"""
Evaluation orchestrator.
Runs all evaluators on traces and aggregates results.
"""

from .types import Trace, EvaluationResult, CategoryResult, TraceResult, Status
from .evaluators import (
    FunctionalEvaluator,
    ReasoningEvaluator,
    ToolUsageEvaluator,
    PerformanceEvaluator,
    SafetyEvaluator,
    OutputQualityEvaluator,
)


# Default category weights
DEFAULT_WEIGHTS = {
    "functional": 0.20,
    "reasoning": 0.15,
    "tool_usage": 0.15,
    "output_quality": 0.20,
    "performance": 0.15,
    "safety": 0.15,
}


class Evaluator:
    """Orchestrates evaluation across all categories."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.weights = self.config.get("weights", DEFAULT_WEIGHTS)
        
        # Initialize evaluators
        self.evaluators = [
            FunctionalEvaluator(),
            ReasoningEvaluator(),
            ToolUsageEvaluator(),
            OutputQualityEvaluator(),
            PerformanceEvaluator(),
            SafetyEvaluator(),
        ]
    
    def evaluate(
        self,
        traces: list[Trace],
        system_name: str,
        system_description: str = "",
    ) -> EvaluationResult:
        """
        Evaluate traces and produce results.
        """
        
        if not traces:
            # Return empty result
            return self._empty_result(system_name)
        
        # Evaluate each trace
        trace_results = []
        all_category_scores = {e.name: [] for e in self.evaluators}
        
        for trace in traces:
            trace_categories = []
            
            for evaluator in self.evaluators:
                cat_result = evaluator.evaluate(
                    trace,
                    system_description=system_description,
                )
                trace_categories.append(cat_result)
                all_category_scores[evaluator.name].append(cat_result.score)
            
            # Calculate trace score
            trace_score = sum(
                cat.score * self.weights.get(cat.name, 0.1)
                for cat in trace_categories
            )
            
            trace_results.append(TraceResult(
                trace_id=trace.id,
                trace_name=trace.name,
                score=trace_score,
                categories=trace_categories,
                issues=[i for c in trace_categories for i in c.issues],
                input_preview=str(trace.input)[:100] if trace.input else "",
                output_preview=str(trace.output)[:100] if trace.output else "",
                duration_ms=trace.duration_ms,
                llm_calls_count=len(trace.llm_calls),
                tool_calls_count=len(trace.tool_calls),
            ))
        
        # Aggregate category scores
        aggregate_categories = []
        for evaluator in self.evaluators:
            scores = all_category_scores[evaluator.name]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            aggregate_categories.append(CategoryResult(
                name=evaluator.name,
                score=avg_score,
                weight=self.weights.get(evaluator.name, 0.1),
                checks={},  # Aggregate checks if needed
                issues=[],  # Aggregate common issues
            ))
        
        # Calculate overall score
        overall_score = sum(
            cat.score * cat.weight for cat in aggregate_categories
        )
        
        # Determine status
        if overall_score >= 0.9:
            status = Status.EXCELLENT
        elif overall_score >= 0.75:
            status = Status.GOOD
        elif overall_score >= 0.6:
            status = Status.FAIR
        else:
            status = Status.POOR
        
        # Collect all issues and generate recommendations
        all_issues = list(set(i for tr in trace_results for i in tr.issues))
        recommendations = self._generate_recommendations(aggregate_categories, all_issues)
        
        # Generate summary
        summary = self._generate_summary(overall_score, status, traces, all_issues)
        
        return EvaluationResult(
            name="",  # Set when saving
            system_name=system_name,
            score=overall_score,
            status=status,
            categories=aggregate_categories,
            trace_results=trace_results,
            summary=summary,
            issues=all_issues,
            recommendations=recommendations,
            total_traces=len(traces),
            total_llm_calls=sum(len(t.llm_calls) for t in traces),
            total_tool_calls=sum(len(t.tool_calls) for t in traces),
            total_tokens=sum(t.total_tokens for t in traces),
            total_duration_ms=sum(t.duration_ms for t in traces),
            agents_observed=list(set(
                s.name for t in traces for s in t.agent_spans
            )),
            tools_observed=list(set(
                tc.name for t in traces for tc in t.tool_calls
            )),
        )
    
    def _empty_result(self, system_name: str) -> EvaluationResult:
        """Return empty result when no traces."""
        return EvaluationResult(
            name="",
            system_name=system_name,
            score=0.0,
            status=Status.POOR,
            categories=[],
            trace_results=[],
            summary="No traces to evaluate",
            issues=["No traces captured"],
            recommendations=["Run your agent to capture traces"],
            total_traces=0,
            total_llm_calls=0,
            total_tool_calls=0,
            total_tokens=0,
            total_duration_ms=0,
            agents_observed=[],
            tools_observed=[],
        )
    
    def _generate_summary(self, score, status, traces, issues) -> str:
        return f"{len(traces)} traces evaluated. Score: {score:.0%} ({status.value}). {len(issues)} issues found."
    
    def _generate_recommendations(self, categories, issues) -> list[str]:
        recommendations = []
        
        for cat in categories:
            if cat.score < 0.7:
                recommendations.append(f"Improve {cat.name}: score is {cat.score:.0%}")
        
        # Add specific recommendations based on issues
        if any("error" in issue.lower() for issue in issues):
            recommendations.append("Add better error handling")
        
        if any("slow" in issue.lower() or "latency" in issue.lower() for issue in issues):
            recommendations.append("Optimize for performance")
        
        if any("incomplete" in issue.lower() for issue in issues):
            recommendations.append("Ensure outputs fully address inputs")
        
        return recommendations

