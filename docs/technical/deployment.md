{{ snippet("_version.md") }}

# 🚀 Deployment Guide

This project is deployed remotely to Hugging Face Spaces (Gradio UI, Docker type) and Modal (backend) via CI/CD. Local deployment is optional, for development or testing only.

---

## 📋 Deployment Prerequisites

Before triggering production deployment, ensure the following are set up:

### 📝 Configuration

- ✅ `src/config/deploy.env` is updated with the correct usernames:
    ```env
    HF_USERNAME=<your-huggingface-username>
    DOCKER_USERNAME=<your-dockerhub-username>
    ```

### 🧱 Infrastructure

- ✅ **Modal is set up**
    - `OPENAI_API_KEY` and `HF_TOKEN` (write access) are added as secrets
    - Your account has enough credits to run and deploy the app

- ✅ **Docker Hub repository** is created  
    - The repo name must **match** the `PROJECT_NAME` defined in `src/config/deploy.env`  

- ✅ **Hugging Face Space** is created:
    - Type: **Docker**
    - The **Space name must match** the `PROJECT_NAME` defined in `src/config/deploy.env`  
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

- Manually run the GitHub Action `changelog-version-prep.yml` to generate the changelog and update `version.py` (input: new version).
- A changelog is generated using LLM in a `changelog` branch.
- Review and edit as needed, then **squash or rebase merge via CLI** into `main`.  
  ⚠️ The **merge commit must contain** `changelog for`, e.g., `changelog for v1.2.3`.

This commit **automatically triggers**:

- 🧹 Deletion of the `changelog` branch  
- 📄 Copying the changelog to `docs/changelog.md`

---

## 🚀 Ready to Deploy

🔔 Now all is set for **production deployment and release**.

For full details and a visual overview, see the CI/CD schema in [`/cicd.md`](../cicd.md).

There are **two deployment modes**, both triggered **manually** via the GitHub Actions UI.

### 🔹 Option 1: `deploy-all`

`deploy-all` triggers deployment to **all targets** in a single step — recommended for first-time full deployment.

This will:

1. Set `ENV=prod` in `deploy.env`
2. Create a version **tag** and GitHub **release** with the changelog in the description
3. Deploy MkDocs documentation to GitHub Pages
4. Deploy to **Hugging Face** (Docker type):
    - Only minimal code/files are pushed
    - Hugging Face builds the Docker image and runs the app on **Modal**
5. Build Docker image and push to Docker Hub with:
    - Version tag (`vX.Y.Z`)
    - `latest` tag

### 🔸 Option 2: Deploy Individual Components

Use this when you need to deploy a specific target only (e.g., just Docker or docs),  
or to retry a failed step from a previous `deploy-all` run.

Each target (Docker, Hugging Face, docs, release ...) has its own manual trigger in the GitHub Actions tab.




