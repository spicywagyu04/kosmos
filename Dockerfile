# Kosmo - Cosmology Research Agent
# Dockerfile for containerized deployment

# Use Python 3.11 slim image for smaller footprint
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies for matplotlib and scientific computing
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY examples/ examples/

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash kosmo
USER kosmo

# Create output directory for plots with correct permissions
RUN mkdir -p /home/kosmo/output
ENV KOSMO_OUTPUT_DIR=/home/kosmo/output

# Default command runs the CLI in interactive mode
ENTRYPOINT ["kosmo"]
CMD ["--help"]

# Labels for container metadata
LABEL org.opencontainers.image.title="Kosmo - Cosmology Research Agent" \
      org.opencontainers.image.description="An autonomous AI system for universe exploration" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/your-username/kosmo"
