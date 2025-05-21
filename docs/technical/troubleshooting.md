# ⚠️ Troubleshooting Guide

This page outlines common issues you may encounter when working with the {{ PRETTY_PROJECT_NAME }} project, and how to resolve them efficiently.

---

## 1. ⚡ Modal App Not Running

**Symptoms:**

- Errors like `ft loaded failed` or `[ERROR] Remote RAGPricer failed`
- Agents not responding or failing silently

**Fix:**

- Make sure the Modal app is running.

    - It should start automatically with `make docker-run`. You’ll see output similar to:

        ```
        ✓ Created objects.
        ├── 🔨 Created mount PythonPackage:src
        ├── 🔨 Created function RAGPricer.*.
        ├── 🔨 Created function XGBPricer.*.
        ├── 🔨 Created function EnsemblePricer.*.
        └── 🔨 Created function FTPricer.*.
        ✓ App deployed in 2.806s! 🎉
        ```

- If you manually deleted the app in Modal:

    - Set the correct environment in `deploy.env`:
        ```py
        env=dev  # or env=prod
        ```
    - Then run make `make docker-run` to redeploy.

- Check the logs in Modal for errors.

---

## 2. 🔗 Dependency Conflicts

**Symptoms:**

- Errors during CI/CD runs (e.g., GitHub Actions) or local pre-push hooks
- Conflicting versions between `requirements.txt` and `requirements.lock`

**Fix:**

* After any change to `requirements.txt`, always run:

  ```sh
  make lock
  ```

  This updates both `requirements.lock` and syncs versions back to `requirements.txt`.

---

## 3. 🎨 Code Formatting

**Symptoms:**

- Pre-commit hook errors related to PEP8/code formatting (Ruff/Black)

**Fix:**

- For any PEP8 or code formatting failures flagged by pre-commit:

    - First, run `make fix` to auto-fix most issues; 
    - If errors remain, run `make check` to identify what needs manual fixing, 
    - Then re-run `make pre-commit` or try your commit again.

---

## 4. 🔑 API Key Issues

**Symptoms:**

- Agent calls to Modal or OpenAI fail
- Authentication errors in logs

**Fix:**

- Ensure your `.env` file exists and includes valid tokens:

    - `MODAL_TOKEN_ID`
    - `MODAL_TOKEN_SECRET`
    - `OPENAI_API_KEY`

- A sample .env.template is provided with a list of all tokens required for this project.

---

## 5. 🌎 Env Misconfig

**Symptoms:**

- Wrong app being deployed
- Unexpected behavior or resource usage

**Fix:**

- Set the correct environment in `deploy.env`:
    ```py
    env=dev  # or env=prod
    ```
- Then run make `make docker-run` to redeploy.

- For production: Ensure the deployment workflow (CI/CD) sets the environment to `prod` after execution.

---

## 6. 🐳 Docker Cache

**Status:**

- No known issues.

Don’t clear Docker/Modal volumes unless you intend to.
