"""
Generate evaluation reports.
"""

from .types import EvaluationResult


def print_report(result: EvaluationResult):
    """Print detailed report to console."""
    
    print()
    print("=" * 70)
    print(f"  AGENTRA EVALUATION: {result.system_name}")
    print("=" * 70)
    print()
    
    # Overall
    status_icon = {"excellent": "★", "good": "●", "fair": "○", "poor": "✗"}
    icon = status_icon.get(result.status.value, "")
    print(f"  Overall Score: {result.score:.0%} {icon} ({result.status.value})")
    print()
    
    # Stats
    print(f"  Traces: {result.total_traces}")
    print(f"  LLM Calls: {result.total_llm_calls}")
    print(f"  Tool Calls: {result.total_tool_calls}")
    print(f"  Total Tokens: {result.total_tokens:,}")
    print(f"  Total Time: {result.total_duration_ms/1000:.1f}s")
    print()
    
    # Category scores
    print("  CATEGORY SCORES")
    print("  " + "-" * 66)
    
    for cat in sorted(result.categories, key=lambda c: c.score, reverse=True):
        bar_width = 25
        filled = int(cat.score * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        warning = " ⚠" if cat.score < 0.7 else ""
        print(f"  {cat.name:<18} {bar} {cat.score:.0%}{warning}")
    
    print()
    
    # Issues
    if result.issues:
        print("  ISSUES")
        print("  " + "-" * 66)
        for issue in result.issues[:10]:  # Top 10
            print(f"  • {issue}")
        if len(result.issues) > 10:
            print(f"  ... and {len(result.issues) - 10} more")
        print()
    
    # Recommendations
    if result.recommendations:
        print("  RECOMMENDATIONS")
        print("  " + "-" * 66)
        for rec in result.recommendations:
            print(f"  → {rec}")
        print()
    
    # Per-trace breakdown (if few traces)
    if len(result.trace_results) <= 5:
        print("  TRACE BREAKDOWN")
        print("  " + "-" * 66)
        for tr in result.trace_results:
            name = tr.trace_name or tr.trace_id[:8]
            print(f"  {name}: {tr.score:.0%} ({tr.llm_calls_count} LLM, {tr.tool_calls_count} tools, {tr.duration_ms/1000:.1f}s)")
        print()
    
    # Coverage
    if result.agents_observed:
        print(f"  Agents observed: {', '.join(result.agents_observed)}")
    if result.tools_observed:
        print(f"  Tools observed: {', '.join(result.tools_observed)}")
    
    print()
    print("=" * 70)
    print()


def generate_summary(result: EvaluationResult) -> str:
    """Generate one-line summary."""
    return (
        f"{result.total_traces} traces | "
        f"Score: {result.score:.0%} ({result.status.value}) | "
        f"{result.total_llm_calls} LLM calls | "
        f"{len(result.issues)} issues"
    )

