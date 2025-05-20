"""MkDocs Macros Plugin Configuration."""

import importlib.util
import os
import sys
from types import ModuleType

from dotenv import load_dotenv

from mkdocs_macros.plugin import MacrosPlugin

# Get the absolute path to the project root directory
project_root = os.path.abspath(os.path.dirname(__file__))

# Add the project root to the Python path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load env from the custom path
load_dotenv(dotenv_path="src/config/deploy.env")


def get_version() -> str:
    """Load and return version."""
    spec = importlib.util.spec_from_file_location("version", "src/version.py")
    version_module = importlib.util.module_from_spec(spec)
    sys.modules["version"] = version_module
    spec.loader.exec_module(version_module)
    return getattr(version_module, "__version__", "v0.0.0")


def get_constants() -> ModuleType:
    """Import constants from src/config/constants.py."""
    spec = importlib.util.spec_from_file_location(
        "constants", "src/config/constants.py"
    )
    constants = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(constants)
    return constants


def define_env(env: MacrosPlugin) -> None:
    """Configure environment variables for MkDocs macros."""
    project_name = os.getenv("PROJECT_NAME", "DefaultProject")
    pretty_project_name = project_name.replace("-", " ").title()
    env.variables["PROJECT_NAME"] = project_name
    env.variables["PRETTY_PROJECT_NAME"] = pretty_project_name

    hf_username = os.getenv("HF_USERNAME", "default_hf_user")
    env.variables["HF_USERNAME"] = hf_username

    docker_username = os.getenv("DOCKER_USERNAME", "default_docker_user")
    env.variables["DOCKER_USERNAME"] = docker_username

    # Add version from src/version.py
    env.variables["VERSION"] = get_version()

    constants = get_constants()
    env.variables["MAX_CAT"] = getattr(constants, "MAX_CATEGORY_SELECTION")
    env.variables["MEM_EXP_DAYS"] = getattr(constants, "MEMORY_EXPIRATION_DAYS")
    env.variables["MAX_DEMO_RUNS"] = getattr(constants, "MAX_DEMO_RUNS_PER_DAY")
    env.variables["DEAL_THRESHOLD"] = getattr(constants, "DEAL_THRESHOLD")

    # Add a function to include snippets with macro processing
    @env.macro
    def snippet(filename: str) -> str:
        """Include content from a snippet file with macro processing."""
        try:
            base_path = "docs/"
            with open(os.path.join(base_path, filename), "r", encoding="utf-8") as f:
                content = f.read()

            # Process any macros in the content
            # This is the key part - we use the env.render method to process macros
            processed_content = env.render(content)
            return processed_content
        except Exception as e:
            return f"Error loading snippet '{filename}': {str(e)}"
