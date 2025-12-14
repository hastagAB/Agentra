# Agentra Examples

This directory contains example scripts demonstrating various Agentra features.

## Running Examples

```bash
# Simple example with basic wrapping
python examples/simple_example.py

# Named traces for test case tracking
python examples/named_traces_example.py

# Manual agent span tracking
python examples/manual_spans_example.py
```

## Examples Overview

### simple_example.py
Basic usage demonstrating:
- Wrapping an agent function with `@agentra.wrap`
- Running multiple queries
- Evaluating and generating reports
- Saving results

### named_traces_example.py
Shows how to use named traces for:
- Test case tracking
- Regression testing
- Edge case testing
- Organizing multiple test scenarios

### manual_spans_example.py
Demonstrates explicit agent boundary tracking:
- Multi-agent systems
- Manual span creation with `agentra.agent()`
- Coverage reporting
- Agent role tracking

## Integration Examples

For real-world integration examples with actual frameworks:

### With OpenAI
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

my_agent("Hello, world!")
agentra.report()
```

### With CrewAI
```python
from agentra import Agentra
from agentra.adaptors import CrewAIAdaptor
from crewai import Agent, Task, Crew

agentra = Agentra("dev-crew")

# Create your crew
crew = Crew(agents=[...], tasks=[...])

# Instrument
CrewAIAdaptor(agentra).instrument(crew)

# Run
crew.kickoff()

# Evaluate
agentra.report()
```

### With LangChain
```python
from agentra import Agentra
from agentra.adaptors import LangChainAdaptor

agentra = Agentra("my-chain")
adaptor = LangChainAdaptor(agentra)

# Get callback handler
handler = adaptor.get_callback_handler()

# Use with chain
chain.invoke(input, config={"callbacks": [handler]})

agentra.report()
```

## Creating Your Own Examples

Feel free to create additional examples demonstrating:
- Integration with new frameworks
- Custom evaluation scenarios
- Production use cases
- Advanced features

Submit a PR to share them with the community!

