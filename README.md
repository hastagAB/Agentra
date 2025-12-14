# Agentra 🎯

**Live Agent Instrumentation & Evaluation**

A lightweight Python library that wraps any AI agent system to capture execution traces and evaluate performance. Add minimal code, run your agent normally, and Agentra captures everything automatically.

---

## Quick Start

```python
from agentra import Agentra
import openai

agentra = Agentra("my-agent")

@agentra.wrap
def my_agent(query: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    )
    return response.choices[0].message.content

# Run your agent
my_agent("Write a Python function to sort a list")
my_agent("Explain recursion")

# Evaluate and view results
result = agentra.evaluate()
agentra.report()
agentra.save("test-run-1")
```

Output:
```
======================================================================
  AGENTRA EVALUATION: my-agent
======================================================================

  Overall Score: 87% ● (good)

  Traces: 2
  LLM Calls: 2
  Tool Calls: 0
  Total Tokens: 1,234
  Total Time: 3.2s

  CATEGORY SCORES
  ------------------------------------------------------------------
  output_quality     █████████████████████████ 95%
  functional         ████████████████████████░ 92%
  safety             ███████████████████████░░ 88%
  reasoning          ██████████████████████░░░ 85%
  performance        █████████████████████░░░░ 82%
  tool_usage         ████████████████████░░░░░ 80%

  RECOMMENDATIONS
  ------------------------------------------------------------------
  → Improve performance: score is 82%

======================================================================
```

---

## Key Features

### 🎯 Zero-Config Auto-Patching
Automatically captures LLM calls from OpenAI, Anthropic, LiteLLM - no manual instrumentation needed.

### 📊 Comprehensive Evaluation
Six evaluation categories:
- **Functional**: Task completion, correctness, completeness
- **Reasoning**: Logical consistency, tool selection, efficiency
- **Tool Usage**: Success rate, diversity, latency
- **Output Quality**: Clarity, completeness, format
- **Performance**: Speed, token efficiency, error rate
- **Safety**: Data leakage, harmful content, error handling

### 🔧 Framework Adaptors
Rich instrumentation for popular frameworks:
- **CrewAI**: Agent roles, task assignments, delegation
- **LangChain**: Chain structure, retriever calls, memory
- **LangGraph**: Graph nodes, edge transitions, state
- **AutoGen**: Agent conversations, message passing

### 💾 Results Storage
Save and compare results across runs:

```python
# Save results
agentra.save("v1-baseline")

# Load and compare
result = Agentra.load("v1-baseline")
comparison = Agentra.compare(["v1-baseline", "v2-improvements"])
print(comparison)
```

---

## Installation

```bash
pip install agentra
```

For LLM-based evaluation:
```bash
pip install agentra openai  # or anthropic
export OPENAI_API_KEY=your_key
```

---

## Usage Examples

### Example 1: Simple Function

```python
from agentra import Agentra
import openai

agentra = Agentra("code-reviewer")

@agentra.wrap
def review_code(code: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Review: {code}"}]
    )
    return response.choices[0].message.content

# Run
review_code("def foo(): pass")
review_code("class User: ...")

# Evaluate
result = agentra.evaluate()
agentra.report()
agentra.save("code-review-test")
```

### Example 2: Named Traces (Test Cases)

```python
from agentra import Agentra

agentra = Agentra("my-agent")

# Name each trace for tracking
with agentra.trace("simple-task"):
    my_agent("Fix typo")

with agentra.trace("complex-task"):
    my_agent("Redesign auth system")

with agentra.trace("edge-case-empty"):
    my_agent("")

# Evaluate all traces
agentra.evaluate()
agentra.save("regression-test-v2.1")
```

### Example 3: CrewAI Integration

```python
from agentra import Agentra
from agentra.adaptors import CrewAIAdaptor
from crewai import Agent, Task, Crew

agentra = Agentra("dev-crew")

# Your crew setup
architect = Agent(role="Architect", goal="Design system", ...)
developer = Agent(role="Developer", goal="Implement", ...)
crew = Crew(agents=[architect, developer], tasks=[...])

# Instrument crew
CrewAIAdaptor(agentra).instrument(crew)

# Run normally
crew.kickoff(inputs={"task": "Build REST API"})

# Evaluate
agentra.evaluate()
agentra.save("crew-test")
```

### Example 4: LangChain Integration

```python
from agentra import Agentra
from agentra.adaptors import LangChainAdaptor
from langchain.chains import LLMChain

agentra = Agentra("my-chain")
adaptor = LangChainAdaptor(agentra)

# Option 1: Get callback handler
handler = adaptor.get_callback_handler()
chain.invoke(input, config={"callbacks": [handler]})

# Option 2: Instrument chain directly
adaptor.instrument(chain)
chain.invoke(input)

agentra.evaluate()
```

