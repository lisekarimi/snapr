"""Defines shared Modal configuration.

Includes constants, image, volume, secrets, and app setup.
"""

from modal import App, Image, Secret, Volume

from src.config.constants import APP_NAME

CACHE_PATH = "/cache"
GPU = "T4"

# Modal image, volume, and secrets
image = (
    Image.debian_slim()
    .pip_install(
        "huggingface",
        "torch",
        "transformers",
        "bitsandbytes",
        "accelerate",
        "peft",
        "sentence-transformers",
        "xgboost",
        "joblib",
        "chromadb",
        "openai",
        "numpy",
        "pandas",
    )
    .env({"HF_HUB_CACHE": CACHE_PATH})
    .add_local_file(local_path="pyproject.toml", remote_path="/root/pyproject.toml")
)

# Modal setup
app = App(APP_NAME, image=image)

cache_vol = Volume.from_name("hf-hub-cache", create_if_missing=True)
secrets = [Secret.from_name("HF_TOKEN"), Secret.from_name("OPENAI_API_KEY")]

# Shared Modal class config for all model agents
modal_class_kwargs = dict(
    image=image,
    secrets=secrets,
    volumes={CACHE_PATH: cache_vol},  # Mount volume into /cache
    gpu=GPU,
    timeout=1800,  # 30-minute max runtime
    min_containers=0,  # 1 = always-on, uses credits
    scaledown_window=180,  # Shuts down the container
)
