"""
CrewAI adaptor.
"""

from .base import BaseAdaptor


class CrewAIAdaptor(BaseAdaptor):
    """
    Adaptor for CrewAI framework.
    
    Captures:
    - Agent roles and goals
    - Task execution order
    - Agent delegation
    - Crew workflow
    
    Usage:
        from agentra import Agentra
        from agentra.adaptors import CrewAIAdaptor
        from crewai import Crew
        
        agentra = Agentra("my-crew")
        crew = Crew(agents=[...], tasks=[...])
        
        CrewAIAdaptor(agentra).instrument(crew)
        
        crew.kickoff()
        agentra.evaluate()
    """
    
    def instrument(self, crew) -> None:
        """Instrument a CrewAI Crew instance."""
        
        # Store original kickoff
        original_kickoff = crew.kickoff
        
        def wrapped_kickoff(*args, **kwargs):
            # Start trace
            with self.agentra.trace(f"crew-{getattr(crew, 'id', 'run')}"):
                # Set up agent callbacks
                for agent in getattr(crew, "agents", []):
                    self._instrument_agent(agent)
                
                # Run crew
                result = original_kickoff(*args, **kwargs)
                
                return result
        
        crew.kickoff = wrapped_kickoff
        
        # Store crew info in agentra metadata
        try:
            self.agentra._crew_info = {
                "agents": [
                    {"role": getattr(a, "role", "unknown"), "goal": getattr(a, "goal", "")}
                    for a in getattr(crew, "agents", [])
                ],
                "tasks": [
                    {"description": getattr(t, "description", "")}
                    for t in getattr(crew, "tasks", [])
                ],
            }
        except:
            pass
    
    def _instrument_agent(self, agent):
        """Add callbacks to a CrewAI agent."""
        # Hook into agent's execute method to track agent spans
        # This is simplified - actual implementation depends on CrewAI version
        
        try:
            original_execute = agent.execute_task
            
            def wrapped_execute(task, *args, **kwargs):
                agent_name = getattr(agent, "role", "agent")
                
                self.on_agent_start(
                    name=agent_name,
                    role=getattr(agent, "role", None),
                    input=getattr(task, "description", None)
                )
                
                try:
                    result = original_execute(task, *args, **kwargs)
                    self.on_agent_end(name=agent_name, output=result)
                    return result
                except Exception as e:
                    self.on_agent_end(name=agent_name, error=str(e))
                    raise
            
            agent.execute_task = wrapped_execute
        except AttributeError:
            # Method doesn't exist or different API
            pass

