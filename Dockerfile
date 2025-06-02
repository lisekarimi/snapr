FROM python:3.11-slim

# Install uv
RUN pip install uv

WORKDIR /app

# Copy dependency files first (changes rarely)
COPY pyproject.toml uv.lock ./

# Put venv outside of /app so it won't be affected by volume mounts
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

# Install dependencies (this will now create venv at /opt/venv)
RUN uv sync --locked --no-group docs --no-group notebook

# Create a non-root user
RUN useradd -m appuser

# Copy all source code
COPY . .

# Set ownership of writable dirs
RUN mkdir -p /app/memory && chown -R appuser:appuser /app/memory

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command - use uv run to execute with the virtual environment
CMD ["bash", "-c", "set -e && uv run modal deploy -m src.modal_services.entry && uv run main.py"]
# CMD ["uv", "run", "main.py"]