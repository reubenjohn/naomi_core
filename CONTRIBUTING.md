# Contributing to NAOMI Core

NAOMI Core is a Python package that provides core functionality for LLM-powered assistants. This guide will help you set up your development environment and contribute to the project.

**Requirements: Python 3.10+**

## Setting up your development environment

1. Fork the repository on GitHub
2. Clone your fork: `git clone git@github.com:YOUR_USERNAME/naomi_core.git`
3. Enter the directory: `cd naomi_core`
4. Install the project: `make install` (uses Poetry)

## Development workflow

1. Create a new branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Format the code: `make fmt` (runs isort and black)
4. Run the linter: `make lint` (runs flake8, black --check, mypy)
5. Run tests: `make test` (pytest with coverage)
6. Commit your changes using [conventional commits](https://www.conventionalcommits.org/):
   - Format: `<type>(<scope>): <description>`
   - Example: `feat(assistant): add streaming support for agent responses`
   - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`
7. Push your changes: `git push origin feature/my-feature`
8. Submit a pull request

## Code standards

- **Type hints**: Use comprehensive type hints for all functions and methods
- **Docstrings**: Include docstrings for all public functions, methods, and classes
- **Testing**: Try to maintain >99% test coverage for all new code and mark intentionally untested code with exclusions
- **Error handling**: Use explicit exception handling with specific exception types
- **Formatting**: Code is formatted with Black (100 char line length) and isort

## Useful commands

```bash
make help              # Show available commands
make install           # Install the project in development mode
make fmt               # Format code with isort and black
make lint              # Run linters (flake8, black --check, mypy)
make test              # Run tests with coverage report
make watch             # Run tests on file changes
make docs              # Build documentation locally
make clean             # Clean up build artifacts
```

## VS Code setup

Install the following extensions:
- Python (ms-python.python)
- Flake8 (ms-python.flake8)
- MyPy (ms-python.mypy-type-checker) 
- Black Formatter (ms-python.black-formatter)

Create `.vscode/settings.json`:
```json
{
    "python.analysis.autoImportCompletions": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "flake8.importStrategy": "fromEnvironment",
    "mypy-type-checker.importStrategy": "fromEnvironment",
    "black-formatter.importStrategy": "fromEnvironment",
    "editor.formatOnSave": true,
    "python.formatting.provider": "black"
}
```

## Project architecture

- **naomi_core/assistant/**: Contains agent functionality and persistence
- **naomi_core/db.py**: Database connection and session management
- **tests/**: Mirror the package structure with corresponding test files

## Making a release

NAOMI Core uses [semantic versioning](https://semver.org/):
1. Ensure all tests pass and documentation is updated
2. Run `make release` and specify the new version number
3. The release process will create a tag and trigger the CI/CD pipeline