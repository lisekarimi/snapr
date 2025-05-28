# ⚠️ Troubleshooting Guide

This page outlines common issues you may encounter when working with the {{ PROJECT_NAME_DISPLAY }} project, and how to resolve them efficiently.

---

## ⚡ Modal App Not Running

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

    - Set the correct environment in `src/config/constants.py`:
        ```py
        env=PROD  # or env=DEV
        ```
    - Then run make `make docker-run` to redeploy.

- Check the logs in Modal for errors.

---

## 🎨 Code Formatting

**Symptoms:**

- Pre-commit hook errors related to PEP8/code formatting (Ruff)

**Fix:**

- For any PEP8 or code formatting failures flagged by pre-commit:

    - **Quick fix:** Run `make fix` to auto-fix most issues, then `make lint` to verify
    - **Manual fix:** Address each issue shown in the pre-commit log output

---

## 🔑 API Key Issues

**Symptoms:**

- Agent calls to Modal or OpenAI fail
- Authentication errors in logs

**Fix:**

- Ensure your `.env` file exists and includes valid tokens:

    - `MODAL_TOKEN_ID`
    - `MODAL_TOKEN_SECRET`
    - `OPENAI_API_KEY`

- A sample `env.example` is provided with a list of all tokens required for this project.

---

## 🌎 Env Misconfig

**Symptoms:**

- Wrong app being deployed
- Unexpected behavior or resource usage

**Fix:**

- Set the correct environment in `src/config/constants.py`:
    ```py
    env=DEV  # or env=PROD
    ```
- Then run make `make docker-run` to redeploy.

- For production: Ensure the deployment workflow (CI/CD) sets the environment to `prod` after execution.

---

## 6. 🐳 Docker Cache

**Status:**

- No known issues.

Don’t clear Docker/Modal volumes unless you intend to.
