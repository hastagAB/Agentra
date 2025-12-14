"""
Core data types for Agentra.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from enum import Enum


# ─────────────────────────────────────────────────────────────────
# TRACE DATA - What we capture
# ─────────────────────────────────────────────────────────────────

@dataclass
class LLMCall:
    """Single LLM invocation."""
    model: str
    messages: list[dict]
    response: str
    tokens_in: int = 0
    tokens_out: int = 0
    duration_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)  # agent_name, node_name, etc.


@dataclass
class ToolCall:
    """Single tool/function call."""
    name: str
    input: dict
    output: Any = None
    error: str | None = None
    duration_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentSpan:
    """Tracks one agent's execution (for multi-agent systems)."""
    name: str
    role: str | None = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    llm_calls: list[LLMCall] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    input: Any = None
    output: Any = None
    error: str | None = None


@dataclass
class Trace:
    """Complete trace of one execution."""
    id: str
    name: str | None = None  # User-provided name for this run
    input: Any = None
    output: Any = None
    
    # Captured data
    llm_calls: list[LLMCall] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    agent_spans: list[AgentSpan] = field(default_factory=list)  # For multi-agent
    
    # Metadata
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    duration_ms: float = 0
    error: str | None = None
    framework: str | None = None  # "crewai", "langchain", etc.
    metadata: dict = field(default_factory=dict)
    
    @property
    def total_tokens(self) -> int:
        return sum(c.tokens_in + c.tokens_out for c in self.llm_calls)
    
    @property 
    def total_cost(self) -> float:
        # Rough estimate - can be made more accurate
        return self.total_tokens * 0.00001


# ─────────────────────────────────────────────────────────────────
# EVALUATION RESULTS
# ─────────────────────────────────────────────────────────────────

@dataclass
class Score:
    """Single evaluation score."""
    value: float  # 0.0 to 1.0
    reason: str
    details: dict = field(default_factory=dict)


@dataclass
class CategoryResult:
    """Results for one evaluation category."""
    name: str
    score: float
    weight: float
    checks: dict[str, Score]
    issues: list[str] = field(default_factory=list)


@dataclass
class TraceResult:
    """Evaluation result for a single trace."""
    trace_id: str
    trace_name: str | None
    score: float
    categories: list[CategoryResult]
    issues: list[str]
    input_preview: str  # First 100 chars of input
    output_preview: str  # First 100 chars of output
    duration_ms: float
    llm_calls_count: int
    tool_calls_count: int


class Status(Enum):
    EXCELLENT = "excellent"  # >= 0.9
    GOOD = "good"            # >= 0.75
    FAIR = "fair"            # >= 0.6
    POOR = "poor"            # < 0.6


@dataclass
class EvaluationResult:
    """Complete evaluation results."""
    name: str  # Result file name
    system_name: str
    
    # Aggregate scores
    score: float
    status: Status
    
    # Per-category aggregates
    categories: list[CategoryResult]
    
    # Per-trace results
    trace_results: list[TraceResult]
    
    # Summary
    summary: str
    issues: list[str]
    recommendations: list[str]
    
    # Stats
    total_traces: int
    total_llm_calls: int
    total_tool_calls: int
    total_tokens: int
    total_duration_ms: float
    
    # Coverage (what was exercised)
    agents_observed: list[str]
    tools_observed: list[str]
    
    # Meta
    timestamp: datetime = field(default_factory=datetime.now)
    agentra_version: str = "0.1.0"

