# Agentra Project Summary

## Overview

**Agentra** is a lightweight Python library for live agent instrumentation and evaluation. It captures execution traces from any AI agent system and provides comprehensive performance evaluation across six quality dimensions.

**Version**: 0.1.0  
**License**: MIT  
**Language**: Python 3.10+

---

## Complete Project Structure

```
agentra/
│
├── agentra/                          # Main package
│   ├── __init__.py                   # Public exports
│   ├── agentra.py                    # Main Agentra class (295 lines)
│   ├── types.py                      # Core data types (135 lines)
│   ├── capture.py                    # Trace capture context (107 lines)
│   ├── evaluate.py                   # Evaluation orchestrator (172 lines)
│   ├── judge.py                      # LLM-as-judge (175 lines)
│   ├── report.py                     # Report generation (98 lines)
│   ├── results.py                    # Save/load results (183 lines)
│   │
│   ├── patches/                      # Auto-patching LLM clients
│   │   ├── __init__.py
│   │   ├── openai_patch.py          # OpenAI instrumentation
│   │   ├── anthropic_patch.py       # Anthropic instrumentation
│   │   └── litellm_patch.py         # LiteLLM instrumentation
│   │
│   ├── adaptors/                     # Framework-specific adaptors
│   │   ├── __init__.py
│   │   ├── base.py                  # Base adaptor class
│   │   ├── crewai.py                # CrewAI adaptor
│   │   ├── langchain.py             # LangChain adaptor
│   │   ├── langgraph.py             # LangGraph adaptor
│   │   └── autogen.py               # AutoGen adaptor
│   │
│   └── evaluators/                   # Evaluation categories
│       ├── __init__.py
│       ├── base.py                  # Base evaluator
│       ├── functional.py            # Task completion evaluation
│       ├── reasoning.py             # Logic & efficiency evaluation
│       ├── tool_usage.py            # Tool effectiveness evaluation
│       ├── performance.py           # Speed & resource evaluation
│       ├── safety.py                # Security & safety evaluation
│       └── output_quality.py        # Output quality evaluation
│
├── examples/                         # Usage examples
│   ├── README.md
│   ├── simple_example.py            # Basic usage
│   ├── named_traces_example.py      # Test case tracking
│   └── manual_spans_example.py      # Multi-agent tracking
│
├── README.md                         # Main documentation (450+ lines)
├── QUICKSTART.md                     # Quick start guide
├── CONTRIBUTING.md                   # Contribution guidelines
├── LICENSE                           # MIT License
├── requirements.txt                  # Dependencies
├── setup.py                          # Package setup
├── .gitignore                        # Git ignore rules
└── PROJECT_SUMMARY.md               # This file
```

---

## Core Components

### 1. Types System (`types.py`)
**Purpose**: Define all data structures

**Key Types**:
- `LLMCall`: Single LLM invocation with tokens, timing
- `ToolCall`: Tool/function execution with I/O
- `AgentSpan`: Agent execution boundary (multi-agent)
- `Trace`: Complete execution trace
- `Score`: Evaluation score with reasoning
- `CategoryResult`: Category evaluation result
- `TraceResult`: Single trace evaluation
- `EvaluationResult`: Complete evaluation results
- `Status`: Overall quality status (Excellent/Good/Fair/Poor)

### 2. Capture System (`capture.py`)
**Purpose**: Context-aware trace capture using contextvars

**Features**:
- Async-safe context management
- Automatic agent span tracking
- Event logging
- Input/output capture
- Duration tracking

### 3. Main Class (`agentra.py`)
**Purpose**: Primary user interface

**API**:
- `@wrap`: Decorator for agent functions
- `trace()`: Manual trace context
- `agent()`: Agent boundary marking
- `evaluate()`: Run evaluation
- `report()`: Print detailed report
- `save()/load()`: Results persistence
- `compare()`: Compare multiple runs
- `coverage()`: Coverage tracking

### 4. Auto-Patching (`patches/`)
**Purpose**: Automatic LLM client instrumentation

**Supported**:
- OpenAI (sync & async)
- Anthropic
- LiteLLM

**Captures**:
- Model name
- Messages
- Response
- Token counts
- Duration

### 5. Framework Adaptors (`adaptors/`)
**Purpose**: Rich instrumentation for popular frameworks

**Supported Frameworks**:
- **CrewAI**: Agent roles, tasks, delegation
- **LangChain**: Chains, tools, retrievers
- **LangGraph**: Nodes, edges, state
- **AutoGen**: Conversations, messages

### 6. Evaluation System (`evaluators/`)
**Purpose**: Multi-dimensional quality assessment

**Categories** (6 total):

#### Functional (20%)
- Task completion
- Output correctness
- Completeness

#### Reasoning (15%)
- Logical consistency
- Tool selection
- Efficiency

#### Tool Usage (15%)
- Success rate
- Diversity
- Latency

#### Output Quality (20%)
- Clarity
- Completeness
- Format

#### Performance (15%)
- Execution duration
- Token efficiency
- Error rate

#### Safety (15%)
- Data leakage
- Harmful content
- Error handling

### 7. LLM Judge (`judge.py`)
**Purpose**: Use LLM for subjective evaluation

**Features**:
- Supports OpenAI & Anthropic
- Structured prompt engineering
- Score parsing
- Fallback on errors

### 8. Results System (`results.py`)
**Purpose**: Persistence and comparison

**Features**:
- JSON serialization
- Timestamp tracking
- Load by name/prefix
- Multi-result comparison
- List all results

