"""
Main Agentra class - primary interface for agent instrumentation.
"""

import random
from functools import wraps
from typing import Callable, Any, Optional
from contextlib import contextmanager

from .types import Trace, EvaluationResult
from .capture import CaptureContext
from .evaluate import Evaluator
from .report import print_report, generate_summary
from .results import save_result, load_result, list_results, compare_results


class Agentra:
    """
    Main interface for agent instrumentation and evaluation.
    
    Usage:
        agentra = Agentra("my-system")
        
        @agentra.wrap
        def my_agent(query):
            ...
        
        my_agent("do something")
        
        result = agentra.evaluate()
        agentra.save("my-test-run")
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        auto_patch: bool = True,
        sample_rate: float = 1.0,
        results_dir: str = "agentra-results",
    ):
        """
        Initialize Agentra.
        
        Args:
            name: Name of the system being evaluated
            description: Description of what the system does
            auto_patch: Whether to auto-patch LLM clients
            sample_rate: Fraction of runs to capture (for production)
            results_dir: Directory to save results
        """
        self.name = name
        self.description = description
        self.sample_rate = sample_rate
        self.results_dir = results_dir
        
        # Storage for captured traces
        self._traces: list[Trace] = []
        
        # Latest evaluation result
        self._latest_result: Optional[EvaluationResult] = None
        
        # Auto-patch LLM clients
        if auto_patch:
            self._apply_patches()
    
    def _apply_patches(self):
        """Apply auto-patching to LLM clients."""
        try:
            from .patches import patch_openai, patch_anthropic, patch_litellm
            patch_openai()
            patch_anthropic()
            patch_litellm()
        except Exception as e:
            # Silently fail if patches can't be applied
            pass
    
    def wrap(self, fn: Callable) -> Callable:
        """
        Decorator to wrap agent entry point.
        
        @agentra.wrap
        def my_agent(query):
            ...
        """
        
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Sample check
            if random.random() > self.sample_rate:
                return fn(*args, **kwargs)
            
            # Create capture context
            with self.trace() as ctx:
                # Capture input (first arg or all args/kwargs)
                if args:
                    ctx.set_input(args[0] if len(args) == 1 else {"args": args, "kwargs": kwargs})
                elif kwargs:
                    ctx.set_input(kwargs)
                
                # Execute function
                result = fn(*args, **kwargs)
                
                # Capture output
                ctx.set_output(result)
                
                return result
        
        return wrapper
    
    @contextmanager
    def trace(self, name: str = None):
        """
        Context manager for manual tracing.
        
        with agentra.trace("test-case-1") as t:
            result = my_agent(query)
            t.set_output(result)
        """
        ctx = CaptureContext(name)
        
        with ctx:
            yield ctx
        
        # Store completed trace
        self._traces.append(ctx.trace)
    
    @contextmanager
    def agent(self, name: str, role: str = None):
        """
        Context manager to mark agent boundaries.
        
        with agentra.agent("router"):
            decision = router.decide(task)
        """
        ctx = CaptureContext.get_current()
        
        if ctx:
            ctx.start_agent_span(name, role)
        
        try:
            yield
        finally:
            if ctx:
                ctx.end_agent_span(name)
    
    # ─────────────────────────────────────────────────────────────
    # Results
    # ─────────────────────────────────────────────────────────────
    
    def evaluate(self, config: dict = None) -> EvaluationResult:
        """
        Evaluate all captured traces.
        
        Args:
            config: Optional evaluation config (weights, thresholds, etc.)
        
        Returns:
            EvaluationResult
        """
        evaluator = Evaluator(config)
        result = evaluator.evaluate(
            traces=self._traces,
            system_name=self.name,
            system_description=self.description,
        )
        
        self._latest_result = result
        return result
    
    def summary(self) -> str:
        """Quick one-line summary."""
        if not self._latest_result:
            return f"No evaluation yet. {len(self._traces)} traces captured."
        
        return generate_summary(self._latest_result)
    
    def report(self):
        """Print detailed report to console."""
        if not self._latest_result:
            # Auto-evaluate if not done yet
            self._latest_result = self.evaluate()
        
        print_report(self._latest_result)
    
    def save(self, name: str) -> str:
        """
        Save results to agentra-results/{name}.json
        
        Args:
            name: Name for this result file (e.g., "auth-flow-test")
        
        Returns:
            Path to saved file
        """
        if not self._latest_result:
            # Auto-evaluate if not done yet
            self._latest_result = self.evaluate()
        
        filepath = save_result(self._latest_result, name, self.results_dir)
        return filepath
    
    @staticmethod
    def load(name: str, results_dir: str = "agentra-results") -> EvaluationResult:
        """Load previously saved results."""
        return load_result(name, results_dir)
    
    @staticmethod
    def list_results(results_dir: str = "agentra-results") -> list[str]:
        """List all saved result files."""
        return list_results(results_dir)
    
    @staticmethod
    def compare(names: list[str], results_dir: str = "agentra-results") -> str:
        """Compare multiple saved results."""
        return compare_results(names, results_dir)
    
    # ─────────────────────────────────────────────────────────────
    # Data access
    # ─────────────────────────────────────────────────────────────
    
    def get_traces(self) -> list[Trace]:
        """Get all captured traces."""
        return self._traces.copy()
    
    def clear(self):
        """Clear captured traces."""
        self._traces = []
        self._latest_result = None
    
    def coverage(self) -> dict:
        """Get coverage report - what agents/tools were exercised."""
        agents = set()
        tools = set()
        
        for trace in self._traces:
            agents.update(span.name for span in trace.agent_spans)
            tools.update(tc.name for tc in trace.tool_calls)
        
        return {
            "agents": list(agents),
            "tools": list(tools),
            "traces": len(self._traces),
            "llm_calls": sum(len(t.llm_calls) for t in self._traces),
            "tool_calls": sum(len(t.tool_calls) for t in self._traces),
        }
    
    def export(self, path: str):
        """Export traces to JSON file."""
        import json
        from dataclasses import asdict
        
        data = {
            "system_name": self.name,
            "system_description": self.description,
            "traces": [asdict(t) for t in self._traces],
        }
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

