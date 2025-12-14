"""
AutoGen adaptor.
"""

from .base import BaseAdaptor


class AutoGenAdaptor(BaseAdaptor):
    """
    Adaptor for Microsoft AutoGen.
    
    Captures:
    - Agent conversations
    - Message passing
    - Termination conditions
    
    Usage:
        from agentra import Agentra
        from agentra.adaptors import AutoGenAdaptor
        import autogen
        
        agentra = Agentra("autogen-system")
        
        assistant = autogen.AssistantAgent(...)
        user_proxy = autogen.UserProxyAgent(...)
        
        adaptor = AutoGenAdaptor(agentra)
        adaptor.instrument_agents([assistant, user_proxy])
        
        user_proxy.initiate_chat(assistant, message="...")
        
        agentra.evaluate()
    """
    
    def instrument(self, target) -> None:
        """
        Instrument AutoGen agents or group chat.
        
        Args:
            target: Can be a single agent, list of agents, or GroupChat
        """
        # Handle different target types
        if isinstance(target, list):
            self.instrument_agents(target)
        else:
            self.instrument_agent(target)
    
    def instrument_agents(self, agents: list):
        """Instrument multiple AutoGen agents."""
        for agent in agents:
            self.instrument_agent(agent)
    
    def instrument_agent(self, agent):
        """Instrument a single AutoGen agent."""
        # Try multiple possible method names
        methods_to_try = ['generate_reply', 'generate_response', 'reply']
        
        for method_name in methods_to_try:
            if not hasattr(agent, method_name):
                continue
            
            try:
                original_method = getattr(agent, method_name)
                if not callable(original_method):
                    continue
                
                def make_wrapper(original):
                    def wrapped_method(messages=None, sender=None, **kwargs):
                        agent_name = getattr(agent, "name", "agent")
                        
                        # Extract last message safely
                        last_msg = None
                        if messages:
                            try:
                                last_msg = messages[-1] if isinstance(messages, list) else str(messages)[:100]
                            except (IndexError, TypeError):
                                pass
                        
                        self.on_agent_start(
                            name=agent_name,
                            role=getattr(agent, "system_message", None),
                            input=last_msg
                        )
                        
                        try:
                            reply = original(messages=messages, sender=sender, **kwargs)
                            self.on_agent_end(name=agent_name, output=reply)
                            return reply
                        except Exception as e:
                            self.on_agent_end(name=agent_name, error=str(e))
                            raise
                    return wrapped_method
                
                setattr(agent, method_name, make_wrapper(original_method))
                break  # Successfully patched
            except (AttributeError, TypeError):
                continue

