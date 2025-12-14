"""
Auto-patch LiteLLM to capture all LLM calls.
"""

import time
from functools import wraps
from datetime import datetime
from ..capture import CaptureContext
from ..types import LLMCall


_original_completion = None
_patched = False


def patch_litellm():
    """Patch LiteLLM to capture calls."""
    global _original_completion, _patched
    
    if _patched:
        return
    
    try:
        import litellm
        
        # Patch litellm.completion
        _original_completion = litellm.completion
        
        @wraps(_original_completion)
        def patched_completion(*args, **kwargs):
            ctx = CaptureContext.get_current()
            start = time.time()
            
            # Call original
            response = _original_completion(*args, **kwargs)
            
            duration = (time.time() - start) * 1000
            
            # Capture if in traced context
            if ctx:
                ctx.add_llm_call(_extract_llm_call(kwargs, response, duration))
            
            return response
        
        litellm.completion = patched_completion
        _patched = True
        
    except ImportError:
        pass  # LiteLLM not installed


def unpatch_litellm():
    """Restore original LiteLLM."""
    global _original_completion, _patched
    
    if _patched and _original_completion:
        import litellm
        litellm.completion = _original_completion
        _patched = False


def _extract_llm_call(kwargs: dict, response, duration: float) -> LLMCall:
    """Extract LLMCall from LiteLLM request/response."""
    
    # Extract messages
    messages = kwargs.get("messages", [])
    
    # Extract response text with error handling
    response_text = ""
    try:
        if hasattr(response, "choices") and response.choices:
            choice = response.choices[0]
            if hasattr(choice, "message") and choice.message:
                response_text = choice.message.content or ""
    except (IndexError, AttributeError, TypeError):
        pass
    
    # Extract token counts with error handling
    tokens_in = 0
    tokens_out = 0
    try:
        if hasattr(response, "usage") and response.usage:
            tokens_in = getattr(response.usage, "prompt_tokens", 0)
            tokens_out = getattr(response.usage, "completion_tokens", 0)
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

