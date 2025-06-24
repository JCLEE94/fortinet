# FortiGate Nextrade - CLAUDE.md v8.7.0 Compliant Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/ssl/certs

# Copy requirements first for better caching
COPY requirements.txt requirements_minimal.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Create non-root user for security
RUN groupadd -r fortinet && useradd -r -g fortinet fortinet
RUN chown -R fortinet:fortinet /app
USER fortinet

# Environment variables with dynamic port support
ARG PORT=7777
ENV PORT=$PORT
ENV PYTHONPATH=/app
ENV FLASK_APP=src.main
ENV FLASK_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/api/health', timeout=5).read()" || exit 1

# Expose port dynamically
EXPOSE $PORT

# Start command
CMD ["python3", "src/main.py", "--web"]