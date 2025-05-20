{{ snippet("_version.md") }}

# ⚙️ Local Development
This page provides a complete guide for setting up {{ PRETTY_PROJECT_NAME }} locally, including environment setup, development tools, pre-commit hooks, and key Makefile commands.

---

## 📋 Prerequisites

### 🔧 System Requirements
- Python 3.8+
- Docker
- Conda (or Miniconda)
- VS Code (recommended)
- Google Colab (for notebooks requiring GPU)

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

    - For all future repos:

      ```bash
      git config --global init.defaultBranch main
      ```

    - For existing repos (if currently on `master`):

      ```bash
      git branch -m master main
      git fetch origin
      git branch -u origin/main main
      git remote set-head origin -a
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
- **Install dependencies:**

    Create environment with Conda:
    ```bash
    make install-env
    conda activate snapr
    ```

- **Set up development tools:**
    ```bash
    make install-hooks
    ```
    This installs pre-commit hooks.

- **Set environment variables.**

    - Copy `.env.example` to `.env` 
    - Add your tokens - all required tokens are listed in the file.

- **Modal Setup Required.**

    - Sign up at [modal.com](https://modal.com/) (includes $5 free credits).
    - - Add `OPENAI_API_KEY` and `HF_TOKEN` (with **write permissions**) as secrets in your Modal account.
    - Authenticate your environment:
      ```bash
      modal setup
      ```
    !!! Note 
        See the Modal guide for a quick intro [here](https://github.com/{{ HF_USERNAME }}/lexo/blob/main/notebooks/10_part2_modal.ipynb).

- **Update `src/config/deploy.env`.**
      ```py
      ENV=DEV   # unlimited runs locally
      HF_USERNAME=<your-huggingface-username> # for prod deployment
      DOCKER_USERNAME=<your-docker-username>  # image and container
      ```
- **Start the app locally:**

    - **With Docker:** (Highly Recommended)
        ```bash
        make docker-build
        make docker-run
        ```

    - **Without Docker:**
        ```bash
        modal deploy -m src.modal_services.entry
        python app.py
        ```
---

## 📝 Key Make Commands

This project uses a Makefile for practical, streamlined development and deployment. All commands are defined in `Makefile`.

Here is an exmpale:

| Command              | Description                          |
|----------------------|--------------------------------------|                   
| `make docker-build`  | Build Docker image                   |
| `make docker-run`    | Run container locally                |

---

## 🛡️ Pre-Commit

- Pre-commit hooks catch code style, dependency and security issues early, so you don’t waste time on failed GitHub Actions checks.
- Hooks ensure all code passes 
    - Code Quality: ruff, black
    - Commit Standards: commitizen, custom 50-char check
    - Dependencies: lock file sync check at pre-push
    - Security: gitleaks to catch secrets before pushing
    - CI Safety: remote branch diff check to avoid overwriting

!!! tip
    This workflow enforces clean code and reproducible builds before CI/CD even runs.

---

## 🧼 Dependency Management

- Keeps prod environment lean while dev remains flexible:
    - **`requirements.txt`** contains only runtime dependencies required to run or deploy the app (e.g., in Docker or on Hugging Face).
    - **`dev_env.yml`** holds local-only development tools such as `matplotlib` (for EDA), `black`, `ruff`, `pre-commit`, and `mkdocs`

