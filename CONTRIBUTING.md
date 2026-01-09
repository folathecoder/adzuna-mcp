# Contributing to Adzuna MCP Server

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10+
- Git

### Local Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/folarinakinloye/adzuna-mcp.git
   cd adzuna-mcp
   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your Adzuna API credentials
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=server --cov-report=html

# Run specific test file
pytest tests/test_server.py -v
```

## Code Style

This project uses:
- **ruff** for linting and formatting
- **mypy** for type checking

### Before committing

```bash
# Format code
ruff format .

# Check for linting issues
ruff check .

# Type check
mypy server.py --ignore-missing-imports
```

## Making Changes

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring

### Commit Messages

Use clear, descriptive commit messages:

```
Add salary currency conversion helper

- Added convert_salary() function
- Updated search_jobs to use converter
- Added tests for currency conversion
```

### Pull Request Process

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** with appropriate tests
3. **Ensure tests pass** (`pytest`)
4. **Ensure code is formatted** (`ruff format .`)
5. **Update documentation** if needed
6. **Submit a pull request**

### PR Description Template

```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
How were these changes tested?

## Checklist
- [ ] Tests pass locally
- [ ] Code is formatted with ruff
- [ ] Documentation updated (if applicable)
```

## Adding New Tools

When adding a new MCP tool:

1. **Add the function** in `server.py` with the `@mcp.tool` decorator
2. **Write comprehensive docstrings** including:
   - PURPOSE section explaining when to use the tool
   - Detailed Args with types and examples
   - Returns section with response schema
   - Example response
   - Errors section
3. **Add tests** in `tests/test_server.py`
4. **Update README.md** with the new tool

### Tool Docstring Template

```python
@mcp.tool
async def new_tool(param1: str, param2: Optional[int] = None) -> dict:
    """
    Brief one-line description.

    PURPOSE: Explain when and why to use this tool.

    Args:
        param1: Description with examples.
        param2: Description with default behavior.

    Returns:
        dict: Description of response structure:
            - field1: Description
            - field2: Description

    Example response:
        {
            "field1": "value",
            "field2": 123
        }

    Errors:
        - Error condition: "Error message format"
    """
```

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)

## Questions?

Feel free to open an issue for questions or discussion.
