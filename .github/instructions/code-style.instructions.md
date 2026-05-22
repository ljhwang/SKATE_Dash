---
applyTo: "**/*.py"
---

# Python Coding Conventions

## Style Guide
- Follow [PEP 8](https://peps.python.org/pep-0008/) for all Python code.
- Use 4 spaces for indentation (no tabs).
- Limit all lines to a maximum of 79 characters.
- Use blank lines to separate top-level definitions (2 blank lines) and method definitions (1 blank line).
- Use `snake_case` for function and variable names.
- Use `CamelCase` for class names.
- Use `UPPER_CASE` for constants.

## Type Hints
- **Always** include type hints for all function parameters and return values.
- Use `Optional[X]` or `X | None` for nullable types.

```python
# Good
def calculate_score(name: str, value: int) -> float:
    ...

# Bad
def calculate_score(name, value):
    ...
```

## Docstrings
- Use **Google-style docstrings** for all public modules, classes, functions, and methods.

```python
def fetch_data(url: str, timeout: int = 30) -> dict:
    """Fetch data from the given URL.

    Args:
        url: The URL to fetch data from.
        timeout: Request timeout in seconds.

    Returns:
        A dictionary containing the response data.

    Raises:
        ValueError: If the URL is invalid.
        TimeoutError: If the request exceeds the timeout.
    """
```

## Imports
- Group imports in this order, separated by blank lines:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
- Use absolute imports over relative imports.
- Avoid wildcard imports (`from module import *`).

## Error Handling
- Catch specific exceptions, not bare `except:` clauses.
- Always provide meaningful error messages.

## General
- Prefer list/dict/set comprehensions over loops where readable.
- Avoid mutable default arguments (use `None` and set inside the function).
- Use `f-strings` for string formatting (Python 3.6+).
