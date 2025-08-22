# =============================================================================
# FortiGate Nextrade - Production Dockerfile
# Multi-service support with environment-based configuration
# =============================================================================

FROM python:3.11-slim as base

# Build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG COMMIT_SHA
ARG SERVICE_TYPE=fortinet

# Environment setup
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src \
    SERVICE_TYPE=${SERVICE_TYPE} \
    APP_MODE=production \
    WEB_APP_HOST=0.0.0.0 \
    WEB_APP_PORT=7777

# Labels
LABEL maintainer="FortiGate Nextrade Team" \
      version="${VERSION}" \
      description="FortiGate Nextrade ${SERVICE_TYPE} Service" \
      build-date="${BUILD_DATE}"

# =============================================================================
# System Dependencies
# =============================================================================
FROM base as system-deps

RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Python Dependencies
# =============================================================================
FROM system-deps as python-deps

RUN groupadd -r fortinet && \
    useradd -r -g fortinet -m -s /bin/bash fortinet

RUN mkdir -p /app/src /app/data /app/logs && \
    chown -R fortinet:fortinet /app

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn gevent

# =============================================================================
# Application Stage
# =============================================================================
FROM python-deps as app

COPY --chown=fortinet:fortinet . /app/

# Unified startup script for all services
RUN cat > /app/start.sh << 'EOF'
#!/bin/bash
set -e

SERVICE_TYPE=${SERVICE_TYPE:-fortinet}
echo "Starting $SERVICE_TYPE service..."

case "$SERVICE_TYPE" in
    fortinet)
        # Main FortiGate application
        echo "FortiGate Nextrade Main Service"
        echo "Port: $WEB_APP_PORT"
        
        # Wait for dependencies
        if [ ! -z "$REDIS_HOST" ]; then
            echo "Waiting for Redis..."
            timeout 30 sh -c 'until nc -z $REDIS_HOST ${REDIS_PORT:-6379}; do sleep 1; done'
        fi
        
        if [ ! -z "$POSTGRES_HOST" ]; then
            echo "Waiting for PostgreSQL..."
            timeout 30 sh -c 'until nc -z $POSTGRES_HOST ${POSTGRES_PORT:-5432}; do sleep 1; done'
        fi
        
        cd /app/src
        exec gunicorn \
            --bind $WEB_APP_HOST:$WEB_APP_PORT \
            --workers ${WORKERS:-4} \
            --worker-class gevent \
            --timeout 120 \
            --access-logfile - \
            --error-logfile - \
            "web_app:create_app()"
        ;;
        
    redis)
        # Redis cache service
        echo "Redis Cache Service"
        exec redis-server \
            --bind 0.0.0.0 \
            --port ${REDIS_PORT:-6379} \
            --maxmemory ${REDIS_MAXMEMORY:-256mb} \
            --maxmemory-policy ${REDIS_POLICY:-allkeys-lru} \
            --appendonly ${REDIS_AOF:-yes} \
            --dir /data
        ;;
        
    postgresql)
        # PostgreSQL database service
        echo "PostgreSQL Database Service"
        
        # Initialize if needed
        if [ ! -s "$PGDATA/PG_VERSION" ]; then
            echo "Initializing PostgreSQL..."
            initdb -D $PGDATA \
                --username=${POSTGRES_USER:-fortinet} \
                --pwfile=<(echo ${POSTGRES_PASSWORD:-fortinet123})
        fi
        
        exec postgres \
            -D $PGDATA \
            -p ${POSTGRES_PORT:-5432}
        ;;
        
    *)
        echo "Unknown service type: $SERVICE_TYPE"
        exit 1
        ;;
esac
EOF

RUN chmod +x /app/start.sh

# Install service-specific dependencies
RUN if [ "$SERVICE_TYPE" = "redis" ]; then \
        apt-get update && \
        apt-get install -y redis-server && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*; \
    elif [ "$SERVICE_TYPE" = "postgresql" ]; then \
        apt-get update && \
        apt-get install -y postgresql-client postgresql && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*; \
    fi

# Compile Python bytecode
RUN python -m compileall /app/src -b -qq || true

# Set permissions
RUN chown -R fortinet:fortinet /app && \
    chmod -R 755 /app/src && \
    chmod 777 /app/data /app/logs

# =============================================================================
# Runtime Configuration
# =============================================================================

# Dynamic health check based on service type
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD if [ "$SERVICE_TYPE" = "fortinet" ]; then \
            curl -f http://localhost:${WEB_APP_PORT}/api/health || exit 1; \
        elif [ "$SERVICE_TYPE" = "redis" ]; then \
            redis-cli ping || exit 1; \
        elif [ "$SERVICE_TYPE" = "postgresql" ]; then \
            pg_isready -U ${POSTGRES_USER:-fortinet} || exit 1; \
        fi

USER fortinet
WORKDIR /app

# Dynamic port exposure
EXPOSE 7777 6379 5432

# Volume for data persistence
VOLUME ["/app/data", "/data"]

CMD ["/app/start.sh"]