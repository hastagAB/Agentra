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
        try:
            # Hook into agent's generate_reply method
            original_generate_reply = agent.generate_reply
            
            def wrapped_generate_reply(messages=None, sender=None, **kwargs):
                agent_name = getattr(agent, "name", "agent")
                
                self.on_agent_start(
                    name=agent_name,
                    role=getattr(agent, "system_message", None),
                    input=messages[-1] if messages else None
                )
                
                try:
                    reply = original_generate_reply(messages=messages, sender=sender, **kwargs)
                    self.on_agent_end(name=agent_name, output=reply)
                    return reply
                except Exception as e:
                    self.on_agent_end(name=agent_name, error=str(e))
                    raise
            
            agent.generate_reply = wrapped_generate_reply
        except AttributeError:
            # Method doesn't exist or different API
            pass

