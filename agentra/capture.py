"""
Context management for trace capture.
Uses contextvars to track current trace across async boundaries.
"""

from contextvars import ContextVar
from typing import Optional
import uuid
import time

from .types import Trace, LLMCall, ToolCall, AgentSpan


# Current trace being recorded
_current_context: ContextVar[Optional["CaptureContext"]] = ContextVar(
    "agentra_context", default=None
)


class CaptureContext:
    """
    Context for capturing a single trace.
    
    Used internally by Agentra.wrap and agentra.trace()
    """
    
    def __init__(self, name: str = None):
        self.trace = Trace(
            id=str(uuid.uuid4()),
            name=name,
        )
        self._agent_stack: list[AgentSpan] = []
        self._token = None
        self._start_time = None
    
    def __enter__(self):
        self._token = _current_context.set(self)
        self._start_time = time.time()
        self.trace.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        self.trace.end_time = datetime.now()
        self.trace.duration_ms = (end_time - self._start_time) * 1000
        
        if exc_val:
            self.trace.error = str(exc_val)
        
        _current_context.reset(self._token)
    
    @staticmethod
    def get_current() -> Optional["CaptureContext"]:
        """Get current capture context (if any)."""
        return _current_context.get()
    
    def set_input(self, input):
        self.trace.input = input
    
    def set_output(self, output):
        self.trace.output = output
    
    def add_llm_call(self, call: LLMCall):
        self.trace.llm_calls.append(call)
        
        # Also add to current agent span if any
        if self._agent_stack:
            self._agent_stack[-1].llm_calls.append(call)
    
    def add_tool_call(self, call: ToolCall):
        self.trace.tool_calls.append(call)
        
        if self._agent_stack:
            self._agent_stack[-1].tool_calls.append(call)
    
    def start_agent_span(self, name: str, role: str = None, input=None):
        span = AgentSpan(name=name, role=role, input=input)
        self._agent_stack.append(span)
        self.trace.agent_spans.append(span)
    
    def end_agent_span(self, name: str, output=None, error: str = None):
        if self._agent_stack and self._agent_stack[-1].name == name:
            span = self._agent_stack.pop()
            span.end_time = datetime.now()
            span.output = output
            span.error = error
    
    def add_event(self, event_type: str, data: dict):
        """Add generic event to trace metadata."""
        if "events" not in self.trace.metadata:
            self.trace.metadata["events"] = []
        self.trace.metadata["events"].append({
            "type": event_type,
            "data": data,
            "timestamp": time.time(),
        })


# Import datetime here to avoid circular import
from datetime import datetime

