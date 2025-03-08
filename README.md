# NAOMI Core

[![codecov](https://codecov.io/gh/reubenjohn/naomi_core/branch/main/graph/badge.svg?token=naomi_core_token_here)](https://codecov.io/gh/reubenjohn/naomi_core/branch/main)
[![CI](https://github.com/reubenjohn/naomi_core/actions/workflows/main.yml/badge.svg)](https://github.com/reubenjohn/naomi_core/actions/workflows/main.yml)

NAOMI Core is a Python package that provides the foundational components for building LLM-powered assistants.

## Overview

NAOMI Core provides a robust framework for creating, managing, and interacting with LLM-powered agents. The library abstracts away the complexity of working directly with language models, allowing developers to focus on building applications with advanced AI capabilities.

NAOMI Core is the foundational library that powers NAOMI, providing shared functionality for both `naomi_streamlit` (the user-facing Streamlit application) and `naomi_api` (the FastAPI server for push notifications and webhook integration). It manages core logic, data processing, and database interactions to enable intelligent, autonomous operations.

### Key Features

#### Currently Implemented
- **Agent Management**: Create and manage AI agents with different roles and capabilities
- **Persistence Layer**: Store and retrieve conversation history and agent state
- **Database Integration**: SQLAlchemy-based ORM for flexible data storage options
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Google Calendar Integration**: Connect to and manage Google Calendar events

#### Planned
- **Extensibility**: Framework for easily extending with new capabilities
- **Event-driven Architecture**: Support for automated triggers and event handling

## Features

#### Currently Implemented
- **Database Management**: Interfaces with the shared database, handling data related to:
  - Conversations
  - Agent states and history
- **Google Calendar Tool**: Fetch events, list calendars, and manage calendar data

#### Planned
- **Responsibilities Management**: Database structures for user-defined and system-suggested responsibilities
- **Events and Triggers**: Infrastructure for event capture and automated response
- **Core Reasoning**: Advanced logic and reasoning capabilities for NAOMI's decision-making
- **Shared Utilities**: Common functions and helper modules for `naomi_streamlit` and `naomi_api`
- **Event Processing**: Handlers for event-based workflows enabling proactive engagement
- **Reasoning and Observations**: Storage and processing of insights about internal operations

## Installation

```bash
# Install with pip
pip install naomi-core

# Or install with Poetry
poetry add naomi-core
```

To install `naomi_core`, clone the repository and install its dependencies using Poetry:

```sh
git clone https://github.com/reubenjohn/naomi_core.git
cd naomi_core
poetry install
```

For development installation:
```bash
# Clone the repository
git clone https://github.com/reubenjohn/naomi_core.git
cd naomi_core

# Install dependencies
make install
```

## Usage

`naomi_core` is designed to be used as a dependency in `naomi_streamlit` and `naomi_api`. To use it in another project, add it as a dependency in `pyproject.toml`:

```toml
[tool.poetry.dependencies]
naomi_core = { git = "https://github.com/reubenjohn/naomi_core.git", rev = "latest" }
```

## Project Structure

```
naomi_core/
├── assistant/       # Agent and conversation management
│   ├── agent.py     # Core Agent implementation
│   └── persistence.py  # Persistence layer for conversations
├── tools/           # Integration tools for external services
│   ├── calendar/    # Google Calendar integration
├── db.py            # Database connection and session management
```

## Database Schema

### Currently Implemented
NAOMI Core uses a shared database that currently includes:
- **Conversations**: Stores messages, context, and conversation history

### Planned Database Components
- **Responsibilities**: Will store user-defined and system-suggested responsibilities
- **Events & Triggers**: Will capture real-world and digital events that influence NAOMI's actions
- **User Preferences**: Will maintain user settings and personalization data
- **Knowledge Graph**: Will store relationships between entities for contextual understanding

## Available Tools

### Currently Implemented
NAOMI Core includes the following integration tools:

- **Google Calendar Tool**: Integration with Google Calendar API to fetch events, list calendars, and manage calendar data

### Planned Tools
- **Email Integration**: Connect with email providers for message processing and sending
- **Task Management**: Integration with task tracking systems
- **Weather Services**: Access to weather forecasts and alerts
- **Knowledge Base**: Structured information storage and retrieval

For more details on available tools, see the [Tools README](naomi_core/tools/README.md).

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