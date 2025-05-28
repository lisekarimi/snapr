"""MkDocs Macros Plugin Configuration."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict

import tomllib
from dotenv import load_dotenv

from mkdocs_macros.plugin import MacrosPlugin

# Load environment variables
load_dotenv()

# Get the absolute path to the project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

# Add the project root to the Python path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def get_constants() -> ModuleType:
    """Import constants from src/config/constants.py."""
    constants_path = PROJECT_ROOT / "src" / "config" / "constants.py"

    if not constants_path.exists():
        raise FileNotFoundError(f"Constants file not found: {constants_path}")

    spec = importlib.util.spec_from_file_location("constants", constants_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load constants from {constants_path}")

    constants = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(constants)
    return constants


def get_project_metadata() -> Dict[str, Any]:
    """Extract project metadata from pyproject.toml."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"

    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found: {pyproject_path}")

    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


def load_environment_variables() -> Dict[str, Any]:
    """Load and validate environment variables."""
    return {
        "HF_USERNAME": "lisekarimi",
        "DOCKER_USERNAME": "lkar",
    }


def load_constants_variables(constants: ModuleType) -> Dict[str, Any]:
    """Extract required constants from the constants module."""
    constant_mappings = {
        "MAX_CAT": "MAX_CATEGORY_SELECTION",
        "MEM_EXP_DAYS": "MEMORY_EXPIRATION_DAYS",
        "MAX_DEMO_RUNS": "MAX_DEMO_RUNS_PER_DAY",
        "DEAL_THRESHOLD": "DEAL_THRESHOLD",
    }

    variables = {}
    for var_name, const_name in constant_mappings.items():
        if not hasattr(constants, const_name):
            raise AttributeError(
                f"Constant '{const_name}' not found in constants module"
            )
        variables[var_name] = getattr(constants, const_name)

    return variables


def define_env(env: MacrosPlugin) -> None:
    """Configure environment variables for MkDocs macros."""
    try:
        # Load project metadata
        project_data = get_project_metadata()
        project_name = project_data.get("project", {}).get("name", "")
        if not project_name:
            raise ValueError("Project name not found in pyproject.toml")
        env.variables["PROJECT_NAME"] = project_name
        env.variables["PROJECT_NAME_DISPLAY"] = project_name.capitalize()

        # Load environment variables
        env_vars = load_environment_variables()
        env.variables.update(env_vars)

        # Load constants
        constants = get_constants()
        const_vars = load_constants_variables(constants)
        env.variables.update(const_vars)

    except Exception as e:
        # Re-raise the exception to fail fast and make issues visible
        raise RuntimeError(f"Failed to configure MkDocs macros: {e}") from e
