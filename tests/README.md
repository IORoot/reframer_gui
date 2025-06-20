# Reframer GUI Backend Testing Framework

This directory contains a comprehensive testing framework for the Reframer GUI backend Python scripts. The framework uses pytest and provides both unit and integration tests.

## Directory Structure

```
tests/
├── __init__.py              # Makes tests a Python package
├── conftest.py              # Pytest configuration and fixtures
├── test_main.py             # Tests for main.py script
├── test_object_detector.py  # Tests for object detection
├── test_video_processor.py  # Tests for video processing
├── test_ffmpeg_manager.py   # Tests for FFmpeg management
├── requirements-test.txt    # Testing dependencies
├── run_tests.py            # Test runner script
└── README.md               # This file
```

## Quick Start

### 1. Install Test Dependencies

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Or use the test runner with auto-install
python tests/run_tests.py --install-deps
```

### 2. Run Tests

```bash
# Run all tests
python tests/run_tests.py

# Run with coverage
python tests/run_tests.py --coverage

# Run only unit tests
python tests/run_tests.py --type unit

# Run only integration tests
python tests/run_tests.py --type integration

# Run fast tests (skip slow ones)
python tests/run_tests.py --type fast

# Run with verbose output
python tests/run_tests.py --verbose

# Run in parallel
python tests/run_tests.py --parallel

# Generate HTML report
python tests/run_tests.py --output html
```

## Test Categories

### Unit Tests
- Test individual functions and classes in isolation
- Use mocks to avoid external dependencies
- Fast execution
- Marked with `@pytest.mark.unit`

### Integration Tests
- Test component interactions
- May require real video files or external tools
- Slower execution
- Marked with `@pytest.mark.integration`

### Fast Tests
- Tests that complete quickly
- Exclude slow operations
- Use `@pytest.mark.slow` to mark slow tests

## Test Markers

The framework uses pytest markers to categorize tests:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (can be skipped with `-m "not slow"`)
- `@pytest.mark.requires_video` - Tests that need a sample video file

## Fixtures

Common fixtures are defined in `conftest.py`:

- `test_data_dir` - Temporary directory for test data
- `sample_video_path` - Path to sample video (if available)
- `output_dir` - Temporary directory for test outputs
- `debug_dir` - Temporary directory for debug outputs
- `models_dir` - Path to models directory
- `python_dir` - Path to Python backend directory

## Running Specific Tests

### Using pytest directly:

```bash
# Run specific test file
pytest tests/test_main.py

# Run specific test class
pytest tests/test_main.py::TestMainArgumentParsing

# Run specific test method
pytest tests/test_main.py::TestMainArgumentParsing::test_parse_args_required_arguments

# Run tests matching pattern
pytest -k "test_parse_args"

# Run tests with specific marker
pytest -m "unit"
pytest -m "integration"
pytest -m "not slow"
```

### Using the test runner:

```bash
# Run all tests
python tests/run_tests.py

# Run specific test types
python tests/run_tests.py --type unit
python tests/run_tests.py --type integration
python tests/run_tests.py --type fast
```

## Coverage Reports

Generate coverage reports to see which code is tested:

```bash
# Generate coverage report
python tests/run_tests.py --coverage

# This will create:
# - Terminal coverage summary
# - HTML coverage report in htmlcov/
```

## Test Output Formats

The test runner supports multiple output formats:

```bash
# Text output (default)
python tests/run_tests.py

# HTML report
python tests/run_tests.py --output html
# Creates: test_results.html

# JSON report
python tests/run_tests.py --output json
# Creates: test_results.json
```

## Continuous Integration

For CI/CD pipelines, you can run tests with:

```bash
# Install dependencies and run tests
pip install -r tests/requirements-test.txt
python tests/run_tests.py --type fast --coverage
```

## Writing New Tests

### 1. Create a new test file

```python
# tests/test_new_module.py
import pytest
from unittest.mock import Mock, patch

# Import the module to test
from new_module import NewClass

class TestNewClass:
    """Test the NewClass functionality."""
    
    def test_new_class_init(self):
        """Test NewClass initialization."""
        obj = NewClass()
        assert obj is not None
    
    @pytest.mark.unit
    def test_new_class_method(self):
        """Test a method of NewClass."""
        obj = NewClass()
        result = obj.some_method()
        assert result == expected_value
    
    @pytest.mark.integration
    def test_new_class_integration(self):
        """Test NewClass integration with other components."""
        # Integration test code here
        pass
```

### 2. Use appropriate markers

- Use `@pytest.mark.unit` for unit tests
- Use `@pytest.mark.integration` for integration tests
- Use `@pytest.mark.slow` for slow tests
- Use `@pytest.mark.requires_video` for tests needing video files

### 3. Use fixtures when needed

```python
def test_with_fixtures(sample_video_path, output_dir):
    """Test using fixtures."""
    if not sample_video_path:
        pytest.skip("Sample video not available")
    
    # Test code here
    pass
```

### 4. Mock external dependencies

```python
@patch('module.external_dependency')
def test_with_mock(mock_dependency):
    """Test with mocked external dependency."""
    mock_dependency.return_value = "mocked_result"
    
    # Test code here
    pass
```

## Best Practices

1. **Test Naming**: Use descriptive test names that explain what is being tested
2. **Arrange-Act-Assert**: Structure tests with clear sections
3. **Mock External Dependencies**: Don't rely on external services in unit tests
4. **Use Fixtures**: Share common setup code using fixtures
5. **Test Edge Cases**: Include tests for error conditions and edge cases
6. **Keep Tests Fast**: Unit tests should run quickly
7. **Use Appropriate Markers**: Mark tests correctly for filtering

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the Python backend directory is in the Python path
2. **Missing Dependencies**: Install test requirements with `pip install -r tests/requirements-test.txt`
3. **Video File Not Found**: Some tests require `landscape_10secs.mp4` in the project root
4. **FFmpeg Not Available**: Some tests may fail if FFmpeg is not installed

### Debug Mode

Run tests with verbose output to see more details:

```bash
python tests/run_tests.py --verbose
```

### Running Individual Tests

To debug a specific test:

```bash
# Run with maximum verbosity
pytest tests/test_main.py::TestMainArgumentParsing::test_parse_args_required_arguments -vvv

# Run with print statement output
pytest tests/test_main.py::TestMainArgumentParsing::test_parse_args_required_arguments -s
```

## Contributing

When adding new features to the backend:

1. Write tests for new functionality
2. Ensure existing tests still pass
3. Add appropriate markers to new tests
4. Update this README if needed
5. Run the full test suite before submitting changes

## Test Maintenance

- Keep tests up to date with code changes
- Remove obsolete tests
- Refactor tests when code is refactored
- Monitor test execution time and optimize slow tests
- Update test dependencies as needed 