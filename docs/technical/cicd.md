# 🔁 CI/CD Workflow

- All deployments, code quality checks (`ruff`, `black`), unit tests, **security checks**, and `requirements.lock` validation are automated via GitHub Actions on every PR and push.

- See [/.github/workflows](https://github.com/{{ HF_USERNAME }}/{{ PROJECT_NAME }}/tree/main/.github/workflows) for full pipeline details.

The diagram below illustrates the full workflow — from local development (pre-commit hooks) to production deployment via CI/CD.

![](../styles/assets/cicd.png)
*Click on image to zoom*

---

## ✅ CI/CD Prerequisites

### 🔐 Add Required Secrets

Before pushing to remote repo, go to the Github Repo:

**Settings → Secrets and variables → Actions → New repository secret**

Add the following:

- `OPENAI_API_KEY`
- `DOCKER_TOKEN`
- `HF_TOKEN`
- `HF_USERNAME`
- `GIT_USER_NAME`
- `GIT_USER_EMAIL`: *Use your GitHub-provided private email:* 

      - Go to [/settings/profile](https://github.com/settings/profile) → Emails**, enable **“Keep my email address private”**,  
      - then copy the `@users.noreply.github.com` address shown there.

!!!note
       Define `HF_USERNAME` in GitHub Actions secrets even if it's already in deploy.env, because GitHub may treat it as sensitive data and mask it, leading to hard-to-debug issues. Using secrets ensures consistent and reliable acces.

---

### ⚙️ Configure Workflow Permissions

Ensure GitHub Actions has the correct permissions:

Go to Github Repo:  
   **Settings → Actions → General → Under Workflow permissions**:

   - ✅ Select: `Read and write permissions`
   - ✅ Check: `Allow GitHub Actions to create and approve pull requests`
