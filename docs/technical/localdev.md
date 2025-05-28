# ⚙️ Local Development
This page provides a complete guide for setting up {{ PROJECT_NAME_DISPLAY }} locally, including environment setup, development tools, pre-commit hooks, and key Makefile commands.

---

## 📋 Prerequisites

### 🔧 System Requirements
- Python 3.11
- Docker
- VS Code or any IDE that supports Python
- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)
- Make: `winget install GnuWin32.Make` (Windows) | `brew install make` (macOS) | `sudo apt install make` (Linux)
- Google Colab (for GPU-based notebooks), or use your own GPU if available.

### ☁️ Accounts & Services
- [Hugging Face](https://huggingface.co/) (for deployment)
- [Docker Hub](https://hub.docker.com/)
- [Modal](https://modal.com/) (required for app runtime)

### 🧠 Useful Skills
- Modal & Serverless deployment
- LLM APIs (OpenAI, Hugging Face Transformers)
- Traditional ML workflows (scikit-learn, XGBoost, etc.)
- Git, GitHub, pre-commit workflows
- CI/CD with GitHub Actions

### 🪝 Git Setup

- Ensure your default branch is `main`.

      ```bash
      git config --global init.defaultBranch main
      ```

This is required for pre-commit and CI/CD tools expecting a `main` branch.

---

## 🛠️ Local Setup

Local setup is useful for development and testing.

- **Clone the repository:**
```bash
git clone https://github.com/lisekarimi/snapr.git
cd snapr
```
- **Configure `.env`**:

Rename `.env.example` to `.env` and populate it with the required secrets.

- **Modal Setup Required:**

    - Sign up at [modal.com](https://modal.com/) (includes $5 free credits).
    - Add `OPENAI_API_KEY` and `HF_TOKEN` (with **write permissions**) as secrets in your Modal account.
    - Go to Settings → Profile → Tokens, then click "New Token" to generate one.
```bash
modal token set --token-id <YOUR_MODAL_TOKEN_ID> --token-secret <YOUR_MODAL_TOKEN_SECRET>
```
Add both values to your `.env` file.


!!! Note 
    If you're curious and want to learn more about Modal, check out this quick and friendly intro [here](https://github.com/{{ HF_USERNAME }}/lexo/blob/main/notebooks/10_part2_modal.ipynb).

---

## 🚀 Run the App


### 🖥️ Local Dev Setup

1. **Create a virtual environment (venv)**

    There are three ways to install dependencies:

    - `uv sync` — installs the **main dependencies** required to run the core app and Modal agents.
    - `uv sync --group docs` — installs the **docs dependencies** (for MkDocs).
    - `uv sync --group notebook` — installs the **notebook dependencies** (for running notebooks).

    To install **everything**, including all groups: `uv sync --all-groups`

2. Activate venv: `source .venv/bin/activate` (Unix) or `.\.venv\Scripts\activate` (Win).

3. **Run the app locally:**

    - Start Modal:  
    ```bash
    make run-modal
    ```
    - Launch the app:  
    ```bash
    make run-local
    ```

    - Run the **UI with hot reload**:  
    ```bash
    make ui
    ```

    - Run the **docs**:  
    ```bash
    make docs-serve
    ```

### 🐳 With Docker
```bash
make docker-build
make docker-run
```

---

## 🛡️ Pre-Commit

- Pre-commit hooks catch code style, commit message, and security issues early—saving you from failed CI checks later.
- Hooks ensure all code passes:

    - **Code Quality:** `ruff`
    - **Commit Standards:** `commitizen`, custom 50-character limit check
    - **Security:** `gitleaks` to prevent committing secrets
    - **CI Safety:** checks if the remote branch is ahead—forces a `git pull --rebase` to avoid merge conflicts

!!! tip
    This workflow enforces clean code and a smooth CI/CD process before anything hits GitHub.

- To install the hooks, run:
```bash
make install-hooks
```

---

## 📝 Key Make Commands

This project uses a `Makefile` to streamline development and deployment.

Run `make help` to see all available commands with their descriptions.

---

## ⛓️ Dependency Management

We use **uv** for fast, simple dependency management.

Dependencies are added or removed using commands (see `Makefile`), which automatically update both `pyproject.toml` and the lockfile.

For more details, visit: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

---

## ⚙️ Configuration Constants

To change constants like `ENV` (e.g., to `PROD` or `DEV`), edit `csrc/config/constants.py`—this file centralizes all constants used in the project.


---

## 💤 Modal App Scaling

Note that the **Modal app is configured to sleep after inactivity**:

- `scaledown_window=180` — containers shut down 3 minutes after the last request. This results in a **cold start** on the next call, but **saves credits**, which suits our demo needs.
- `min_containers=0` — no container stays "always-on".

    If set to `1`, it keeps one container running (faster, but consumes more credits). Use this only during active development or testing, and **remember to stop the app manually** afterward to avoid waste.

The configuration used offers the best balance for this project.

🔧 To modify this behavior, go to: `src/modal_services/app_config.py`

📚 For more details, refer to [this guide](https://github.com/{{ HF_USERNAME }}/lexo/blob/main/notebooks/10_part2_modal.ipynb).

