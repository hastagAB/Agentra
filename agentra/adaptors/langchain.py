"""
LangChain adaptor.
"""

from .base import BaseAdaptor


class LangChainCallbackHandler:
    """LangChain callback handler that feeds into Agentra."""
    
    def __init__(self, adaptor: "LangChainAdaptor"):
        self.adaptor = adaptor
    
    def on_chain_start(self, serialized, inputs, **kwargs):
        chain_name = serialized.get("name", "chain") if isinstance(serialized, dict) else "chain"
        self.adaptor.on_agent_start(chain_name, input=inputs)
    
    def on_chain_end(self, outputs, **kwargs):
        self.adaptor.on_agent_end("chain", output=outputs)
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name", "tool") if isinstance(serialized, dict) else "tool"
        self.adaptor.on_task_start(tool_name, input_str)
    
    def on_tool_end(self, output, **kwargs):
        self.adaptor.on_task_end("tool", output)
    
    def on_retriever_start(self, serialized, query, **kwargs):
        self.adaptor.on_task_start("retriever", query)
    
    def on_retriever_end(self, documents, **kwargs):
        doc_count = len(documents) if documents else 0
        self.adaptor.on_task_end("retriever", f"{doc_count} docs")


class LangChainAdaptor(BaseAdaptor):
    """
    Adaptor for LangChain.
    
    Usage:
        from agentra import Agentra
        from agentra.adaptors import LangChainAdaptor
        
        agentra = Agentra("my-chain")
        adaptor = LangChainAdaptor(agentra)
        
        # Option 1: Get callback handler to pass to chains
        handler = adaptor.get_callback_handler()
        chain.invoke(input, config={"callbacks": [handler]})
        
        # Option 2: Instrument a chain directly
        adaptor.instrument(chain)
        chain.invoke(input)
    """
    
    def get_callback_handler(self):
        """Get callback handler to pass to LangChain."""
        try:
            from langchain_core.callbacks import BaseCallbackHandler
            
            class AgentraCallbackHandler(BaseCallbackHandler):
                def __init__(self, adaptor):
                    super().__init__()
                    self.adaptor = adaptor
                
                def on_chain_start(self, serialized, inputs, **kwargs):
                    chain_name = serialized.get("name", "chain") if isinstance(serialized, dict) else "chain"
                    self.adaptor.on_agent_start(chain_name, input=inputs)
                
                def on_chain_end(self, outputs, **kwargs):
                    self.adaptor.on_agent_end("chain", output=outputs)
                
                def on_tool_start(self, serialized, input_str, **kwargs):
                    tool_name = serialized.get("name", "tool") if isinstance(serialized, dict) else "tool"
                    self.adaptor.on_task_start(tool_name, input_str)
                
                def on_tool_end(self, output, **kwargs):
                    self.adaptor.on_task_end("tool", output)
            
            return AgentraCallbackHandler(self)
        except ImportError:
            # Fallback to simple callback
            return LangChainCallbackHandler(self)
    
    def instrument(self, chain) -> None:
        """Instrument a LangChain chain/agent."""
        
        original_invoke = chain.invoke
        handler = self.get_callback_handler()
        
        def wrapped_invoke(input, config=None, **kwargs):
            config = config or {}
            callbacks = config.get("callbacks", [])
            callbacks.append(handler)
            config["callbacks"] = callbacks
            
            with self.agentra.trace():
                return original_invoke(input, config=config, **kwargs)
        
        chain.invoke = wrapped_invoke

