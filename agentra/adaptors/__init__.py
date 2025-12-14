"""
Framework-specific adaptors for richer instrumentation.
"""

from .base import BaseAdaptor
from .crewai import CrewAIAdaptor
from .langchain import LangChainAdaptor
from .langgraph import LangGraphAdaptor
from .autogen import AutoGenAdaptor

__all__ = [
    "BaseAdaptor",
    "CrewAIAdaptor",
    "LangChainAdaptor",
    "LangGraphAdaptor",
    "AutoGenAdaptor",
]

