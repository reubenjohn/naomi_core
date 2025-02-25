# python_template

[![codecov](https://codecov.io/gh/reubenjohn/python_template/branch/main/graph/badge.svg?token=python_template_token_here)](https://codecov.io/gh/reubenjohn/python_template/branch/main)
[![CI](https://github.com/reubenjohn/python_template/actions/workflows/main.yml/badge.svg)](https://github.com/reubenjohn/python_template/actions/workflows/main.yml)

A template project to help you get started with a new Python project. This template is designed to be modular, simple, and easy to maintain, with a focus on flexibility and low dependency.

## Introduction

**python_template** is a project template for creating new Python projects. It provides a well-structured project layout, essential configurations, and utilities to streamline the development process. Whether you're building a library, application, or framework, this template offers a solid foundation to start from.

### **Key Features**
1. **Modular Structure**: A clean and modular project structure that is easy to navigate and extend.
2. **Low Dependency**: Minimal dependencies to keep the project lightweight and easy to manage.
3. **Flexibility**: Easily customizable to fit various project requirements.
4. **Development Utilities**: Includes a Makefile with common development tasks and a pyproject.toml for managing dependencies with Poetry.

## Project Structure

```text
├── Containerfile            # The file to build a container using buildah or docker
├── CONTRIBUTING.md          # Onboarding instructions for new contributors
├── docs                     # Documentation site (add more .md files here)
│   └── index.md             # The index page for the docs site
├── .github                  # Github metadata for repository
│   ├── release_message.sh   # A script to generate a release message
│   └── workflows            # The CI pipeline for Github Actions
├── .gitignore               # A list of files to ignore when pushing to Github
├── HISTORY.md               # Auto generated list of changes to the project
├── LICENSE                  # The license for the project
├── Makefile                 # A collection of utilities to manage the project
├── MANIFEST.in              # A list of files to include in a package
├── mkdocs.yml               # Configuration for documentation site
├── python_template          # The main python package for the project
│   ├── base.py              # The base module for the project
│   ├── __init__.py          # This tells Python that this is a package
│   ├── __main__.py          # The entry point for the project
│   └── VERSION              # The version for the project is kept in a static file
├── README.md                # The main readme for the project
├── setup.py                 # The setup.py file for installing and packaging the project
├── requirements.txt         # An empty file to hold the requirements for the project
├── requirements-test.txt    # List of requirements for testing and development
└── tests                    # Unit tests for the project (add more test files here)
    ├── conftest.py          # Configuration, hooks and fixtures for pytest
    ├── __init__.py          # This tells Python that this is a test package
    └── test_base.py         # The base test case for the project
```

## Setup

To set up the project for development, run:

    ```bash
    make install
    ```

For detailed development setup, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## Usage

To run the main entry point of the project:

```bash
$ poetry run python_template
```
(See CONTRIBUTING.md for more usage details.)

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for all development guidelines (setup, contributions, etc).

## Makefile

The Makefile includes several useful targets for managing the project:

```bash
❯ make
Usage: make <target>

Targets:
help:             ## Show the help.
install:          ## Install the project in dev mode.
fmt:              ## Format code using black & isort.
lint:             ## Run pep8, black, mypy linters.
test: lint        ## Run tests and generate coverage report.
watch:            ## Run tests on every change.
clean:            ## Clean unused files.
virtualenv:       ## Create a virtual environment.
release:          ## Create a new tag for release.
docs:             ## Build the documentation.
```
(Refer to CONTRIBUTING.md for extended usage.)

## Acknowledgements

This template is inspired by best practices and experiences from maintaining various Python projects.
