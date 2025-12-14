"""
Auto-patching for LLM clients.
"""

from .openai_patch import patch_openai, unpatch_openai
from .anthropic_patch import patch_anthropic, unpatch_anthropic
from .litellm_patch import patch_litellm, unpatch_litellm

__all__ = [
    "patch_openai",
    "unpatch_openai",
    "patch_anthropic",
    "unpatch_anthropic",
    "patch_litellm",
    "unpatch_litellm",
]

