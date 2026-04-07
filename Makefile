# Makefile for managing the tools project

# Variables
VENV_NAME = .venv
PYTHON_FILES = src
EXTRACT_IMAGE = afcourrier
EXTRACT_TEST_IMAGE = afcourrier-test

ifeq ($(OS),Windows_NT)
    VENV_PYTHON := $(VENV_NAME)/Scripts/python.exe
else
    VENV_PYTHON := $(VENV_NAME)/bin/python
endif

# Detect the operating system
ifeq ($(OS),Windows_NT)
    OS_NAME := Windows
else
    OS_NAME := $(shell uname -s)
endif

# install uv
install_uv:
ifeq ($(OS_NAME),Linux)
	@echo Detected Linux OS
	curl -LsSf https://astral.sh/uv/install.sh | sh
else ifeq ($(OS_NAME),Darwin)
	@echo Detected macOS
	curl -LsSf https://astral.sh/uv/install.sh | sh
else ifeq ($(OS_NAME),Windows)
	@echo Detected Windows OS
	powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
	# If you are on Windows and this doesn't work, check your permissions or run the command manually.
endif

# Create a virtual environment
venv:
	uv venv $(VENV_NAME)
	@echo Virtual $(VENV_NAME) environment created.
	@echo To activate the virtual environment, please run: source $(VENV_NAME)/bin/activate


# Install dependencies using uv
# only for python <= 3.12:
# uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
install:
ifeq ($(OS_NAME),Windows)
	uv pip install --python $(VENV_PYTHON) pip --upgrade --link-mode=copy
	uv pip install --python $(VENV_PYTHON) -e ".[dev]" --link-mode=copy
else
	@if [ ! -x "$(VENV_PYTHON)" ]; then \
		echo "❌ Virtual environment not found at $(VENV_PYTHON). Run 'make venv' first."; \
		exit 1; \
	fi
	uv pip install --python $(VENV_PYTHON) pip --upgrade
	uv pip install --python $(VENV_PYTHON) -e ".[dev]"
endif
	@echo Dependencies and project installed in editable mode.
	@echo To activate the virtual environment, please run: source $(VENV_NAME)/bin/activate or the corresponding command for your operating system.

activate:
	@echo "  Run the appropriate command in YOUR shell:"
	@echo ""
ifeq ($(OS_NAME),Windows)
	@echo "  PowerShell:  ./$(VENV_NAME)/Scripts/Activate.ps1"
	@echo "  cmd.exe:     ./$(VENV_NAME)\Scripts\activate.bat"
	@echo "  Git Bash:    source ./$(VENV_NAME)/Scripts/activate"
else
	@echo "  source $(VENV_NAME)/bin/activate"
endif
	@echo ""

# Pre-commit hooks
pre_commit:
	pre-commit install
	@echo Pre-commit hooks installed.

.PHONY: pre-commit-run
pre-commit-run:
	pre-commit run --all-files
	@echo Pre-commit hooks executed.

.PHONY: pre-commit-run-staged
pre-commit-run-staged:
	pre-commit run --hook-stage manual
	@echo Pre-commit hooks executed on staged files.

# Clean up
clean:
ifeq ($(OS_NAME),Windows)
	del /s /q $(VENV_NAME)
	rmdir /s /q $(VENV_NAME)
else
	rm -rf $(VENV_NAME)
endif
	@echo Cleaned up the environment.

# Allow passing extra words after target without make complaining
%:
	@:

# Tests
test:
ifeq ($(OS_NAME),Windows)
	uv run --link-mode=copy pytest
else
	uv run pytest
endif
	@echo Tests executed.

# Linting and formatting
.PHONY: format
format:
	pre-commit run black --all-files
	pre-commit run isort --all-files
	@echo Formatting completed.


.PHONY: flake8
flake8:
	pre-commit run flake8 --all-files
	@echo Flake8 check completed.

.PHONY: bandit
bandit:
	pre-commit run bandit --all-files
	@echo Bandit security check completed.

.PHONY: mypy
mypy:  ## Run mypy type checker
	pre-commit run mypy --all-files
	@echo MyPy type checking completed.

.PHONY: pyupgrade
pyupgrade:
	pre-commit run pyupgrade --all-files
	@echo Python code upgraded to Python 3.12+ syntax.


# add mypy if wanted
.PHONY: lint
lint: format flake8 bandit mypy pyupgrade
	@echo All linting checks completed.

.PHONY: check-all
check-all: check-format lint test
	@echo All checks and tests completed.


# Help
help:
	@echo Makefile for tools
	@echo Usage:
	@echo   make install_uv                 - Install uv cross-platform
	@echo   make venv                       - Create a virtual environment
	@echo   make install                    - Install dependencies using uv
	@echo   make activate                   - Activate the virtual environment
	@echo   make pre_commit                 - Install pre-commit hooks
	@echo   make pre-commit-run             - Run all pre-commit hooks on all files
	@echo   make pre-commit-run-staged      - Run pre-commit hooks on staged files
	@echo   make pyupgrade                  - Upgrade Python syntax to 3.12+
	@echo   make format                     - Format code with black and isort
	@echo   make flake8                     - Run flake8 linting
	@echo   make bandit                     - Run bandit security checks
	@echo   make mypy                       - Run mypy type checking
	@echo   make lint                       - Run all linting tools
	@echo   make check-all                  - Run all checks and tests
	@echo   make clean                      - Clean up the environment
	@echo   make help                       - Display this help message