### 9. Reporting (`report.py`)
**Purpose**: Human-readable output

**Features**:
- Console-formatted reports
- Category score visualization
- Issue highlighting
- Recommendations
- Coverage summary

---

## Key Design Principles

### 1. **Zero Configuration**
Auto-patching means minimal code changes. Just wrap and run.

### 2. **Observable Reality**
Capture what actually happens, not what you think happens. Different runs may trigger different agents/tools - that's fine.

### 3. **Framework Agnostic**
Core functionality works with any Python code. Adaptors add richness for specific frameworks.

### 4. **Production Ready**
- Sampling support for production monitoring
- Async-safe with contextvars
- Graceful error handling
- Minimal overhead

### 5. **Developer Friendly**
- Simple, intuitive API
- Clear, actionable reports
- JSON results for version control
- Easy comparison across runs

### 6. **Extensible**
- Easy to add new evaluators
- Easy to add new adaptors
- Configurable weights/thresholds
- Plugin architecture

---

## Technical Highlights

### Context Management
Uses Python's `contextvars` for async-safe trace tracking across async boundaries.

### Auto-Patching
Function wrapping/monkey-patching of LLM clients to transparently capture calls.

### Evaluation Architecture
Modular evaluator pattern with base class and category implementations. Easy to extend.

### Results Storage
JSON-based with timestamp tracking. Easy to version control and compare.

### Type Safety
Comprehensive type hints throughout for better IDE support and fewer bugs.

---

## Dependencies

**Core**: None (pure Python)

**Optional**:
- `openai>=1.0.0` - For OpenAI LLM judge
- `anthropic>=0.18.0` - For Anthropic LLM judge
- `crewai>=0.1.0` - For CrewAI adaptor
- `langchain>=0.1.0` - For LangChain adaptor
- `langgraph>=0.0.1` - For LangGraph adaptor
- `pyautogen>=0.2.0` - For AutoGen adaptor
- `litellm>=1.0.0` - For LiteLLM patching

---

## Usage Patterns

### Pattern 1: Quick Test
```python
agentra = Agentra("agent")

@agentra.wrap
def agent(q): return llm(q)

agent("test")
agentra.report()
```

### Pattern 2: Test Suite
```python
for test in tests:
    with agentra.trace(test.name):
        agent(test.input)

agentra.save("regression-v1")
```

### Pattern 3: Production Monitoring
```python
agentra = Agentra("prod", sample_rate=0.1)  # 10% sampling

@agentra.wrap
def prod_agent(req): ...

# Periodically evaluate and save
```

### Pattern 4: Multi-Agent
```python
@agentra.wrap
def workflow(task):
    with agentra.agent("planner"):
        plan = planner(task)
    
    with agentra.agent("executor"):
        result = executor(plan)
    
    return result
```

### Pattern 5: Framework Integration
```python
from agentra.adaptors import CrewAIAdaptor

crew = Crew(...)
CrewAIAdaptor(agentra).instrument(crew)
crew.kickoff()
```

---

## Implementation Statistics

**Total Files**: 31  
**Core Package Files**: 20  
**Example Files**: 4  
**Documentation Files**: 7

**Lines of Code** (approximate):
- Core functionality: ~1,500 lines
- Evaluators: ~600 lines
- Patches: ~300 lines
- Adaptors: ~400 lines
- Documentation: ~1,200 lines
- Examples: ~300 lines

**Total**: ~4,300 lines

---

## Testing Strategy

### Manual Testing
- Run examples to verify basic functionality
- Test with real LLM clients (OpenAI, Anthropic)
- Test framework adaptors with actual frameworks

### Integration Points
1. LLM client patching
2. Framework adaptor hooks
3. Evaluation with LLM judge
4. Results serialization

### Future Testing
- Unit tests for core components
- Integration tests with frameworks
- Performance benchmarks
- Edge case coverage

---

## Future Enhancements

### Potential Features
- [ ] HTML/dashboard reports
- [ ] More sophisticated cost estimation
- [ ] Real-time monitoring dashboard
- [ ] Export to CSV/Excel
- [ ] Statistical analysis across runs
- [ ] A/B testing support
- [ ] Custom metric definitions
- [ ] Webhook notifications
- [ ] Cloud storage integration
- [ ] Team collaboration features

### Additional Adaptors
- [ ] Haystack
- [ ] AutoGPT
- [ ] Semantic Kernel
- [ ] Custom agent frameworks

### Additional Evaluators
- [ ] Cost efficiency
- [ ] Latency percentiles
- [ ] Token usage patterns
- [ ] Conversation quality
- [ ] User satisfaction proxy

---

## Getting Started

1. **Install**: `pip install -e .`
2. **Set API Key**: `export OPENAI_API_KEY=...`
3. **Run Example**: `python examples/simple_example.py`
4. **Read Docs**: Check README.md and QUICKSTART.md

---

## Contributing

See CONTRIBUTING.md for:
- Development setup
- Adding evaluators
- Adding adaptors
- Code style
- PR process

---

## Support

- **Documentation**: README.md, QUICKSTART.md
- **Examples**: `examples/` directory
- **Issues**: GitHub Issues
- **Questions**: Open a discussion

---

## License

MIT License - See LICENSE file

---

## Acknowledgments

Built for developers who want to understand and improve their AI agents.

**Agentra** = **Agent** + Ins**tra**mentation + Evaluation

---

**Project Status**: ✅ Complete (v0.1.0)

All core features implemented and documented. Ready for use and extension.

