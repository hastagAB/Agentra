# Agentra - Complete Technical Documentation

This document provides a comprehensive guide to understanding Agentra's architecture, structure, execution flow, and implementation details. After reading this, you should be able to answer any question about how Agentra works.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Directory Structure](#directory-structure)
4. [Core Components](#core-components)
5. [Data Types](#data-types)
6. [Execution Flow](#execution-flow)
7. [Component Details](#component-details)
8. [End-to-End Examples](#end-to-end-examples)
9. [How Everything Connects](#how-everything-connects)

---

## Project Overview

**Agentra** is a Python library for instrumenting and evaluating AI agent systems. It works by:

1. **Wrapping** agent functions to create execution traces
2. **Auto-patching** LLM clients to capture API calls
3. **Capturing** all execution data (LLM calls, tool calls, agent spans)
4. **Evaluating** captured traces across 6 quality dimensions
5. **Reporting** results with scores, issues, and recommendations

### Key Design Principles

- **Zero Configuration**: Auto-patching means minimal code changes
- **Observability**: Captures what actually happens, not assumptions
- **Framework Agnostic**: Works with any Python agent code
- **Context-Aware**: Uses Python's `contextvars` for async-safe tracing
- **Extensible**: Easy to add new evaluators and adaptors

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Agent Code                        │
│  @agentra.wrap                                              │
│  def my_agent(query):                                       │
│      response = openai.chat.completions.create(...)         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Agentra Instrumentation Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   @wrap      │  │  auto-patch  │  │  adaptors    │     │
│  │  decorator   │  │  LLM clients  │  │  frameworks  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Capture Context (contextvars)                  │
│  - Trace creation                                           │
│  - LLM call capture                                         │
│  - Tool call capture                                        │
│  - Agent span tracking                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Trace Storage (in-memory)                      │
│  - List of Trace objects                                    │
│  - Each trace contains:                                    │
│    * LLM calls                                              │
│    * Tool calls                                             │
│    * Agent spans                                            │
│    * Input/output                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Evaluation Engine                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 6 Evaluators │  │ LLM Judge    │  │ Aggregator   │     │
│  │ (categories) │  │ (subjective) │  │ (weighted)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Results & Reporting                            │
│  - EvaluationResult object                                  │
│  - Console reports                                          │
│  - JSON storage                                             │
│  - Comparison tools                                         │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
User Code
    │
    ├─> Agentra.__init__() ──> Auto-patch LLM clients
    │
    ├─> @agentra.wrap ──────> Creates wrapper function
    │
    ├─> my_agent() ──────────> Wrapper executes:
    │                          1. Check sample_rate
    │                          2. Create CaptureContext
    │                          3. Call original function
    │                          4. Capture input/output
    │
    ├─> openai.chat... ──────> Patched function:
    │                          1. Get current CaptureContext
    │                          2. Call original API
    │                          3. Extract LLM call data
    │                          4. Add to trace
    │
    ├─> agentra.evaluate() ──> Evaluation:
    │                          1. Create Evaluator
    │                          2. Run 6 evaluators on each trace
    │                          3. Aggregate scores
    │                          4. Generate recommendations
    │
    └─> agentra.report() ────> Display results
```

---

## Directory Structure

```
agentra/
├── __init__.py              # Public API exports
├── agentra.py               # Main Agentra class (entry point)
├── types.py                 # All data structures (Trace, LLMCall, etc.)
├── capture.py               # Context management for trace capture
├── evaluate.py              # Evaluation orchestrator
├── judge.py                 # LLM-as-judge for subjective evaluation
├── report.py                # Console report generation
├── results.py               # Save/load evaluation results
│
├── patches/                 # Auto-patching for LLM clients
│   ├── __init__.py
│   ├── openai_patch.py      # Patches OpenAI client
│   ├── anthropic_patch.py   # Patches Anthropic client
│   └── litellm_patch.py     # Patches LiteLLM client
│
├── adaptors/                # Framework-specific instrumentation
│   ├── __init__.py
│   ├── base.py              # BaseAdaptor abstract class
│   ├── crewai.py            # CrewAI framework adaptor
│   ├── langchain.py         # LangChain framework adaptor
│   ├── langgraph.py         # LangGraph framework adaptor
│   └── autogen.py           # AutoGen framework adaptor
│
└── evaluators/              # Evaluation category implementations
    ├── __init__.py
    ├── base.py              # BaseEvaluator abstract class
    ├── functional.py         # Task completion evaluation
    ├── reasoning.py         # Logic quality evaluation
    ├── tool_usage.py        # Tool effectiveness evaluation
    ├── output_quality.py    # Output clarity evaluation
    ├── performance.py       # Speed/efficiency evaluation
    └── safety.py            # Security/safety evaluation
```

---

## Core Components

### 1. `agentra.py` - Main Entry Point

**Purpose**: Primary user interface, orchestrates all functionality.

**Key Classes**:
- `Agentra`: Main class that users interact with

**Key Methods**:
- `__init__()`: Initialize, optionally auto-patch LLM clients
- `wrap()`: Decorator to wrap agent functions
- `trace()`: Context manager for manual tracing
- `agent()`: Context manager for agent boundaries
- `evaluate()`: Run evaluation on captured traces
- `report()`: Print evaluation report
- `save()`: Save results to JSON
- `load()`: Load saved results
- `compare()`: Compare multiple results

**What It Does**:
1. Stores captured traces in `self._traces`
2. Applies auto-patching on initialization
3. Creates `CaptureContext` when wrapping functions
4. Delegates evaluation to `Evaluator` class
5. Delegates reporting to `report.py` functions

**Example**:
```python
agentra = Agentra("my-system")  # Creates instance, patches LLM clients

@agentra.wrap  # Decorator creates wrapper
def my_agent(query):
    return llm(query)

my_agent("test")  # Wrapper executes, captures trace
agentra.evaluate()  # Evaluates all captured traces
```

---

### 2. `types.py` - Data Structures

**Purpose**: Defines all data types used throughout the system.

**Key Types**:

#### `LLMCall`
Represents a single LLM API call.
```python
@dataclass
class LLMCall:
    model: str              # "gpt-4", "claude-3", etc.
    messages: list[dict]     # Input messages
    response: str            # Output text
    tokens_in: int          # Input tokens
    tokens_out: int         # Output tokens
    duration_ms: float      # Call duration
    timestamp: datetime     # When it happened
    metadata: dict         # Additional context
```

#### `ToolCall`
Represents a single tool/function call.
```python
@dataclass
class ToolCall:
    name: str              # Tool name
    input: dict            # Tool input
    output: Any            # Tool output
    error: Optional[str]   # Error if any
    duration_ms: float     # Call duration
    timestamp: datetime    # When it happened
```

#### `AgentSpan`
Tracks one agent's execution in multi-agent systems.
```python
@dataclass
class AgentSpan:
    name: str                    # Agent name
    role: Optional[str]          # Agent role
    start_time: datetime
    end_time: Optional[datetime]
    llm_calls: list[LLMCall]     # LLM calls by this agent
    tool_calls: list[ToolCall]   # Tool calls by this agent
    input: Any
    output: Any
    error: Optional[str]
```

#### `Trace`
Complete execution trace of one agent run.
```python
@dataclass
class Trace:
    id: str                      # Unique ID
    name: Optional[str]          # User-provided name
    input: Any                  # Agent input
    output: Any                 # Agent output
    llm_calls: list[LLMCall]    # All LLM calls
    tool_calls: list[ToolCall]  # All tool calls
    agent_spans: list[AgentSpan] # Agent boundaries
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: float
    error: Optional[str]
    framework: Optional[str]     # "crewai", "langchain", etc.
    metadata: dict              # Additional data
```

#### `EvaluationResult`
Complete evaluation results.
```python
@dataclass
class EvaluationResult:
    name: str                    # Result file name
    system_name: str
    score: float                 # Overall score (0-1)
    status: Status               # EXCELLENT/GOOD/FAIR/POOR
    categories: list[CategoryResult]  # Per-category scores
    trace_results: list[TraceResult] # Per-trace results
    summary: str
    issues: list[str]
    recommendations: list[str]
    total_traces: int
    total_llm_calls: int
    total_tool_calls: int
    total_tokens: int
    total_duration_ms: float
    agents_observed: list[str]
    tools_observed: list[str]
```

**What It Does**:
- Provides type-safe data structures
- Enables serialization to JSON
- Defines the contract between components

---

### 3. `capture.py` - Context Management

**Purpose**: Manages trace capture using Python's `contextvars` for async-safe operation.

**Key Classes**:
- `CaptureContext`: Context manager for a single trace

**Key Concepts**:

#### Context Variables
Uses `contextvars.ContextVar` to track current trace across:
- Function calls
- Async boundaries
- Thread boundaries
- Nested contexts

```python
_current_context: ContextVar[Optional["CaptureContext"]] = ContextVar(
    "agentra_context", default=None
)
```

**Key Methods**:

#### `CaptureContext.__init__()`
Creates a new trace with unique ID.

#### `CaptureContext.__enter__()`
1. Sets this context as current (via `contextvars`)
2. Records start time
3. Returns self for use in `with` statement

#### `CaptureContext.__exit__()`
1. Records end time
2. Calculates duration
3. Captures any exceptions
4. Resets context variable

#### `CaptureContext.get_current()`
Static method to get current active context (if any).

#### `CaptureContext.add_llm_call()`
Adds an LLM call to the trace. Also adds to current agent span if active.

#### `CaptureContext.add_tool_call()`
Adds a tool call to the trace. Also adds to current agent span if active.

#### `CaptureContext.start_agent_span()`
Starts tracking an agent boundary. Creates `AgentSpan` and pushes to stack.

#### `CaptureContext.end_agent_span()`
Ends tracking an agent boundary. Pops from stack and records end time.

**What It Does**:
- Creates and manages `Trace` objects
- Tracks agent boundaries (for multi-agent systems)
- Provides async-safe context tracking
- Captures all execution data (LLM calls, tool calls, errors)

**Example**:
```python
# When @agentra.wrap is used:
with CaptureContext() as ctx:  # __enter__ called
    ctx.set_input(query)
    result = my_agent(query)   # LLM calls captured here
    ctx.set_output(result)
# __exit__ called, trace stored
```

---

### 4. `patches/` - Auto-Patching LLM Clients

**Purpose**: Monkey-patches LLM client libraries to automatically capture API calls.

**How It Works**:

1. **Store Original Function**: Save reference to original API method
2. **Create Wrapper**: Create new function that wraps original
3. **Replace Function**: Replace original with wrapper
4. **Capture in Wrapper**: In wrapper, get current context and capture call

**Example (OpenAI)**:

```python
# Original code
def patch_openai():
    # 1. Get original function
    _original_create = openai.chat.completions.create
    
    # 2. Create wrapper
    def patched_create(*args, **kwargs):
        ctx = CaptureContext.get_current()  # Get active trace
        start = time.time()
        
        # 3. Call original
        response = _original_create(*args, **kwargs)
        
        duration = (time.time() - start) * 1000
        
        # 4. Capture if in traced context
        if ctx:
            llm_call = _extract_llm_call(kwargs, response, duration)
            ctx.add_llm_call(llm_call)
        
        return response
    
    # 5. Replace original
    openai.chat.completions.create = patched_create
```

**What Gets Captured**:
- Model name
- Input messages
- Response text
- Token counts (input/output)
- Duration
- Timestamp

**Files**:
- `openai_patch.py`: Patches `openai.chat.completions.create`
- `anthropic_patch.py`: Patches `anthropic.Anthropic.messages.create`
- `litellm_patch.py`: Patches `litellm.completion`

**When It Happens**:
- Called automatically in `Agentra.__init__()` if `auto_patch=True`
- Only patches once (uses global flag to prevent double-patching)

---

### 5. `adaptors/` - Framework Integration

**Purpose**: Provides rich instrumentation for specific AI frameworks beyond just LLM calls.

**Base Class** (`base.py`):

```python
class BaseAdaptor(ABC):
    def __init__(self, agentra: "Agentra"):
        self.agentra = agentra
    
    @abstractmethod
    def instrument(self, target) -> None:
        """Instrument a framework object."""
        pass
    
    def on_agent_start(self, name, role, input):
        """Called when agent starts."""
        ctx = CaptureContext.get_current()
        if ctx:
            ctx.start_agent_span(name, role, input)
    
    def on_agent_end(self, name, output, error):
        """Called when agent ends."""
        ctx = CaptureContext.get_current()
        if ctx:
            ctx.end_agent_span(name, output, error)
```

**How Adaptors Work**:

1. **Hook into Framework**: Monkey-patch framework methods
2. **Create Trace Context**: Wrap framework execution in trace
3. **Track Agent Boundaries**: Call `on_agent_start/end` for each agent
4. **Track Tasks/Nodes**: Call `on_task_start/end` for framework events

**Example (CrewAI)**:

```python
class CrewAIAdaptor(BaseAdaptor):
    def instrument(self, crew):
        original_kickoff = crew.kickoff
        
        def wrapped_kickoff(*args, **kwargs):
            # Start trace
            with self.agentra.trace():
                # Instrument each agent
                for agent in crew.agents:
                    self._instrument_agent(agent)
                
                # Run crew
                return original_kickoff(*args, **kwargs)
        
        crew.kickoff = wrapped_kickoff
    
    def _instrument_agent(self, agent):
        original_execute = agent.execute_task
        
        def wrapped_execute(task, *args, **kwargs):
            # Track agent start
            self.on_agent_start(agent.role, role=agent.role)
            
            try:
                result = original_execute(task, *args, **kwargs)
                self.on_agent_end(agent.role, output=result)
                return result
            except Exception as e:
                self.on_agent_end(agent.role, error=str(e))
                raise
        
        agent.execute_task = wrapped_execute
```

**What Adaptors Capture**:
- Agent roles and boundaries
- Task execution order
- Framework-specific events
- Delegation patterns

**Files**:
- `crewai.py`: CrewAI framework
- `langchain.py`: LangChain framework
- `langgraph.py`: LangGraph framework
- `autogen.py`: AutoGen framework

---

### 6. `evaluate.py` - Evaluation Orchestrator

**Purpose**: Coordinates evaluation across all categories and aggregates results.

**Key Classes**:
- `Evaluator`: Main orchestrator class

**How It Works**:

1. **Initialize Evaluators**: Create all 6 evaluator instances
2. **For Each Trace**: Run all evaluators
3. **Aggregate Scores**: Calculate weighted average
4. **Generate Results**: Create `EvaluationResult` object

**Key Methods**:

#### `Evaluator.__init__()`
Creates all evaluator instances:
```python
self.evaluators = [
    FunctionalEvaluator(),
    ReasoningEvaluator(),
    ToolUsageEvaluator(),
    OutputQualityEvaluator(),
    PerformanceEvaluator(),
    SafetyEvaluator(),
]
```

#### `Evaluator.evaluate()`
Main evaluation method:

```python
def evaluate(self, traces, system_name, system_description):
    # 1. Evaluate each trace
    for trace in traces:
        trace_categories = []
        
        # 2. Run each evaluator
        for evaluator in self.evaluators:
            cat_result = evaluator.evaluate(trace, system_description)
            trace_categories.append(cat_result)
        
        # 3. Calculate trace score (weighted)
        trace_score = sum(
            cat.score * self.weights[cat.name]
            for cat in trace_categories
        )
        
        # 4. Create TraceResult
        trace_results.append(TraceResult(...))
    
    # 5. Aggregate category scores
    for evaluator in self.evaluators:
        avg_score = sum(scores) / len(scores)
        aggregate_categories.append(CategoryResult(...))
    
    # 6. Calculate overall score
    overall_score = sum(cat.score * cat.weight for cat in aggregate_categories)
    
    # 7. Determine status
    if overall_score >= 0.9: status = EXCELLENT
    elif overall_score >= 0.75: status = GOOD
    elif overall_score >= 0.6: status = FAIR
    else: status = POOR
    
    # 8. Generate recommendations
    recommendations = self._generate_recommendations(...)
    
    # 9. Return EvaluationResult
    return EvaluationResult(...)
```

**Default Weights**:
```python
DEFAULT_WEIGHTS = {
    "functional": 0.20,      # 20%
    "reasoning": 0.15,      # 15%
    "tool_usage": 0.15,     # 15%
    "output_quality": 0.20, # 20%
    "performance": 0.15,    # 15%
    "safety": 0.15,         # 15%
}
```

---

### 7. `evaluators/` - Evaluation Categories

**Purpose**: Implements specific evaluation logic for each quality dimension.

**Base Class** (`base.py`):

```python
class BaseEvaluator(ABC):
    name: str = "base"  # Category name
    
    @abstractmethod
    def evaluate(self, trace: Trace, system_description: str) -> CategoryResult:
        """Evaluate a trace and return category result."""
        pass
```

**How Evaluators Work**:

1. **Analyze Trace**: Examine trace data (LLM calls, tool calls, input/output)
2. **Run Checks**: Perform specific checks (e.g., "Is output correct?")
3. **Calculate Score**: Score each check (0.0 to 1.0)
4. **Identify Issues**: Collect issues found
5. **Return Result**: Return `CategoryResult` with score and issues

**Example (FunctionalEvaluator)**:

```python
class FunctionalEvaluator(BaseEvaluator):
    name = "functional"
    
    def evaluate(self, trace, system_description):
        checks = {}
        issues = []
        judge = Judge()
        
        # Check 1: Task Completion
        completion_score = judge.evaluate(
            criteria="Did the agent complete the requested task?",
            input=str(trace.input),
            output=str(trace.output),
            context=system_description,
        )
        checks["task_completion"] = completion_score
        
        # Check 2: Correctness
        correctness_score = judge.evaluate(
            criteria="Is the output correct?",
            input=str(trace.input),
            output=str(trace.output),
        )
        checks["correctness"] = correctness_score
        
        # Check 3: Completeness
        completeness_score = judge.evaluate(
            criteria="Does output fully address input?",
            input=str(trace.input),
            output=str(trace.output),
        )
        checks["completeness"] = completeness_score
        
        # Calculate average score
        avg_score = sum(s.value for s in checks.values()) / len(checks)
        
        return CategoryResult(
            name=self.name,
            score=avg_score,
            weight=0.20,
            checks=checks,
            issues=issues,
        )
```

**All Evaluators**:

1. **FunctionalEvaluator** (`functional.py`):
   - Task completion
   - Output correctness
   - Completeness
   - Uses LLM judge

2. **ReasoningEvaluator** (`reasoning.py`):
   - Logical consistency
   - Tool selection appropriateness
   - Efficiency (steps to solution)
   - Uses heuristics + LLM judge

3. **ToolUsageEvaluator** (`tool_usage.py`):
   - Success rate
   - Tool diversity
   - Latency
   - Uses heuristics

4. **OutputQualityEvaluator** (`output_quality.py`):
   - Clarity
   - Completeness
   - Format quality
   - Uses LLM judge + heuristics

5. **PerformanceEvaluator** (`performance.py`):
   - Execution duration
   - Token efficiency
   - Error rate
   - Uses heuristics

6. **SafetyEvaluator** (`safety.py`):
   - Data leakage detection
   - Harmful content
   - Error handling
   - Uses pattern matching + LLM judge

---

### 8. `judge.py` - LLM-as-Judge

**Purpose**: Uses an LLM to evaluate subjective criteria (e.g., "Is the output correct?").

**Key Classes**:
- `Judge`: LLM evaluator

**How It Works**:

1. **Initialize Client**: Set up OpenAI or Anthropic client
2. **Build Prompt**: Create evaluation prompt with criteria, input, output
3. **Call LLM**: Request evaluation from LLM
4. **Parse Response**: Extract score (0.0-1.0) and reason
5. **Return Score**: Return `Score` object

**Example**:

```python
judge = Judge()  # Uses OpenAI or Anthropic based on API keys

score = judge.evaluate(
    criteria="Is the output correct?",
    input="Write a Python function to sort a list",
    output="def sort_list(lst):\n    return sorted(lst)",
    context="Code generation agent",
)

# Returns:
# Score(
#     value=0.95,
#     reason="Output is correct and complete",
#     details={...}
# )
```

**Prompt Structure**:

```
You are an expert evaluator of AI agent systems.

Evaluate the following based on this criteria: {criteria}

System Context: {context}

Input:
{input}

Output:
{output}

Provide your evaluation in the following format:
SCORE: [0.0 to 1.0]
REASON: [Brief explanation]
```

**Response Parsing**:
- Looks for "SCORE: X" line
- Extracts number (0.0 to 1.0)
- Looks for "REASON: Y" line
- Falls back to regex if format differs

---

### 9. `report.py` - Report Generation

**Purpose**: Generates human-readable console reports from evaluation results.

**Key Functions**:

#### `print_report(result: EvaluationResult)`
Prints detailed report:
- Overall score and status
- Statistics (traces, LLM calls, tokens, time)
- Category scores with visual bars
- Issues list
- Recommendations
- Per-trace breakdown (if few traces)
- Coverage (agents/tools observed)

#### `generate_summary(result: EvaluationResult) -> str`
Returns one-line summary:
```
"2 traces | Score: 87% (good) | 2 LLM calls | 0 issues"
```

**Example Output**:

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

### 10. `results.py` - Results Persistence

**Purpose**: Save and load evaluation results to/from JSON files.

**Key Functions**:

#### `save_result(result, name, results_dir) -> str`
Saves `EvaluationResult` to JSON file:
- Creates directory if needed
- Generates filename with timestamp: `{name}_{timestamp}.json`
- Serializes dataclasses to dict
- Writes to file

#### `load_result(name, results_dir) -> EvaluationResult`
Loads result from file:
- Tries exact match first
- Falls back to prefix match (most recent)
- Deserializes JSON to dataclasses
- Returns `EvaluationResult`

#### `list_results(results_dir) -> list[dict]`
Lists all saved results:
- Scans directory for `.json` files
- Extracts metadata (name, score, status, traces)
- Sorts by timestamp (newest first)

#### `compare_results(names, results_dir) -> str`
Compares multiple results:
- Loads all specified results
- Creates comparison table
- Shows scores, status, category breakdowns

**File Format**:

```json
{
  "name": "test-run-1",
  "system_name": "my-agent",
  "score": 0.87,
  "status": "good",
  "categories": [...],
  "trace_results": [...],
  "summary": "...",
  "issues": [...],
  "recommendations": [...],
  "total_traces": 2,
  "total_llm_calls": 2,
  ...
}
```

---

## Execution Flow

### End-to-End Flow: Simple Agent

Let's trace through a complete execution:

```python
from agentra import Agentra
import openai

# STEP 1: Initialize
agentra = Agentra("my-agent")
```

**What Happens**:
1. `Agentra.__init__()` called
2. Stores name, description, sample_rate
3. Creates empty `self._traces = []`
4. Calls `self._apply_patches()`
5. `_apply_patches()` calls:
   - `patch_openai()` → Patches `openai.chat.completions.create`
   - `patch_anthropic()` → Patches Anthropic client
   - `patch_litellm()` → Patches LiteLLM
6. Each patch function:
   - Stores original function
   - Creates wrapper function
   - Replaces original with wrapper

**State After Init**:
- LLM clients are patched
- `agentra._traces = []`
- `agentra._latest_result = None`

```python
# STEP 2: Wrap Agent Function
@agentra.wrap
def my_agent(query: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    )
    return response.choices[0].message.content
```

**What Happens**:
1. `agentra.wrap(my_agent)` called
2. Creates wrapper function that:
   - Checks `sample_rate` (random sampling)
   - Creates `CaptureContext(name=None)`
   - Enters context (`__enter__`)
   - Calls original function
   - Exits context (`__exit__`)
   - Stores trace in `agentra._traces`

**State After Wrap**:
- `my_agent` is now the wrapper function
- Original function stored in closure

```python
# STEP 3: Call Agent
result = my_agent("Write a Python function to sort a list")
```

**What Happens** (detailed):

1. **Wrapper Executes**:
   ```python
   # In wrapper function
   if random.random() > self.sample_rate:  # Check sampling
       return fn(*args, **kwargs)  # Skip if not sampled
   
   # Create capture context
   with self.trace() as ctx:  # Creates CaptureContext
   ```

2. **CaptureContext.__enter__()**:
   ```python
   # Creates new Trace with UUID
   self.trace = Trace(id=uuid4(), name=None)
   
   # Sets context variable
   _current_context.set(self)
   
   # Records start time
   self.trace.start_time = datetime.now()
   ```

3. **Capture Input**:
   ```python
   ctx.set_input("Write a Python function to sort a list")
   # Sets trace.input = "Write a Python function..."
   ```

4. **Original Function Executes**:
   ```python
   # User's code runs
   response = openai.chat.completions.create(...)
   ```

5. **Patched OpenAI Function Executes**:
   ```python
   # In patched_create wrapper
   ctx = CaptureContext.get_current()  # Gets active context
   start = time.time()
   
   # Call original OpenAI API
   response = _original_create(*args, **kwargs)
   
   duration = (time.time() - start) * 1000
   
   # Extract LLM call data
   llm_call = LLMCall(
       model="gpt-4",
       messages=[{"role": "user", "content": "Write a Python..."}],
       response="def sort_list(lst):\n    return sorted(lst)",
       tokens_in=15,
       tokens_out=25,
       duration_ms=1234.5,
       timestamp=datetime.now(),
   )
   
   # Add to trace
   ctx.add_llm_call(llm_call)
   ```

6. **Capture Output**:
   ```python
   ctx.set_output("def sort_list(lst):\n    return sorted(lst)")
   # Sets trace.output = "def sort_list..."
   ```

7. **CaptureContext.__exit__()**:
   ```python
   # Records end time
   self.trace.end_time = datetime.now()
   
   # Calculates duration
   self.trace.duration_ms = (end_time - start_time) * 1000
   
   # Resets context variable
   _current_context.reset(self._token)
   ```

8. **Trace Stored**:
   ```python
   # In agentra.trace() context manager
   self._traces.append(ctx.trace)
   ```

**State After Call**:
- `agentra._traces` contains one `Trace` object
- Trace contains:
  - Input: "Write a Python function..."
  - Output: "def sort_list(lst):..."
  - One `LLMCall` with all API details
  - Duration, timestamps, etc.

```python
# STEP 4: Evaluate
result = agentra.evaluate()
```

**What Happens**:

1. **Create Evaluator**:
   ```python
   evaluator = Evaluator(config=None)
   # Creates 6 evaluator instances
   ```

2. **For Each Trace**:
   ```python
   for trace in agentra._traces:
       trace_categories = []
       
       # Run each evaluator
       for evaluator in self.evaluators:
           cat_result = evaluator.evaluate(trace, system_description)
           trace_categories.append(cat_result)
   ```

3. **FunctionalEvaluator.evaluate()**:
   ```python
   # Creates Judge instance
   judge = Judge()
   
   # Check 1: Task Completion
   completion_score = judge.evaluate(
       criteria="Did the agent complete the requested task?",
       input="Write a Python function...",
       output="def sort_list(lst):...",
   )
   # Returns Score(value=0.95, reason="Task completed successfully")
   
   # Check 2: Correctness
   correctness_score = judge.evaluate(
       criteria="Is the output correct?",
       input="Write a Python function...",
       output="def sort_list(lst):...",
   )
   # Returns Score(value=0.90, reason="Output is correct")
   
   # Check 3: Completeness
   completeness_score = judge.evaluate(
       criteria="Does output fully address input?",
       input="Write a Python function...",
       output="def sort_list(lst):...",
   )
   # Returns Score(value=0.85, reason="Output is complete")
   
   # Calculate average
   avg_score = (0.95 + 0.90 + 0.85) / 3 = 0.90
   
   return CategoryResult(
       name="functional",
       score=0.90,
       weight=0.20,
       checks={...},
       issues=[],
   )
   ```

4. **Other Evaluators Run** (similar process)

5. **Aggregate Scores**:
   ```python
   # Calculate trace score (weighted)
   trace_score = (
       0.90 * 0.20 +  # functional
       0.85 * 0.15 +  # reasoning
       0.80 * 0.15 +  # tool_usage
       0.95 * 0.20 +  # output_quality
       0.82 * 0.15 +  # performance
       0.88 * 0.15    # safety
   ) = 0.87
   ```

6. **Create EvaluationResult**:
   ```python
   return EvaluationResult(
       system_name="my-agent",
       score=0.87,
       status=Status.GOOD,
       categories=[...],
       trace_results=[...],
       summary="1 traces evaluated. Score: 87% (good). 0 issues found.",
       ...
   )
   ```

**State After Evaluate**:
- `agentra._latest_result` contains `EvaluationResult`
- All traces have been evaluated
- Scores calculated and aggregated

```python
# STEP 5: Report
agentra.report()
```

**What Happens**:

1. **Check for Result**:
   ```python
   if not self._latest_result:
       self._latest_result = self.evaluate()  # Auto-evaluate
   ```

2. **Print Report**:
   ```python
   print_report(self._latest_result)
   # Calls report.py functions
   # Prints formatted console output
   ```

```python
# STEP 6: Save
agentra.save("test-run-1")
```

**What Happens**:

1. **Check for Result**:
   ```python
   if not self._latest_result:
       self._latest_result = self.evaluate()
   ```

2. **Save to File**:
   ```python
   save_result(self._latest_result, "test-run-1", "agentra-results")
   # Creates agentra-results/ directory
   # Generates filename: test-run-1_20241215_143022.json
   # Serializes EvaluationResult to JSON
   # Writes to file
   ```

---

## End-to-End Examples

### Example 1: Simple Agent with Auto-Patching

```python
from agentra import Agentra
import openai

# 1. Initialize (patches OpenAI automatically)
agentra = Agentra("code-generator")

# 2. Wrap agent
@agentra.wrap
def generate_code(prompt: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 3. Run agent (trace captured automatically)
result1 = generate_code("Write a Python function to sort a list")
result2 = generate_code("Write a Python function to reverse a string")

# 4. Evaluate
evaluation = agentra.evaluate()

# 5. Report
agentra.report()

# 6. Save
agentra.save("code-gen-test")
```

**Execution Flow**:

```
1. Agentra.__init__()
   └─> patch_openai() → Patches openai.chat.completions.create

2. @agentra.wrap
   └─> Creates wrapper function

3. generate_code("Write a Python...")
   └─> Wrapper executes
       └─> Creates CaptureContext
           └─> __enter__() → Sets context variable
           └─> set_input("Write a Python...")
           └─> Original function executes
               └─> openai.chat.completions.create(...)
                   └─> Patched function executes
                       └─> CaptureContext.get_current()
                       └─> Calls original API
                       └─> Extracts LLM call data
                       └─> ctx.add_llm_call(llm_call)
           └─> set_output("def sort_list...")
           └─> __exit__() → Calculates duration
       └─> Stores trace in agentra._traces

4. agentra.evaluate()
   └─> Creates Evaluator
   └─> For each trace:
       └─> FunctionalEvaluator.evaluate()
           └─> Judge.evaluate() × 3 (completion, correctness, completeness)
       └─> ReasoningEvaluator.evaluate()
       └─> ToolUsageEvaluator.evaluate()
       └─> OutputQualityEvaluator.evaluate()
       └─> PerformanceEvaluator.evaluate()
       └─> SafetyEvaluator.evaluate()
   └─> Aggregates scores
   └─> Returns EvaluationResult

5. agentra.report()
   └─> print_report(evaluation_result)
       └─> Prints formatted console output

6. agentra.save("test-run-1")
   └─> save_result(evaluation_result, "test-run-1", "agentra-results")
       └─> Serializes to JSON
       └─> Writes to file
```

---

### Example 2: Multi-Agent System with Manual Spans

```python
from agentra import Agentra

agentra = Agentra("multi-agent-system")

@agentra.wrap
def complex_workflow(task: str) -> str:
    # Agent 1: Planner
    with agentra.agent("planner", role="Planning Agent"):
        plan = create_plan(task)
    
    # Agent 2: Executor
    with agentra.agent("executor", role="Execution Agent"):
        result = execute_plan(plan)
    
    # Agent 3: Reviewer
    with agentra.agent("reviewer", role="Review Agent"):
        review = review_result(result)
    
    return review

result = complex_workflow("Build a REST API")
agentra.evaluate()
agentra.report()
```

**Execution Flow**:

```
1. complex_workflow("Build a REST API")
   └─> Wrapper creates CaptureContext
       └─> __enter__() → Trace created

2. with agentra.agent("planner", ...)
   └─> CaptureContext.get_current() → Gets active context
   └─> ctx.start_agent_span("planner", role="Planning Agent")
       └─> Creates AgentSpan(name="planner", role="Planning Agent")
       └─> Pushes to _agent_stack
       └─> Adds to trace.agent_spans

3. create_plan(task) executes
   └─> If it calls LLM:
       └─> Patched function captures LLM call
       └─> ctx.add_llm_call() → Adds to trace AND current agent span

4. Agent span ends
   └─> ctx.end_agent_span("planner", output=plan)
       └─> Pops from _agent_stack
       └─> Records end_time, output

5. Same for executor and reviewer agents

6. Trace contains:
   - 3 agent_spans (planner, executor, reviewer)
   - LLM calls associated with each agent
   - Complete workflow trace
```

---

### Example 3: CrewAI with Adaptor

```python
from agentra import Agentra
from agentra.adaptors import CrewAIAdaptor
from crewai import Agent, Task, Crew

agentra = Agentra("dev-crew")

# Create crew
architect = Agent(role="Architect", goal="Design system")
developer = Agent(role="Developer", goal="Implement")
crew = Crew(agents=[architect, developer], tasks=[...])

# Instrument crew
CrewAIAdaptor(agentra).instrument(crew)

# Run crew
crew.kickoff(inputs={"task": "Build REST API"})

# Evaluate
agentra.evaluate()
agentra.report()
```

**Execution Flow**:

```
1. CrewAIAdaptor(agentra).instrument(crew)
   └─> Stores original crew.kickoff
   └─> Creates wrapped_kickoff
       └─> Wraps in agentra.trace()
       └─> Instruments each agent
           └─> Patches agent.execute_task
               └─> Calls on_agent_start/end

2. crew.kickoff(...)
   └─> Wrapped function executes
       └─> Creates CaptureContext (via agentra.trace())
       └─> For each agent execution:
           └─> agent.execute_task() (patched)
               └─> on_agent_start("Architect", ...)
                   └─> ctx.start_agent_span(...)
               └─> Original execute_task runs
                   └─> LLM calls captured automatically
               └─> on_agent_end("Architect", ...)
                   └─> ctx.end_agent_span(...)

3. Trace contains:
   - Framework: "crewai"
   - Multiple agent_spans (one per agent)
   - LLM calls from each agent
   - Task execution order
```

---

## How Everything Connects

### Data Flow Diagram

```
User Code
    │
    ├─> Agentra.__init__()
    │   └─> patches/ (auto-patch LLM clients)
    │
    ├─> @agentra.wrap
    │   └─> agentra.py:wrap()
    │       └─> capture.py:CaptureContext()
    │
    ├─> Function Execution
    │   ├─> capture.py:CaptureContext.__enter__()
    │   │   └─> types.py:Trace() created
    │   │
    │   ├─> LLM Call (patched)
    │   │   └─> patches/openai_patch.py:patched_create()
    │   │       └─> capture.py:CaptureContext.get_current()
    │   │       └─> capture.py:add_llm_call()
    │   │           └─> types.py:LLMCall() added to trace
    │   │
    │   ├─> Tool Call (if any)
    │   │   └─> capture.py:add_tool_call()
    │   │       └─> types.py:ToolCall() added to trace
    │   │
    │   └─> capture.py:CaptureContext.__exit__()
    │       └─> Trace stored in agentra._traces
    │
    ├─> agentra.evaluate()
    │   └─> evaluate.py:Evaluator.evaluate()
    │       └─> For each trace:
    │           ├─> evaluators/functional.py:FunctionalEvaluator.evaluate()
    │           │   └─> judge.py:Judge.evaluate() (LLM-as-judge)
    │           ├─> evaluators/reasoning.py:ReasoningEvaluator.evaluate()
    │           ├─> evaluators/tool_usage.py:ToolUsageEvaluator.evaluate()
    │           ├─> evaluators/output_quality.py:OutputQualityEvaluator.evaluate()
    │           ├─> evaluators/performance.py:PerformanceEvaluator.evaluate()
    │           └─> evaluators/safety.py:SafetyEvaluator.evaluate()
    │       └─> Aggregates scores
    │       └─> Returns types.py:EvaluationResult
    │
    ├─> agentra.report()
    │   └─> report.py:print_report()
    │       └─> Prints formatted output
    │
    └─> agentra.save()
        └─> results.py:save_result()
            └─> Serializes to JSON
            └─> Writes to file
```

### Context Variable Flow

```
Thread/Async Context
    │
    └─> contextvars.ContextVar("agentra_context")
        │
        ├─> CaptureContext.__enter__()
        │   └─> _current_context.set(self)
        │       └─> Context variable set for this execution context
        │
        ├─> Patched LLM function
        │   └─> CaptureContext.get_current()
        │       └─> _current_context.get()
        │           └─> Returns active CaptureContext (if any)
        │
        └─> CaptureContext.__exit__()
            └─> _current_context.reset(token)
                └─> Context variable reset
```

### Trace Lifecycle

```
1. Creation
   └─> CaptureContext.__init__()
       └─> Trace(id=uuid4(), name=None)

2. Capture
   └─> add_llm_call() → Adds LLMCall to trace.llm_calls
   └─> add_tool_call() → Adds ToolCall to trace.tool_calls
   └─> start_agent_span() → Creates AgentSpan, adds to trace.agent_spans

3. Completion
   └─> CaptureContext.__exit__()
       └─> Sets trace.end_time, trace.duration_ms
       └─> Captures error if any

4. Storage
   └─> agentra._traces.append(trace)

5. Evaluation
   └─> Evaluator.evaluate([trace])
       └─> Each evaluator analyzes trace
       └─> Creates TraceResult

6. Aggregation
   └─> EvaluationResult created
       └─> Contains all TraceResults
       └─> Contains aggregate scores
```

---

## Key Design Patterns

### 1. Decorator Pattern
- `@agentra.wrap` wraps functions to add instrumentation
- Transparent to user code

### 2. Context Manager Pattern
- `with agentra.trace()` for manual tracing
- `with agentra.agent()` for agent boundaries
- Uses Python's context manager protocol

### 3. Monkey Patching
- Patches LLM clients to intercept calls
- Stores original functions for restoration

### 4. Strategy Pattern
- Evaluators are pluggable strategies
- Easy to add new evaluation categories

### 5. Observer Pattern (via Context Variables)
- Patched functions observe active context
- Automatically capture when context exists

### 6. Factory Pattern
- `Evaluator` creates evaluator instances
- `Judge` creates LLM client based on available keys

---

## Common Questions & Answers

### Q: How does auto-patching work?
**A**: When `Agentra` is initialized with `auto_patch=True`, it monkey-patches LLM client libraries. It stores the original function, creates a wrapper that captures calls, and replaces the original. The wrapper checks for an active `CaptureContext` and records the call if one exists.

### Q: How does context tracking work across async boundaries?
**A**: Uses Python's `contextvars` module, which is designed for async-safe context tracking. Each async task gets its own context copy, so traces don't interfere with each other.

### Q: What happens if there's no active context?
**A**: Patched functions check `CaptureContext.get_current()`. If it returns `None`, the call proceeds normally but isn't captured. This allows the library to work even when not actively tracing.

### Q: How are scores calculated?
**A**: Each evaluator returns a score (0.0-1.0) for its category. Scores are weighted and averaged:
- Trace score = weighted sum of category scores
- Overall score = weighted sum of category averages
- Status determined by overall score thresholds

### Q: How does the LLM judge work?
**A**: Creates a prompt asking the LLM to evaluate based on criteria. Parses the response to extract a score (0.0-1.0) and reason. Falls back to heuristics if parsing fails.

### Q: Can I use Agentra without LLM API keys?
**A**: Yes, but evaluation will be less accurate. Evaluators that use heuristics (Performance, ToolUsage, Reasoning) will still work. Evaluators that use LLM judge (Functional, OutputQuality, Safety) will fail gracefully and return neutral scores.

### Q: How do adaptors work?
**A**: Adaptors monkey-patch framework methods to add callbacks. When framework events occur (agent starts, task executes, etc.), adaptors call `on_agent_start/end` which creates `AgentSpan` objects in the trace.

### Q: What's the difference between a Trace and an AgentSpan?
**A**: A `Trace` represents one complete execution of the wrapped function. An `AgentSpan` represents one agent's execution within that trace (for multi-agent systems). A trace can contain multiple agent spans.

### Q: How is sampling implemented?
**A**: In the wrapper function, `random.random()` is compared to `sample_rate`. If the random number exceeds the rate, the function executes normally without creating a trace. This allows production monitoring without capturing every request.

### Q: How are results stored?
**A**: Results are serialized to JSON using `dataclasses.asdict()`. Datetime objects are converted to ISO format strings. Files are named with timestamp for uniqueness.

---

## Summary

Agentra is built on these core principles:

1. **Transparent Instrumentation**: Auto-patching and decorators make instrumentation invisible
2. **Context-Aware Capture**: Uses `contextvars` for async-safe trace tracking
3. **Modular Evaluation**: Pluggable evaluators for different quality dimensions
4. **Framework Integration**: Adaptors provide rich instrumentation for specific frameworks
5. **Comprehensive Reporting**: Human-readable reports with actionable insights

The architecture is designed to be:
- **Non-intrusive**: Minimal code changes required
- **Extensible**: Easy to add evaluators and adaptors
- **Robust**: Graceful error handling throughout
- **Production-ready**: Sampling support, efficient capture, JSON storage

This documentation should enable you to understand and answer questions about any aspect of Agentra's implementation.

