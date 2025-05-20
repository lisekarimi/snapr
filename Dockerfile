FROM python:3.12.10-slim

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.lock .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.lock

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

# Default command
CMD ["bash", "-c", "set -e && modal deploy -m src.modal_services.entry && python app.py"]
# CMD ["python", "app.py"]