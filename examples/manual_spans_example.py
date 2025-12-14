"""
Example demonstrating manual agent span tracking.
"""

from agentra import Agentra


def planner_agent(task: str) -> str:
    """Planning agent."""
    return f"Plan for: {task}"


def executor_agent(plan: str) -> str:
    """Execution agent."""
    return f"Executed: {plan}"


def reviewer_agent(result: str) -> str:
    """Review agent."""
    return f"Reviewed and approved: {result}"


def main():
    """Run multi-agent example with explicit spans."""
    
    agentra = Agentra("multi-agent-system")
    
    @agentra.wrap
    def complex_workflow(task: str) -> str:
        """Multi-agent workflow with explicit agent boundaries."""
        
        # Planning phase
        with agentra.agent("planner", role="Planning Agent"):
            plan = planner_agent(task)
            print(f"Planner: {plan}")
        
        # Execution phase
        with agentra.agent("executor", role="Execution Agent"):
            result = executor_agent(plan)
            print(f"Executor: {result}")
        
        # Review phase
        with agentra.agent("reviewer", role="Review Agent"):
            final_result = reviewer_agent(result)
            print(f"Reviewer: {final_result}")
        
        return final_result
    
    print("Running multi-agent workflow...")
    print()
    
    # Run workflow
    result = complex_workflow("Build a web application")
    
    print()
    print(f"Final result: {result}")
    print()
    
    # Check coverage
    coverage = agentra.coverage()
    print("Coverage:")
    print(f"  Agents observed: {coverage['agents']}")
    print()
    
    # Evaluate
    agentra.evaluate()
    agentra.report()
    
    # Save
    agentra.save("multi-agent-test")


if __name__ == "__main__":
    main()

