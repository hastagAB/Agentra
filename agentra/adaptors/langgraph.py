"""
LangGraph adaptor.
"""

from .base import BaseAdaptor


class LangGraphAdaptor(BaseAdaptor):
    """
    Adaptor for LangGraph.
    
    Captures:
    - Node executions
    - Edge transitions
    - State changes
    - Branch decisions
    
    Usage:
        from agentra import Agentra
        from agentra.adaptors import LangGraphAdaptor
        from langgraph.graph import StateGraph
        
        agentra = Agentra("my-graph")
        
        workflow = StateGraph(State)
        workflow.add_node(...)
        app = workflow.compile()
        
        LangGraphAdaptor(agentra).instrument(app)
        
        app.invoke({"input": "..."})
        agentra.evaluate()
    """
    
    def instrument(self, app) -> None:
        """Instrument a compiled LangGraph app."""
        
        original_invoke = app.invoke
        
        def wrapped_invoke(input, config=None, **kwargs):
            with self.agentra.trace():
                # Track node executions via config
                config = config or {}
                
                # LangGraph uses LangChain-style callbacks
                try:
                    from .langchain import LangChainAdaptor
                    langchain_adaptor = LangChainAdaptor(self.agentra)
                    handler = langchain_adaptor.get_callback_handler()
                    
                    callbacks = config.get("callbacks", [])
                    callbacks.append(handler)
                    config["callbacks"] = callbacks
                except:
                    pass
                
                return original_invoke(input, config=config, **kwargs)
        
        app.invoke = wrapped_invoke

