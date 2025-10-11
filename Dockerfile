FROM python:3.11-slim

# Install uv only (no nginx needed!)
RUN pip install uv

WORKDIR /app

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Put venv outside of /app so it won't be affected by volume mounts
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

# Install ALL dependencies including docs group (exclude only notebook)
RUN uv sync --locked --all-groups --no-group notebook

# Add venv to PATH so executables are available
ENV PATH="/opt/venv/bin:$PATH"

# Copy all application code
COPY . .

# Create necessary directories and non-root user
RUN mkdir -p /app/memory \
    && useradd -m appuser \
    && chown -R appuser:appuser /app /opt/venv

# Switch to non-root user
USER appuser

# Expose port 8080
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/')" || exit 1

# Run the application directly
CMD ["python", "main.py"]
