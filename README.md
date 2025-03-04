# NAOMI Core

[![codecov](https://codecov.io/gh/reubenjohn/naomi_core/branch/main/graph/badge.svg?token=naomi_core_token_here)](https://codecov.io/gh/reubenjohn/naomi_core/branch/main)
[![CI](https://github.com/reubenjohn/naomi_core/actions/workflows/main.yml/badge.svg)](https://github.com/reubenjohn/naomi_core/actions/workflows/main.yml)

NAOMI Core is a Python package that provides the foundational components for building LLM-powered assistants.

## Overview

NAOMI Core provides a robust framework for creating, managing, and interacting with LLM-powered agents. The library abstracts away the complexity of working directly with language models, allowing developers to focus on building applications with advanced AI capabilities.

### Key Features

- **Agent Management**: Create and manage AI agents with different roles and capabilities
- **Persistence Layer**: Store and retrieve conversation history and agent state
- **Database Integration**: SQLAlchemy-based ORM for flexible data storage options
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Extensibility**: Designed to be easily extended with new capabilities

## Installation

```bash
# Install with pip
pip install naomi-core

# Or install with Poetry
poetry add naomi-core
```

For development installation:
```bash
# Clone the repository
git clone https://github.com/reubenjohn/naomi_core.git
cd naomi_core

# Install dependencies
make install
```

## Project Structure

```
naomi_core/
├── assistant/       # Agent and conversation management
│   ├── agent.py     # Core Agent implementation
│   └── persistence.py  # Persistence layer for conversations
├── db.py            # Database connection and session management
```

## Documentation

For detailed usage examples and API reference, visit our [documentation site](https://reubenjohn.github.io/naomi_core/).

## Development

NAOMI Core is developed using modern Python practices:

- Python 3.10+ with type hints
- Black and isort for code formatting
- Pytest for testing
- SQLAlchemy for database operations

For development setup and guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
