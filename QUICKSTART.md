# Agentra Quick Start

Get up and running with Agentra in 5 minutes.

## Installation

```bash
# Basic installation
pip install -e .

# With OpenAI support for evaluation
pip install -e . openai
export OPENAI_API_KEY=your_key
```

## 30-Second Example

```python
from agentra import Agentra
import openai

# 1. Initialize
agentra = Agentra("my-agent")

# 2. Wrap your agent
@agentra.wrap
def my_agent(query: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    )
    return response.choices[0].message.content

# 3. Run
my_agent("Write a Python function to sort a list")

# 4. Evaluate
agentra.report()
```

That's it! Agentra automatically captured everything.

## What Happened?

1. **Auto-Patching**: Agentra patched OpenAI to capture all LLM calls
2. **Trace Capture**: Every call to `my_agent()` was traced
3. **Evaluation**: Six categories were evaluated (functional, reasoning, etc.)
4. **Report**: A detailed report was generated

## Next Steps

### Save Results

```python
# Save for later analysis
agentra.save("test-run-1")

# Load and compare
result = Agentra.load("test-run-1")
comparison = Agentra.compare(["run-1", "run-2"])
```

### Named Traces (for Test Cases)

```python
with agentra.trace("test-simple-query"):
    my_agent("Hello")

with agentra.trace("test-complex-query"):
    my_agent("Design a microservices architecture")

agentra.save("regression-tests")
```

### Multi-Agent Systems

```python
@agentra.wrap
def complex_workflow(task):
    with agentra.agent("planner"):
        plan = planner.create_plan(task)
    
    with agentra.agent("executor"):
        result = executor.execute(plan)
    
    return result
```

### Framework Integration

#### CrewAI
```python
from agentra.adaptors import CrewAIAdaptor

crew = Crew(agents=[...], tasks=[...])
CrewAIAdaptor(agentra).instrument(crew)
crew.kickoff()
```

#### LangChain
```python
from agentra.adaptors import LangChainAdaptor

adaptor = LangChainAdaptor(agentra)
handler = adaptor.get_callback_handler()
chain.invoke(input, config={"callbacks": [handler]})
```

## Understanding Results

### Score Ranges
- **90-100%**: Excellent ★
- **75-89%**: Good ●
- **60-74%**: Fair ○
- **<60%**: Poor ✗

### Categories
1. **Functional** (20%): Does it work correctly?
2. **Output Quality** (20%): Is output clear and complete?
3. **Reasoning** (15%): Is logic sound?
4. **Tool Usage** (15%): Are tools used effectively?
5. **Performance** (15%): Is it fast enough?
6. **Safety** (15%): Any security/safety issues?

## Customization

### Adjust Weights
```python
config = {
    "weights": {
        "functional": 0.40,      # Emphasize correctness
        "output_quality": 0.30,
        "reasoning": 0.15,
        "performance": 0.10,
        "safety": 0.05,
    }
}

result = agentra.evaluate(config)
```

### Sampling (for Production)
```python
# Only capture 10% of runs
agentra = Agentra("prod-agent", sample_rate=0.1)
```

## Common Patterns

### Test Suite
```python
agentra = Agentra("my-agent")

test_cases = [
    ("simple", "Hello"),
    ("complex", "Design an API"),
    ("edge-empty", ""),
    ("edge-long", "x" * 10000),
]

for name, input in test_cases:
    with agentra.trace(name):
        my_agent(input)

agentra.save(f"test-suite-{datetime.now():%Y%m%d}")
```

### Regression Testing
```python
# Run before changes
agentra.save("baseline")

# Make changes to your agent...

# Run after changes
agentra.save("after-changes")

# Compare
print(Agentra.compare(["baseline", "after-changes"]))
```

### Coverage Tracking
```python
coverage = agentra.coverage()
print(f"Tested {coverage['traces']} scenarios")
print(f"Used {len(coverage['agents'])} agents")
print(f"Called {len(coverage['tools'])} tools")
```

## Troubleshooting

### No LLM Calls Captured?
- Ensure auto-patching is enabled: `Agentra(..., auto_patch=True)`
- Patch must happen before importing OpenAI/Anthropic
- Use manual instrumentation if needed

### Evaluation Fails?
- Need API key for LLM-as-judge: `export OPENAI_API_KEY=...`
- Or evaluation will use heuristics (less accurate)

### Framework Not Captured?
- Use appropriate adaptor (CrewAI, LangChain, etc.)
- See framework-specific examples

## Examples

Check the `examples/` directory:
- `simple_example.py` - Basic usage
- `named_traces_example.py` - Test cases
- `manual_spans_example.py` - Multi-agent

Run them:
```bash
python examples/simple_example.py
```

## Learn More

- **Full Documentation**: See README.md
- **API Reference**: See docstrings in `agentra/agentra.py`
- **Contributing**: See CONTRIBUTING.md
- **Examples**: See `examples/` directory

## Questions?

Open an issue on GitHub or check the documentation!

---

**Happy Evaluating! 🎯**

