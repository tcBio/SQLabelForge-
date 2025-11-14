# SQLabelForge Development Standards

This document outlines the development standards, best practices, and guidelines for contributing to SQLabelForge.

## Project Overview

SQLabelForge is a high-performance, open-source tool for querying SQL Server databases and creating labeled training datasets with OSS20B integration. The project emphasizes:

- **Security**: SQL injection protection, secure credential management
- **Performance**: GPU acceleration, connection pooling, efficient data processing
- **Flexibility**: Multiple labeling strategies, various export formats
- **Maintainability**: Clean code, comprehensive documentation, thorough testing

## Technology Stack

- **Language**: Python 3.9+
- **Database**: SQL Server (via pyodbc/SQLAlchemy)
- **Web Framework**: FastAPI
- **Data Processing**: pandas, numpy
- **Optional GPU**: cupy
- **Configuration**: YAML, python-dotenv
- **Testing**: pytest
- **Code Quality**: black, isort, pylint, mypy

## Code Style

### Python Style Guide

Follow PEP 8 with these specifics:

- **Line length**: 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings
- **Imports**: Organized with isort

### Formatting Tools

```bash
# Format code
black sqlabelforge/

# Sort imports
isort sqlabelforge/

# Type checking
mypy sqlabelforge/

# Linting
pylint sqlabelforge/
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `SQLConnector`, `DataProcessor`)
- **Functions/Methods**: snake_case (e.g., `execute_query`, `apply_labels`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`)
- **Private methods**: _leading_underscore (e.g., `_create_engine`)
- **Module names**: snake_case (e.g., `sql_connector.py`)

### Documentation

All public modules, classes, and functions must have docstrings:

```python
def execute_query(
    self,
    query: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 300,
) -> List[Dict[str, Any]]:
    """
    Execute a parameterized SELECT query.

    Args:
        query: SQL query with :param_name placeholders
        params: Dictionary of parameter values
        timeout: Query timeout in seconds

    Returns:
        List of dictionaries representing rows

    Raises:
        ValueError: If query is invalid
        TimeoutError: If query exceeds timeout

    Example:
        results = connector.execute_query(
            "SELECT * FROM users WHERE id = :user_id",
            {"user_id": 123}
        )
    """
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import Any, Dict, List, Optional

def process_data(
    data: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    pass
```

## Architecture

### Project Structure

```
sqlabelforge/
├── core/              # Core business logic
│   ├── sql_connector.py
│   ├── data_processor.py
│   ├── labeling_engine.py
│   └── model_interface.py
├── api/               # REST API endpoints
│   └── endpoints.py
└── utils/            # Utility functions
    └── config_loader.py
```

### Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Injection**: Pass dependencies rather than creating them internally
3. **Configuration over Code**: Use configuration files for customization
4. **Fail Fast**: Validate inputs early and raise clear exceptions
5. **Clean Resources**: Always close connections and cleanup properly

### Error Handling

```python
# Good: Specific exception with clear message
if not query:
    raise ValueError("Query cannot be empty")

# Good: Catch specific exceptions
try:
    result = conn.execute(query)
except SQLAlchemyError as e:
    logger.error(f"Query execution failed: {e}")
    raise

# Bad: Bare except
try:
    result = conn.execute(query)
except:  # Don't do this!
    pass
```

### Logging

Use structured logging throughout:

```python
import logging

logger = logging.getLogger(__name__)

# Info for normal operations
logger.info(f"Connected to database {database}")

# Warning for recoverable issues
logger.warning(f"Retrying connection after {delay}s")

# Error for failures
logger.error(f"Failed to execute query: {error}")

# Debug for detailed information
logger.debug(f"Query parameters: {params}")
```

## Security

### SQL Injection Prevention

**Always** use parameterized queries:

```python
# Good: Parameterized query
query = "SELECT * FROM users WHERE id = :user_id"
results = connector.execute_query(query, {"user_id": user_id})

# Bad: String formatting (SQL injection risk!)
query = f"SELECT * FROM users WHERE id = {user_id}"  # NEVER DO THIS!
```

