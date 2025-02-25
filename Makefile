.ONESHELL:
ENV_PREFIX="$(shell (poetry env list --full-path | grep Activated || poetry env list --full-path) | head -n 1 | cut -d' ' -f1)/bin/"

.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current environment.
	@poetry env info

.PHONY: install
install:          ## Install the project in dev mode.
	@if ! poetry --version > /dev/null 2>&1; then \
		echo "Poetry is not installed. Installing..."; \
		python -m pip install poetry; \
	else \
		echo "Poetry is already installed."; \
	fi
	@poetry install

.PHONY: fmt
fmt:              ## Format code using black & isort.
	$(ENV_PREFIX)isort python_template/
	$(ENV_PREFIX)black python_template/
	$(ENV_PREFIX)black tests/

.PHONY: lint
lint:             ## Run pep8, black, mypy linters.
	@echo $(ENV_PREFIX)
	$(ENV_PREFIX)flake8 python_template/
	$(ENV_PREFIX)black --check python_template/
	$(ENV_PREFIX)black --check tests/
	$(ENV_PREFIX)mypy --ignore-missing-imports python_template/

.PHONY: test
test: lint        ## Run tests and generate coverage report.
	xvfb-run $(ENV_PREFIX)pytest -v --cov-config .coveragerc --cov=python_template -l --tb=short --maxfail=1 tests/ || tests_failed=1
	$(ENV_PREFIX)coverage xml
	$(ENV_PREFIX)coverage html
	exit $$tests_failed

.PHONY: test-headed # Used on machines with a display that doesn't have xvfb setup
test-headed: lint        ## Run tests and generate coverage report.
	$(ENV_PREFIX)pytest -v --cov-config .coveragerc --cov=python_template -l --tb=short --maxfail=1 tests/
	$(ENV_PREFIX)coverage xml
	$(ENV_PREFIX)coverage html

.PHONY: watch
watch:            ## Run tests on every change.
	ls **/**.py | entr $(ENV_PREFIX)pytest -s -vvv -l --tb=long --maxfail=1 tests/

.PHONY: clean
clean:            ## Clean unused files.
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build
	@rm -rf site/

.PHONY: release
release:          ## Create a new tag for release.
	@echo "WARNING: This operation will create s version tag and push to github"
	@read -p "Version? (provide the next x.y.z semver) : " TAG
	@echo "$${TAG}" > python_template/VERSION
	@$(ENV_PREFIX)gitchangelog > HISTORY.md
	@git add python_template/VERSION HISTORY.md
	@git commit -m "release: version $${TAG} 🚀"
	@echo "creating git tag : $${TAG}"
	@git tag $${TAG}
	@git push -u origin HEAD --tags
	@echo "Github Actions will detect the new tag and release the new version."

.PHONY: docs
docs:             ## Build the documentation.
	@echo "building documentation ..."
	@$(ENV_PREFIX)mkdocs build
	URL="site/index.html"; xdg-open $$URL || sensible-browser $$URL || x-www-browser $$URL || gnome-open $$URL || open $$URL

# This project has been generated from rochacbruno/python-project-template
# __author__ = 'rochacbruno'
# __repo__ = https://github.com/rochacbruno/python-project-template
# __sponsor__ = https://github.com/sponsors/rochacbruno/
