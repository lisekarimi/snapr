# 🚀 Deployment Guide

This project is deployed remotely to **Hugging Face Spaces** (Gradio UI, Docker) and **Modal** (backend) via **Continuous Delivery**.
Local deployment is optional and intended for development or testing only.

We use **Continuous Delivery** (not Continuous Deployment) because:

- Deployments require **manual confirmation** (`confirm_deployment=deploy`)
- A **human triggers** the release, not every commit
- There are **approval gates** before pushing to production

---

## 📋 Deployment Prerequisites

Before triggering production deployment, ensure the following are set up:

### 📝 Configuration

- ✅ GitHub secrets are configured in your repository.

    Refer to the [CI/CD page](cicd.md) for more details on prerequisites and setup.

- The **version** is set in `pyproject.toml` and committed to GitHub.
- `ENV=PROD` is set in the `src/config/constants` file and committed.
- `CHANGELOG.md` is up to date and copied to the docs folder


### 🧱 Infrastructure

- ✅ **Modal is set up**
    - `OPENAI_API_KEY` and `HF_TOKEN` (write access) are added as secrets
    - Your account has enough credits to run and deploy the app

- ✅ **Docker Hub repository** is created
    - The repo name must **match** the `PROJECT_NAME` defined in `pyproject.toml`

- ✅ **Hugging Face Space** is created:
    - Type: **Docker**
    - The **Space name must match** the `PROJECT_NAME` defined in `pyproject.toml`
    - Secrets are added: `OPENAI_API_KEY`, `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET`

!!! warning "Do not edit the first part of the README"
    ```
    ---
    title:
    emoji:
    colorFrom:
    colorTo:
    sdk:
    pinned:
    ---
    ```
    This is required for Hugging Face deployment.


### 📁 GitHub Pages Setup

Github Pages is required for MkDocs docs deployment.

- ✅ Make sure your repository is **public**
- ✅ Configure GitHub Pages:

  Go to your **GitHub Repo → Settings → Pages**:

  - Under **Source**, select: **"Deploy from a branch"**
  - In the **Branch** dropdown:
    - First, select: `main / (root)` and  **Save**
    - After the first successful deploy, switch to: `gh-pages / (root)` and **Save**

This enables GitHub Pages to serve your MkDocs documentation from the correct branch.

---

## 🚀 Ready to Deploy

🔔 Now all is set for **production deployment and release**.

For full details and a visual overview, see the CI/CD schema in [`/cicd.md`](cicd.md).

Each deployment is triggered manually by typing **`deploy`** as input.

- It first checks if `ENV="PROD"` is set in `src/config/constants.py`
    - If the check fails, it raises an error and stops the deployment
    - If the check passes, it proceeds with the deployment process

!!!note
    **Exception:** MkDocs deployment skips the environment check as it's not necessary for documentation

**Benefits:**

- 🎯 **Targeted deployment** - deploy only what you need
- 🐛 **Easier debugging** - focused logs per service
- 🔄 **Independent rollbacks** - fix issues in specific services
- ⚡ **Faster iteration** - test individual components

**Deployment Steps:**

1. **Deploy to Hugging Face** – This action deploys minimal code and configuration for Docker-based deployment

    → *Manual step*: Perform sanity check - verify logs and UI functionality; fix issues and redeploy as needed.

2. **Deploy to Docker Hub** – This action builds and publishes Docker images with `version` and `latest` tags

3. **Update Documentation (MkDocs)** – This action publishes updated documentation to GitHub Pages

    → *Manual step*: Sanity check page layout and navigation links.

4. **Create GitHub Release** – This action creates a version tag and publishes the release.
