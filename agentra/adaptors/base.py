"""
Base adaptor class.
"""

from abc import ABC, abstractmethod
from typing import Any
from ..capture import CaptureContext


class BaseAdaptor(ABC):
    """
    Base class for framework-specific adaptors.
    
    Adaptors hook into framework internals to capture
    additional structure beyond LLM/tool calls.
    """
    
    def __init__(self, agentra: "Agentra"):
        self.agentra = agentra
    
    @abstractmethod
    def instrument(self, target) -> None:
        """
        Instrument a framework object (Crew, Chain, Graph, etc.)
        
        This should set up callbacks/hooks to capture:
        - Agent boundaries
        - Task/node transitions
        - Framework-specific events
        """
        pass
    
    def on_agent_start(self, name: str, role: str = None, input: Any = None):
        """Called when an agent starts."""
        ctx = CaptureContext.get_current()
        if ctx:
            ctx.start_agent_span(name, role, input)
    
    def on_agent_end(self, name: str, output: Any = None, error: str = None):
        """Called when an agent ends."""
        ctx = CaptureContext.get_current()
        if ctx:
            ctx.end_agent_span(name, output, error)
    
    def on_task_start(self, task_name: str, task_input: Any = None):
        """Called when a task starts."""
        ctx = CaptureContext.get_current()
        if ctx:
            ctx.add_event("task_start", {"name": task_name, "input": task_input})
    
    def on_task_end(self, task_name: str, task_output: Any = None):
        """Called when a task ends."""
        ctx = CaptureContext.get_current()
        if ctx:
            ctx.add_event("task_end", {"name": task_name, "output": task_output})

