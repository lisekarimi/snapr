# =======================
# 🔧 Configuration
# =======================
include src/config/deploy.env

DOCKER_IMAGE = $(DOCKER_USERNAME)/$(PROJECT_NAME)
VERSION := $(shell python -c "exec(open('src/version.py').read()); print(__version__)")
TAG = $(VERSION)
CONTAINER_NAME = $(PROJECT_NAME)-container
ENV_FILE = .env

# Get current directory path in the correct format for each OS
# Windows: Uses PowerShell for Windows-style paths
# Unix/Mac: Uses pwd for Unix-style paths
ifeq ($(OS),Windows_NT)
	CURDIR := $(shell powershell -Command "Convert-Path .")
else
	CURDIR := $(shell pwd)
endif

# =======================
# 📦 Local Conda Env
# =======================

## Create environment from dev_env.yml

install-env:
ifeq ($(OS),Windows_NT)
	@conda env list | findstr $(PROJECT_NAME) >nul || conda env create -n $(PROJECT_NAME) -f dev_env.yml
else
	@conda env list | grep $(PROJECT_NAME) >/dev/null || conda env create -n $(PROJECT_NAME) -f dev_env.yml
endif

## Update conda environment from dev_env.yml
update-env:
	@conda env update -n $(PROJECT_NAME) --file dev_env.yml --prune

# Example env usage:
# make install-env   # to create it
# make update-env    # to update it

# =======================
# 🔒 Lock file
# =======================

## Generate/update requirements lock file
## Creates a complete requirements.txt
lock:
	uv pip compile requirements.txt -o requirements.lock
	python -c "import re; \
	content = open('requirements.txt', 'r').read(); \
	orig_mark = '# Original requirements:'; \
	deps_mark = '# All dependencies'; \
	has_deps = deps_mark in content; \
	has_orig = orig_mark in content; \
	orig = content.split(deps_mark)[0].rstrip() if has_deps else content; \
	orig = orig if has_orig else orig_mark + '\n' + orig; \
	deps = [l for l in open('requirements.lock', 'r') if re.match(r'^[a-zA-Z0-9\._-]+==', l)]; \
	deps = [re.sub(r';.*$$$$', '', d) for d in deps]; \
	deps = sorted(set(deps)); \
	new_content = orig + '\n\n' + deps_mark + ' (including transitive):\n' + ''.join(deps); \
	open('requirements.txt', 'w').write(new_content)"
	@echo "Requirements file updated with all dependencies."

# =======================
# 🪝 Hooks
# =======================

## 🪝 Install pre-commit hooks
install-hooks:
	pre-commit install
	pre-commit install --hook-type commit-msg

# =======================
# 🐳 Docker Commands
# =======================

## 🛠️ Build the Docker image
docker-build:
	docker build -t $(DOCKER_IMAGE):$(TAG) .

## Run development container with local code mounted - no image rebuild needed when code changes
# To see changes: 1) Edit code locally 2) Ctrl+C to stop container 3) Run 'make docker-dev' again
docker-run:
	docker run -it --rm --name $(CONTAINER_NAME) \
	  -e TERM=xterm --env-file $(ENV_FILE) \
	  -v $(CURDIR):/app \
	  -w /app \
	  -p 7860:7860 \
	  --user root \
	  $(DOCKER_IMAGE):$(TAG)

## 💅 Only for UI iteration
ui:
	watchfiles 'python app.py'

# Example docker usage:
# make docker-build  # builds the Docker image
# make docker-dev    # runs with local code (dev mode)

# =======================
# 🧪 Testing Commands
# =======================

## Run all tests using pytest
test:
	python -m pytest tests/

# Example test usage:
# make test                                     # run all tests
# python -m pytest tests/test_ft_price_agent.py # run one test file
# python -m pytest -k test_function_name        # run specific test function

# =======================
# ✨ Code Quality Tools
# =======================

## 🧪 Run linting checks
lint:
	@echo "Checking code with ruff..."
	ruff check --exclude=notebooks/,*.ipynb --config pyproject.toml .

## 🎨 Auto-format code
format:
	@echo "Formatting code with black..."
	black --exclude="/(notebooks)/|\.ipynb$" .

## ✅ Run both lint + format check (CI-safe)
check:
	@echo "Running full code quality check..."
	ruff check --exclude=notebooks/,*.ipynb .
	black --check --exclude="/(notebooks)/|\.ipynb$" .

## 🛠️ Run first to auto-fix simple issues, then use 'lint' to catch what's left
fix:
	@echo "Auto-fixing all fixable issues..."
	ruff check --exclude=notebooks/,*.ipynb --fix .

## 🔍 Manually run ruff linter with detailed output (useful for debugging)
precommit:
	pre-commit run ruff --verbose

# =======================
# 📁 Docs With mkdocs
# =======================

docs-serve:
	mkdocs serve

docs-build:
	mkdocs build

docs-clean:
	rm -rf site

docs-deploy:
	mkdocs gh-deploy


# =======================
# # 🔍 Security Scanning
# =======================

# Security scanning with Gitleaks
# Requires Chocolatey and Gitleaks, both installed via PowerShell running as Administrator
# - Install Chocolatey: https://chocolatey.org/install
# - Install Gitleaks: choco install gitleaks

check-secrets:
	gitleaks detect --source . --verbose

audit:
	pip-audit -r requirements.txt

# =======================
# # PHONY Targets
# =======================

.PHONY: \
	install-env update-env update-lock \
	install-hooks \
	docker-build docker-dev ui-dev \
	test lint format check fix precommit \
	docs-serve docs-build docs-clean docs-deploy \
	check-secrets