### Credential Management

1. **Never commit credentials** to version control
2. **Use environment variables** for secrets
3. **Support secure authentication** methods (Windows Auth, Azure AD)
4. **Rotate credentials** regularly

```python
# Good: Read from environment
password = os.getenv("SQL_PASSWORD")

# Bad: Hard-coded credentials
password = "my_secret_password"  # NEVER DO THIS!
```

### Input Validation

Validate all user inputs:

```python
def set_timeout(self, timeout: int):
    if timeout < 0:
        raise ValueError("Timeout must be non-negative")
    if timeout > 3600:
        raise ValueError("Timeout cannot exceed 3600 seconds")
    self.timeout = timeout
```

## Testing

### Test Structure

```
tests/
├── test_sql_connector.py
├── test_data_processor.py
├── test_labeling_engine.py
└── test_api.py
```

### Writing Tests

```python
import pytest
from sqlabelforge.core.data_processor import DataProcessor

class TestDataProcessor:
    """Test suite for DataProcessor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = DataProcessor()

    def test_process_empty_data(self):
        """Test processing empty dataset."""
        result = self.processor.process_query_results([])
        assert len(result) == 0

    def test_process_valid_data(self):
        """Test processing valid dataset."""
        data = [{"id": 1, "name": "test"}]
        result = self.processor.process_query_results(data)
        assert len(result) == 1
        assert result.iloc[0]["id"] == 1

    def test_invalid_aggregation(self):
        """Test error handling for invalid aggregation."""
        with pytest.raises(ValueError):
            self.processor.aggregate(None, None)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sqlabelforge

# Run specific test file
pytest tests/test_data_processor.py

# Run specific test
pytest tests/test_data_processor.py::TestDataProcessor::test_process_valid_data
```

## Performance

### Database Connection Pooling

Always use connection pooling for multiple queries:

```python
# Good: Reuse connector
connector = SQLConnector(...)
for query in queries:
    results = connector.execute_query(query)
connector.close()

# Bad: Create new connection each time
for query in queries:
    connector = SQLConnector(...)  # Expensive!
    results = connector.execute_query(query)
    connector.close()
```

### Batch Processing

Process large datasets in chunks:

```python
# Good: Chunked processing
processor = DataProcessor(chunk_size=10000)
for chunk in chunks:
    process_chunk(chunk)

# Bad: Load everything into memory
all_data = load_entire_dataset()  # May cause OOM!
```

### GPU Acceleration

Use GPU for large-scale operations when available:

```python
processor = DataProcessor(use_gpu=True)
```

## Git Workflow

### Branch Naming

- **Feature**: `feature/description`
- **Bug fix**: `fix/description`
- **Documentation**: `docs/description`
- **Refactor**: `refactor/description`

### Commit Messages

Follow conventional commits:

```
feat: add model-assisted labeling support
fix: resolve connection pool timeout issue
docs: update configuration guide
refactor: simplify query execution logic
test: add tests for labeling engine
```

### Pull Request Process

1. Create feature branch from `develop`
2. Make changes with clear commits
3. Add/update tests
4. Update documentation
5. Run code quality checks
6. Submit PR with description
7. Address review comments
8. Merge after approval

## Release Process

### Version Numbers

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create git tag
- [ ] Build package
- [ ] Publish to PyPI
- [ ] Create GitHub release

## Contributing

### Getting Started

1. Fork the repository
2. Clone your fork
3. Create feature branch
4. Install development dependencies: `pip install -e ".[dev]"`
5. Make changes
6. Run tests and quality checks
7. Submit pull request

### Code Review Guidelines

Reviewers should check:

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Error handling is proper

### Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Document your changes
- Test thoroughly

## Additional Resources

- [Quick Start Guide](docs/QUICKSTART.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [API Documentation](docs/API.md)
- [Issue Tracker](https://github.com/yourusername/SQLabelForge/issues)

## Questions?

Open an issue or start a discussion on GitHub.
