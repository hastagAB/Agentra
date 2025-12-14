"""
Example demonstrating named traces for test case tracking.
"""

from agentra import Agentra


def mock_agent(query: str) -> str:
    """Mock agent for demonstration."""
    return f"Processed: {query}"


def main():
    """Run example with named traces."""
    
    agentra = Agentra("test-agent")
    
    print("Running test cases with named traces...")
    print()
    
    # Test Case 1: Simple query
    with agentra.trace("simple-query"):
        result = mock_agent("Hello")
        print(f"Test 1 (simple-query): {result}")
    
    # Test Case 2: Complex query
    with agentra.trace("complex-query"):
        result = mock_agent("Write a detailed implementation plan for a REST API")
        print(f"Test 2 (complex-query): {result[:50]}...")
    
    # Test Case 3: Edge case - empty input
    with agentra.trace("edge-case-empty"):
        result = mock_agent("")
        print(f"Test 3 (edge-case-empty): {result}")
    
    # Test Case 4: Edge case - very long input
    with agentra.trace("edge-case-long"):
        result = mock_agent("x" * 10000)
        print(f"Test 4 (edge-case-long): {result[:50]}...")
    
    print()
    print(f"Captured {len(agentra.get_traces())} named traces")
    
    # Evaluate all traces
    result = agentra.evaluate()
    agentra.report()
    
    # Save with meaningful name
    filepath = agentra.save("regression-test-v1.0")
    print(f"Results saved to: {filepath}")


if __name__ == "__main__":
    main()

