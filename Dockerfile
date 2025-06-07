# SAM (Small Agent Model) Production Dockerfile
# Sprint 13 Task 3: Deployment Files

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV SAM_CONFIG_DIR=/app/config
ENV SAM_MEMORY_DIR=/app/memory_store
ENV SAM_LOGS_DIR=/app/logs

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/config /app/memory_store /app/logs /app/backups

# Create non-root user
RUN useradd -m -u 1000 sam && \
    chown -R sam:sam /app

# Switch to non-root user
USER sam

# Create default configuration
RUN python -c "from config.config_manager import get_config_manager; get_config_manager()"

# Expose ports
EXPOSE 5001 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Default command
CMD ["python", "start_sam.py"]

# Labels
LABEL maintainer="SAM Development Team"
LABEL version="1.0.0"
LABEL description="SAM - Small Agent Model with Memory Intelligence"
LABEL org.opencontainers.image.source="https://github.com/your-org/sam"
LABEL org.opencontainers.image.documentation="https://github.com/your-org/sam/blob/main/README.md"
