"""
Simple example demonstrating Agentra usage.

This example shows basic instrumentation of an agent function.
"""

import os
from agentra import Agentra


# Mock LLM call (replace with real OpenAI/Anthropic in production)
def mock_llm_call(prompt: str) -> str:
    """Mock LLM for demonstration purposes."""
    responses = {
        "Write a Python function to sort a list": "def sort_list(lst):\n    return sorted(lst)",
        "Explain recursion": "Recursion is when a function calls itself...",
        "What is the meaning of life?": "42",
    }
    return responses.get(prompt, f"Response to: {prompt[:50]}...")


# Initialize Agentra
agentra = Agentra("simple-agent", description="A simple demo agent")


# Wrap your agent function
@agentra.wrap
def my_agent(query: str) -> str:
    """Simple agent that processes queries."""
    
    # In production, this would be:
    # response = openai.chat.completions.create(...)
    # For demo, we use mock:
    
    response = mock_llm_call(query)
    return response


def main():
    """Run example."""
    
    print("=" * 70)
    print("Agentra Simple Example")
    print("=" * 70)
    print()
    
    # Run agent multiple times
    print("Running agent...")
    result1 = my_agent("Write a Python function to sort a list")
    print(f"Result 1: {result1[:50]}...")
    
    result2 = my_agent("Explain recursion")
    print(f"Result 2: {result2[:50]}...")
    
    result3 = my_agent("What is the meaning of life?")
    print(f"Result 3: {result3}")
    
    print()
    print("Traces captured:", len(agentra.get_traces()))
    print()
    
    # Evaluate (will use mock evaluation without actual LLM judge)
    print("Evaluating...")
    result = agentra.evaluate()
    
    print()
    print("Summary:", agentra.summary())
    print()
    
    # Print detailed report
    agentra.report()
    
    # Save results
    filepath = agentra.save("simple-example")
    print(f"Results saved to: {filepath}")
    print()
    
    # Show coverage
    coverage = agentra.coverage()
    print("Coverage:")
    print(f"  Traces: {coverage['traces']}")
    print(f"  LLM Calls: {coverage['llm_calls']}")
    print(f"  Tool Calls: {coverage['tool_calls']}")


if __name__ == "__main__":
    main()

