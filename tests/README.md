# AI Terminal Tests

This directory contains the test suite for the AI Terminal application. The tests are organized into unit and integration tests to ensure comprehensive coverage of the application's functionality.

## Test Structure

- `unit/`: Contains unit tests for individual components
  - `test_llm_client.py`: Tests for the Mistral API client
  - `test_context_manager.py`: Tests for context management
  - `test_command_handler.py`: Tests for command handling
  - `test_document_handler.py`: Tests for document processing
  - `test_conversation_handler.py`: Tests for conversation handling

- `integration/`: Contains integration tests
  - `test_main_flow.py`: Tests the main application flow
  - `test_zsh_integration.py`: Tests ZSH integration
  - `test_uninstall.py`: Tests the uninstallation process

- `fixtures/`: Contains test fixtures and test data

## Running Tests

To run all tests:

```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=src --cov-report=html tests/
```

To run specific test categories:

```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run a specific test file
pytest tests/unit/test_llm_client.py

# Run a specific test case
pytest tests/unit/test_llm_client.py::TestMistralClient::test_generate_response
```

## Test Coverage

The test suite aims to cover:

1. **Core Functionality**
   - LLM client communication
   - Context management
   - Mode detection
   - Command execution

2. **Handlers**
   - Command generation and execution
   - Document processing
   - Conversation flow

3. **Integration**
   - ZSH completion
   - Installation and uninstallation
   - Configuration management

## Writing New Tests

When adding new features or fixing bugs, please add corresponding tests. Follow these guidelines:

1. Place unit tests in `tests/unit/` and integration tests in `tests/integration/`.
2. Name test files with the prefix `test_`.
3. Use descriptive test method names that start with `test_`.
4. Use fixtures for common test setup (see `conftest.py`).
5. Mock external dependencies to keep tests fast and reliable.

## Fixtures

Common test fixtures are defined in `conftest.py`. These include:

- `tmp_path`: Temporary directory for test files
- `mock_llm_client`: Mocked LLM client
- `mock_context_manager`: Mocked context manager
- `test_config`: Test configuration

## Continuous Integration

Tests are automatically run on pull requests and merges to the main branch. The CI pipeline checks for:

- Test pass/fail status
- Code coverage thresholds
- Code style compliance

## Debugging Tests

To debug a failing test:

```bash
# Run with detailed output
pytest -v tests/path/to/test_file.py::test_name

# Drop to PDB on failure
pytest --pdb tests/path/to/test_file.py::test_name

# Show print output
pytest -s tests/path/to/test_file.py::test_name
```
