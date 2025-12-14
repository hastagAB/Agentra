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
        # Try multiple possible method names based on CrewAI version
        methods_to_try = ['execute_task', 'execute', 'run']
        
        for method_name in methods_to_try:
            if not hasattr(agent, method_name):
                continue
            
            try:
                original_method = getattr(agent, method_name)
                if not callable(original_method):
                    continue
                
                def make_wrapper(original):
                    def wrapped_execute(task, *args, **kwargs):
                        agent_name = getattr(agent, "role", getattr(agent, "name", "agent"))
                        
                        # Handle task input safely
                        task_input = None
                        if hasattr(task, "description"):
                            task_input = task.description
                        elif isinstance(task, str):
                            task_input = task[:100]
                        
                        self.on_agent_start(
                            name=agent_name,
                            role=getattr(agent, "role", None),
                            input=task_input
                        )
                        
                        try:
                            result = original(task, *args, **kwargs)
                            self.on_agent_end(name=agent_name, output=result)
                            return result
                        except Exception as e:
                            self.on_agent_end(name=agent_name, error=str(e))
                            raise
                    return wrapped_execute
                
                setattr(agent, method_name, make_wrapper(original_method))
                break  # Successfully patched
            except (AttributeError, TypeError):
                continue

