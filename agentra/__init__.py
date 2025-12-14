"""
Agentra - Live Agent Instrumentation & Evaluation

A lightweight Python library for capturing execution traces and evaluating
AI agent performance.
"""

from .agentra import Agentra
from .types import (
    Trace,
    LLMCall,
    ToolCall,
    AgentSpan,
    Score,
    CategoryResult,
    TraceResult,
    EvaluationResult,
    Status,
)

__version__ = "0.1.0"

__all__ = [
    "Agentra",
    "Trace",
    "LLMCall",
    "ToolCall",
    "AgentSpan",
    "Score",
    "CategoryResult",
    "TraceResult",
    "EvaluationResult",
    "Status",
]

