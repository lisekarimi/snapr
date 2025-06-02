# 🚀 Local Development Guide

This guide walks you through setting up {{ PROJECT_NAME_DISPLAY }} for local development, from initial prerequisites to running the application locally.

---

## 📋 Prerequisites

### 🔧 System Requirements
- **Python 3.11**
- **Docker** - for containerized deployments
- **[uv package manager](https://docs.astral.sh/uv/getting-started/installation/)** - for dependency management
- **Make** - for build automation
  - Windows: `winget install GnuWin32.Make`
  - macOS: `brew install make`
  - Linux: `sudo apt install make`

### ☁️ Required Accounts
You'll need accounts for these services:
- **[Modal](https://modal.com/)** - serverless app runtime (includes $5 free credits)
- **[Hugging Face](https://huggingface.co/)** - model deployment
- **[Docker Hub](https://hub.docker.com/)** - container registry

### 💡 Recommended Tools
- **VS Code** or any Python-friendly IDE
- **Google Colab** for GPU-based notebooks (or your own GPU)

---

## 🛠️ Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/lisekarimi/snapr.git
cd snapr
```

Ensure your default branch is `main`. This is required for pre-commit and CI/CD tools expecting a `main` branch.

Rename `.env.example` to `.env` and populate it with the required secrets.

### 2. Modal Setup

Modal is required for running the app. Here's how to get started:

1. Sign up at [modal.com](https://modal.com/) (includes $5 free credits)
2. Add these secrets in your Modal dashboard:
   - `OPENAI_API_KEY`
   - `HF_TOKEN` (with **write permissions**)
3. Generate a Modal token:
   - Go to Settings → Profile → Tokens
   - Click "New Token"
   - Run the setup command:

```bash
modal token set --token-id <YOUR_MODAL_TOKEN_ID> --token-secret <YOUR_MODAL_TOKEN_SECRET>
```

Add both token values to your `.env` file.

> **New to Modal?** Check out this [friendly intro guide](https://github.com/{{ HF_USERNAME }}/lexo/blob/main/notebooks/10_part2_modal.ipynb) to learn more.

### 3. Install Dependencies

```bash
# Main dependencies required to run the core app and Modal agents
uv sync

# Docs dependencies (for MkDocs)
uv sync --group docs

# Notebook dependencies (for running notebooks)
uv sync --group notebook

# Install everything, including all groups
uv sync --all-groups
```

Activate your virtual environment:
```bash
# Unix/macOS
source .venv/bin/activate

# Windows
.\.venv\Scripts\activate
```

---

## 🚀 Running the Application

### 🖥️ Local Development
Start your development environment with these commands:

```bash
# Start Modal services
make run-modal

# Launch the main application
make run-local

# Run UI with hot reload (for frontend development)
make ui

# Serve documentation locally
make docs-serve
```

### 🐳 Docker Development
For a containerized environment:

```bash
make docker-build
make docker-run
```

---

## 🛡️ Development Workflow

### 🪝 Pre-commit Hooks
Set up automated code quality checks that run before each commit:

```bash
make install-hooks
```

These hooks ensure your code passes:
- **Code Quality** - `ruff` formatting and linting
- **Commit Standards** - proper commit message format with 50-character limit
- **Security** - `gitleaks` prevents accidental secret commits
- **CI Safety** - checks if remote branch is ahead to avoid merge conflicts

> **Pro tip**: This catches issues early and prevents failed CI checks later.

### 📝 Essential Commands
Run `make help` to see all available commands. Here are the most commonly used:

```bash
make help              # Show all available commands
make run-local         # Start local development server
make run-modal         # Start Modal services
make ui                # Start UI with hot reload
make docs-serve        # Serve documentation
make install-hooks     # Set up pre-commit hooks
make docker-build      # Build Docker image
make docker-run        # Run Docker container
```

---

## ⚙️ Configuration

### ⚙️ Project Constants
Modify application settings in `csrc/config/constants.py`. This file centralizes all project constants including environment settings (`ENV`, `PROD`, `DEV`).

### 💤 Modal App Scaling
The Modal app is configured for cost-effective demo usage:

- **Scale-down window**: 180 seconds (3 minutes after last request)
- **Minimum containers**: 0 (no always-on containers)

This results in cold starts but saves credits. To modify this behavior, edit `src/modal_services/app_config.py`.

For active development, you can set `min_containers=1` to keep one container running, but remember to stop it manually afterward to avoid unnecessary credit usage.

### ⛓️ Dependency Management
This project uses **uv** for fast dependency management. Dependencies are managed through the `Makefile` commands, which automatically update both `pyproject.toml` and the lockfile.

Learn more at [uv documentation](https://docs.astral.sh/uv/).

---

## ❓ Need Help?

- **Modal questions**: Check the [intro guide](https://github.com/{{ HF_USERNAME }}/lexo/blob/main/notebooks/10_part2_modal.ipynb)
- **Available commands**: Run `make help`
- **Dependencies**: See [uv documentation](https://docs.astral.sh/uv/)

Ready to start building? Run the Quick Start steps above and you'll be up and running in minutes!