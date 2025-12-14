"""
Auto-patch Anthropic client to capture all LLM calls.
"""

import time
from functools import wraps
from datetime import datetime
from ..capture import CaptureContext
from ..types import LLMCall


_original_create = None
_patched = False


def patch_anthropic():
    """Patch Anthropic client to capture calls."""
    global _original_create, _patched
    
    if _patched:
        return
    
    try:
        import anthropic
        
        # Patch messages.create
        _original_create = anthropic.Anthropic.messages.create
        
        def patched_create(self, *args, **kwargs):
            ctx = CaptureContext.get_current()
            start = time.time()
            
            # Call original
            response = _original_create(self, *args, **kwargs)
            
            duration = (time.time() - start) * 1000
            
            # Capture if in traced context
            if ctx:
                ctx.add_llm_call(_extract_llm_call(kwargs, response, duration))
            
            return response
        
        anthropic.Anthropic.messages.create = patched_create
        _patched = True
        
    except ImportError:
        pass  # Anthropic not installed
    except Exception:
        pass  # Other error


def unpatch_anthropic():
    """Restore original Anthropic client."""
    global _original_create, _patched
    
    if _patched and _original_create:
        import anthropic
        anthropic.Anthropic.messages.create = _original_create
        _patched = False


def _extract_llm_call(kwargs: dict, response, duration: float) -> LLMCall:
    """Extract LLMCall from Anthropic request/response."""
    
    # Extract messages
    messages = kwargs.get("messages", [])
    
    # Extract response text with error handling
    response_text = ""
    try:
        if hasattr(response, "content") and response.content:
            if isinstance(response.content, list) and len(response.content) > 0:
                if hasattr(response.content[0], "text"):
                    response_text = response.content[0].text
    except (IndexError, AttributeError, TypeError):
        pass
    
    # Extract token counts with error handling
    tokens_in = 0
    tokens_out = 0
    try:
        if hasattr(response, "usage") and response.usage:
            tokens_in = getattr(response.usage, "input_tokens", 0)
            tokens_out = getattr(response.usage, "output_tokens", 0)
    except (AttributeError, TypeError):
        pass
    
    return LLMCall(
        model=kwargs.get("model", "unknown"),
        messages=messages,
        response=response_text,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        duration_ms=duration,
        timestamp=datetime.now(),
    )

