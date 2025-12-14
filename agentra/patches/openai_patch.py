"""
Auto-patch OpenAI client to capture all LLM calls.
"""

import time
from functools import wraps
from datetime import datetime
from ..capture import CaptureContext
from ..types import LLMCall


_original_create = None
_original_async_create = None
_patched = False


def patch_openai():
    """Patch OpenAI client to capture calls."""
    global _original_create, _original_async_create, _patched
    
    if _patched:
        return
    
    try:
        import openai
        
        # Patch sync create
        _original_create = openai.chat.completions.create
        
        @wraps(_original_create)
        def patched_create(*args, **kwargs):
            ctx = CaptureContext.get_current()
            start = time.time()
            
            # Call original
            response = _original_create(*args, **kwargs)
            
            duration = (time.time() - start) * 1000
            
            # Capture if in traced context
            if ctx:
                ctx.add_llm_call(_extract_llm_call(kwargs, response, duration))
            
            return response
        
        openai.chat.completions.create = patched_create
        
        # Patch async create if available
        try:
            from openai import AsyncOpenAI
            _original_async_create = AsyncOpenAI().chat.completions.create
            
            async def patched_async_create(self, *args, **kwargs):
                ctx = CaptureContext.get_current()
                start = time.time()
                
                # Call original
                response = await _original_async_create(*args, **kwargs)
                
                duration = (time.time() - start) * 1000
                
                # Capture if in traced context
                if ctx:
                    ctx.add_llm_call(_extract_llm_call(kwargs, response, duration))
                
                return response
            
            # This patching is simplified - in production you'd need more careful async patching
        except:
            pass
        
        _patched = True
        
    except ImportError:
        pass  # OpenAI not installed


def unpatch_openai():
    """Restore original OpenAI client."""
    global _original_create, _patched
    
    if _patched and _original_create:
        import openai
        openai.chat.completions.create = _original_create
        _patched = False


def _extract_llm_call(kwargs: dict, response, duration: float) -> LLMCall:
    """Extract LLMCall from OpenAI request/response."""
    
    # Extract messages
    messages = kwargs.get("messages", [])
    
    # Extract response text
    response_text = ""
    if hasattr(response, "choices") and response.choices:
        if hasattr(response.choices[0], "message"):
            response_text = response.choices[0].message.content or ""
    
    # Extract token counts
    tokens_in = 0
    tokens_out = 0
    if hasattr(response, "usage"):
        tokens_in = response.usage.prompt_tokens if hasattr(response.usage, "prompt_tokens") else 0
        tokens_out = response.usage.completion_tokens if hasattr(response.usage, "completion_tokens") else 0
    
    return LLMCall(
        model=kwargs.get("model", "unknown"),
        messages=messages,
        response=response_text,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        duration_ms=duration,
        timestamp=datetime.now(),
    )

