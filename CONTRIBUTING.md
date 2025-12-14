# Contributing to Agentra

Thank you for your interest in contributing to Agentra! This guide will help you get started.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agentra.git
cd agentra
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
```

4. Install optional dependencies for testing:
```bash
pip install openai anthropic crewai langchain
```

## Project Structure

```
agentra/
├── agentra/
│   ├── __init__.py          # Public exports
│   ├── agentra.py           # Main class
│   ├── types.py             # Data types
│   ├── capture.py           # Trace capture
│   ├── evaluate.py          # Evaluation orchestrator
│   ├── judge.py             # LLM-as-judge
│   ├── report.py            # Report generation
│   ├── results.py           # Save/load results
│   ├── patches/             # Auto-patching LLM clients
│   ├── adaptors/            # Framework adaptors
│   └── evaluators/          # Evaluation categories
├── examples/                # Usage examples
├── README.md
├── CONTRIBUTING.md
└── setup.py
```

## Adding a New Framework Adaptor

To add support for a new AI framework:

1. Create a new file in `agentra/adaptors/`:

```python
# agentra/adaptors/myframework.py

from .base import BaseAdaptor

class MyFrameworkAdaptor(BaseAdaptor):
    """
    Adaptor for MyFramework.
    
    Captures:
    - [List what you capture]
    """
    
    def instrument(self, target) -> None:
        """Instrument MyFramework object."""
        
        # Hook into framework callbacks/methods
        original_method = target.some_method
        
        def wrapped_method(*args, **kwargs):
            # Start tracking
            self.on_agent_start("agent_name", ...)
            
            try:
                result = original_method(*args, **kwargs)
                self.on_agent_end("agent_name", output=result)
                return result
            except Exception as e:
                self.on_agent_end("agent_name", error=str(e))
                raise
        
        target.some_method = wrapped_method
```

2. Add to `agentra/adaptors/__init__.py`:

```python
from .myframework import MyFrameworkAdaptor

__all__ = [
    ...,
    "MyFrameworkAdaptor",
]
```

3. Document usage in README.md

4. Create an example in `examples/myframework_example.py`

## Adding a New Evaluator

To add a new evaluation category:

1. Create a new file in `agentra/evaluators/`:

```python
# agentra/evaluators/mycategory.py

from .base import BaseEvaluator
from ..types import Trace, CategoryResult, Score

class MyCategoryEvaluator(BaseEvaluator):
    """Evaluates [what this evaluates]."""
    
    name = "my_category"
    
    def evaluate(self, trace: Trace, system_description: str = "") -> CategoryResult:
        checks = {}
        issues = []
        
        # Your evaluation logic here
        # Use self._some_helper() for complex checks
        
        # Calculate score
        avg_score = sum(s.value for s in checks.values()) / len(checks)
        
        return CategoryResult(
            name=self.name,
            score=avg_score,
            weight=0.10,  # Default weight
            checks=checks,
            issues=issues,
        )
```

2. Add to `agentra/evaluators/__init__.py`

3. Add to default evaluators in `agentra/evaluate.py`

4. Update README with new category description

## Code Style

- Follow PEP 8
- Use type hints
- Keep functions focused and under 50 lines when possible
- Document public APIs with docstrings
- Use descriptive variable names

## Testing

Before submitting a PR:

1. Test your changes with examples:
```bash
python examples/simple_example.py
```

2. Ensure no linting errors:
```bash
# If you have a linter installed
pylint agentra/
```

3. Test with different frameworks (if applicable)

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### PR Guidelines

- Clear title and description
- Reference any related issues
- Include examples if adding new features
- Update documentation as needed
- Ensure no breaking changes (or clearly document them)

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Questions about implementation
- Documentation improvements

## Areas We'd Love Help With

- [ ] Additional framework adaptors (Haystack, AutoGPT, etc.)
- [ ] More sophisticated evaluators
- [ ] Performance optimization
- [ ] Documentation improvements
- [ ] Example notebooks
- [ ] Integration tests
- [ ] Cost estimation improvements
- [ ] Visualization/dashboard for results
- [ ] Export to other formats (CSV, HTML reports)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

