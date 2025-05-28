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

## 🧾 Pre-Deployment

- Manually run the GitHub Action `changelog-prep.yml` to generate the changelog (input: new version).
- A changelog is generated using LLM in a `changelog` branch.
- Review and edit as needed, then **squash and merge** into `main`.  
  ⚠️ The **merge commit must contain** `changelog for`, e.g., `changelog for 1.2.3`.

This commit **automatically triggers**:

- 🧹 Deletion of the `changelog` branch  
- 📄 Copying the changelog to `docs/changelog.md`

---

## 🚀 Ready to Deploy

🔔 Now all is set for **production deployment and release**.

For full details and a visual overview, see the CI/CD schema in [`/cicd.md`](cicd.md).

Deploy each component individually for better control and easier debugging:

1. **GitHub Release** - Creates version tag and release with changelog
2. **Docker Hub** - Builds and pushes Docker image with version and `latest` tags  
3. **Hugging Face** - Deploys minimal code/files for Docker-based deployment
4. **MkDocs** - Updates documentation on GitHub Pages

Each deployment is triggered manually by typing **`deploy`** as input.

- It first checks if `ENV="PROD"` is set in `src/config/constants.py`
    - If the check fails, it raises an error and stops the deployment
    - If the check passes, it proceeds with the deployment process

**Benefits:**
- 🎯 **Targeted deployment** - deploy only what you need
- 🐛 **Easier debugging** - focused logs per service
- 🔄 **Independent rollbacks** - fix issues in specific services
- ⚡ **Faster iteration** - test individual components






