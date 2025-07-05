FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    flask==3.0.0 \
    requests==2.31.0 \
    gunicorn==21.2.0

# Copy webhook provider
COPY npm-webhook-provider.py /app/

# Create non-root user
RUN useradd -m -u 1000 webhook && \
    chown -R webhook:webhook /app

USER webhook

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8888/healthz').raise_for_status()"

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8888", "--workers", "2", "--threads", "4", "--timeout", "120", "npm-webhook-provider:app"]