### Example 5: Manual Agent Boundaries

```python
from agentra import Agentra

agentra = Agentra("multi-agent")

@agentra.wrap
def complex_workflow(task):
    # Mark agent boundaries explicitly
    with agentra.agent("planner", role="Planning Agent"):
        plan = planner.create_plan(task)
    
    with agentra.agent("executor", role="Execution Agent"):
        result = executor.execute(plan)
    
    with agentra.agent("reviewer", role="Review Agent"):
        review = reviewer.review(result)
    
    return review

complex_workflow("Build a web app")
agentra.evaluate()
```

---

## Evaluation Configuration

Customize evaluation weights and thresholds:

```python
config = {
    "weights": {
        "functional": 0.30,      # Emphasize correctness
        "output_quality": 0.25,
        "reasoning": 0.15,
        "tool_usage": 0.10,
        "performance": 0.10,
        "safety": 0.10,
    }
}

result = agentra.evaluate(config=config)
```

---

## API Reference

### Agentra Class

```python
class Agentra:
    def __init__(
        self,
        name: str,
        description: str = "",
        auto_patch: bool = True,
        sample_rate: float = 1.0,
        results_dir: str = "agentra-results",
    )
    
    # Instrumentation
    @wrap                           # Decorator for agent functions
    @trace(name: str = None)        # Context manager for manual tracing
    @agent(name: str, role: str)    # Mark agent boundaries
    
    # Evaluation
    def evaluate(config: dict = None) -> EvaluationResult
    def report()                    # Print detailed report
    def summary() -> str            # One-line summary
    
    # Results
    def save(name: str) -> str      # Save to JSON
    @staticmethod
    def load(name: str) -> EvaluationResult
    @staticmethod
    def list_results() -> list[dict]
    @staticmethod
    def compare(names: list[str]) -> str
    
    # Data
    def get_traces() -> list[Trace]
    def clear()                     # Clear traces
    def coverage() -> dict          # Coverage report
    def export(path: str)           # Export traces to JSON
```

---

## Evaluation Categories

### Functional (20%)
- Task completion
- Output correctness
- Completeness

### Reasoning (15%)
- Logical consistency
- Tool selection
- Efficiency

### Tool Usage (15%)
- Success rate
- Diversity
- Latency

### Output Quality (20%)
- Clarity
- Completeness
- Format quality

### Performance (15%)
- Execution duration
- Token efficiency
- Error rate

### Safety (15%)
- Data leakage detection
- Harmful content
- Error handling

---

## Results Storage

Results are saved to `agentra-results/` as JSON files:

```
agentra-results/
├── test-run-1_20240115_143022.json
├── v2.1-regression_20240115_150433.json
└── crew-test_20240115_163044.json
```

Load and compare:

```python
# List all results
results = Agentra.list_results()
for r in results:
    print(f"{r['name']}: {r['score']:.0%} ({r['traces']} traces)")

# Load specific result
result = Agentra.load("v2.1-regression")
print(result.summary)

# Compare versions
comparison = Agentra.compare(["v2.0-baseline", "v2.1-update"])
print(comparison)
```

---

## Advanced Features

### Custom Evaluators

Create your own evaluation categories:

```python
from agentra.evaluators import BaseEvaluator
from agentra.types import CategoryResult, Score

class CustomEvaluator(BaseEvaluator):
    name = "custom"
    
    def evaluate(self, trace, system_description=""):
        # Your evaluation logic
        checks = {
            "my_check": Score(0.9, "Looking good!")
        }
        return CategoryResult(
            name=self.name,
            score=0.9,
            weight=0.1,
            checks=checks,
            issues=[]
        )
```

### Sampling for Production

Capture only a fraction of executions:

```python
# Capture 10% of runs
agentra = Agentra("prod-agent", sample_rate=0.1)
```

### Coverage Tracking

See what agents and tools were exercised:

```python
coverage = agentra.coverage()
print(f"Agents: {coverage['agents']}")
print(f"Tools: {coverage['tools']}")
print(f"LLM calls: {coverage['llm_calls']}")
```

---

## Design Principles

1. **Observability**: Capture what actually happens, not what you think happens
2. **Minimal Overhead**: Auto-patching means minimal code changes
3. **Framework Agnostic**: Works with any Python agent framework
4. **Production Ready**: Sampling support for production monitoring
5. **Developer Friendly**: Simple API, clear outputs, JSON storage

---

## Contributing

Contributions welcome! This is an open-source project.

To add a new framework adaptor:
1. Extend `BaseAdaptor` in `agentra/adaptors/`
2. Implement `instrument()` method
3. Hook into framework callbacks/events
4. Submit PR

---

## License

MIT License

---

## Acknowledgments

Built for developers who want to understand and improve their AI agents.

**Agentra** = Agent + Instrumentation + Evaluation

