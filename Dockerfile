# =============================================================================
# FortiGate Nextrade - 표준 Dockerfile
# Production-ready single container deployment
# =============================================================================

FROM python:3.11-slim as base

# Build arguments for GitOps metadata
ARG BUILD_DATE
ARG BUILD_TIMESTAMP
ARG GIT_COMMIT
ARG GIT_SHA
ARG GIT_BRANCH
ARG VERSION
ARG IMMUTABLE_TAG
ARG REGISTRY_URL="registry.jclee.me"

# Environment setup
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src \
    APP_MODE=${APP_MODE:-production} \
    WEB_APP_HOST=${WEB_APP_HOST:-0.0.0.0} \
    WEB_APP_PORT=${WEB_APP_PORT:-7777} \
    # GitOps metadata
    GIT_COMMIT=${GIT_COMMIT} \
    GIT_SHA=${GIT_SHA} \
    GIT_BRANCH=${GIT_BRANCH} \
    BUILD_DATE=${BUILD_DATE} \
    BUILD_TIMESTAMP=${BUILD_TIMESTAMP} \
    VERSION=${VERSION} \
    IMMUTABLE_TAG=${IMMUTABLE_TAG} \
    REGISTRY_URL=${REGISTRY_URL}

# Labels for metadata
LABEL maintainer="FortiGate Nextrade Team" \
      version="${VERSION}" \
      description="FortiGate Nextrade - Network Monitoring Platform" \
      gitops.principle.immutable="true" \
      gitops.principle.declarative="dockerfile-as-code" \
      gitops.principle.git-source="https://github.com/JCLEE94/fortinet" \
      gitops.principle.pull-based="argocd-managed" \
      build-date="${BUILD_DATE}" \
      build-timestamp="${BUILD_TIMESTAMP}" \
      git-commit="${GIT_COMMIT}" \
      git-sha="${GIT_SHA}" \
      git-branch="${GIT_BRANCH}" \
      immutable-tag="${IMMUTABLE_TAG}" \
      registry="${REGISTRY_URL}" \
      registry.namespace="fortinet" \
      security.scanned="true" \
      security.non-root-user="fortinet" \
      performance.python-optimized="true" \
      performance.gunicorn-ready="true" \
      performance.multi-stage-build="true"

# =============================================================================
# System Dependencies
# =============================================================================
FROM base as system-deps

# Install system dependencies
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends --fix-missing \
    build-essential \
    gcc \
    g++ \
    curl \
    wget \
    netcat-openbsd \
    iputils-ping \
    procps \
    htop \
    ca-certificates \
    && apt-get autoremove -y \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/* \
    && rm -rf /var/cache/apt/archives/*

# =============================================================================
# Python Dependencies
# =============================================================================
FROM system-deps as python-deps

# Create app user for security
RUN groupadd -r fortinet && useradd -r -g fortinet -s /bin/bash fortinet

# Create application directories
RUN mkdir -p /app/src \
    /app/data \
    /app/logs \
    /app/temp \
    && chown -R fortinet:fortinet /app

# Copy requirements first for better caching
COPY requirements.txt /app/
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
    gunicorn \
    gevent \
    prometheus-client

# =============================================================================
# Application Stage
# =============================================================================
FROM python-deps as app

# Copy application code
COPY --chown=fortinet:fortinet . /app/

# Compile Python bytecode for performance
RUN python -m compileall /app/src/ -b -qq || true

# Set proper permissions
RUN chmod +x /app/src/main.py && \
    chmod -R 755 /app/src && \
    chmod -R 777 /app/data /app/logs /app/temp

# =============================================================================
# Production Configuration
# =============================================================================

# Health check with GitOps validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD python3 -c "\
import urllib.request, json, os; \
response = urllib.request.urlopen('http://localhost:${WEB_APP_PORT}/api/health', timeout=10); \
data = json.loads(response.read().decode()); \
build_info = data.get('build_info', {}); \
expected_tag = os.environ.get('IMMUTABLE_TAG', 'unknown'); \
actual_tag = build_info.get('immutable_tag', 'unknown'); \
assert expected_tag == actual_tag, f'Tag mismatch: {expected_tag} != {actual_tag}'; \
print(f'Health check passed - Immutable tag: {actual_tag}');" || exit 1

# Performance and resource settings
ENV PYTHONOPTIMIZE=2 \
    MALLOC_ARENA_MAX=2 \
    PYTHONMALLOC=malloc \
    FLASK_ENV=production \
    FLASK_DEBUG=false \
    WEB_CONCURRENCY=4 \
    WORKERS=4 \
    WORKER_CLASS=gevent \
    WORKER_CONNECTIONS=1000 \
    MAX_REQUESTS=1000 \
    MAX_REQUESTS_JITTER=100 \
    TIMEOUT=120 \
    KEEPALIVE=5

# Copy startup script
COPY --chown=fortinet:fortinet start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Record GitOps build information
RUN echo "=== GitOps Immutable Build Information ===" > /app/build-info.txt && \
    echo "Build Date: ${BUILD_DATE:-unknown}" >> /app/build-info.txt && \
    echo "Build Timestamp: ${BUILD_TIMESTAMP:-unknown}" >> /app/build-info.txt && \
    echo "Git Commit: ${GIT_COMMIT:-unknown}" >> /app/build-info.txt && \
    echo "Git SHA (Short): ${GIT_SHA:-unknown}" >> /app/build-info.txt && \
    echo "Git Branch: ${GIT_BRANCH:-unknown}" >> /app/build-info.txt && \
    echo "Version: ${VERSION:-unknown}" >> /app/build-info.txt && \
    echo "Immutable Tag: ${IMMUTABLE_TAG:-unknown}" >> /app/build-info.txt && \
    echo "Registry: ${REGISTRY_URL:-registry.jclee.me}/fortinet:${IMMUTABLE_TAG:-unknown}" >> /app/build-info.txt && \
    echo "GitOps Principles: Declarative, Git Source, Pull-based, Immutable" >> /app/build-info.txt && \
    echo "Security: Non-root user (fortinet:fortinet)" >> /app/build-info.txt && \
    echo "Optimization: Python bytecode compiled, Gunicorn ready" >> /app/build-info.txt && \
    printf '{\n' > /app/build-info.json && \
    printf '  "gitops": {\n' >> /app/build-info.json && \
    printf '    "principles": ["declarative", "git-source", "pull-based", "immutable"],\n' >> /app/build-info.json && \
    printf '    "managed_by": "argocd",\n' >> /app/build-info.json && \
    printf '    "immutable": true\n' >> /app/build-info.json && \
    printf '  },\n' >> /app/build-info.json && \
    printf '  "build": {\n' >> /app/build-info.json && \
    printf '    "date": "%s",\n' "${BUILD_DATE:-unknown}" >> /app/build-info.json && \
    printf '    "timestamp": "%s",\n' "${BUILD_TIMESTAMP:-unknown}" >> /app/build-info.json && \
    printf '    "version": "%s",\n' "${VERSION:-unknown}" >> /app/build-info.json && \
    printf '    "immutable_tag": "%s"\n' "${IMMUTABLE_TAG:-unknown}" >> /app/build-info.json && \
    printf '  },\n' >> /app/build-info.json && \
    printf '  "git": {\n' >> /app/build-info.json && \
    printf '    "commit": "%s",\n' "${GIT_COMMIT:-unknown}" >> /app/build-info.json && \
    printf '    "sha": "%s",\n' "${GIT_SHA:-unknown}" >> /app/build-info.json && \
    printf '    "branch": "%s",\n' "${GIT_BRANCH:-unknown}" >> /app/build-info.json && \
    printf '    "repository": "https://github.com/JCLEE94/fortinet"\n' >> /app/build-info.json && \
    printf '  },\n' >> /app/build-info.json && \
    printf '  "registry": {\n' >> /app/build-info.json && \
    printf '    "url": "%s",\n' "${REGISTRY_URL:-registry.jclee.me}" >> /app/build-info.json && \
    printf '    "namespace": "fortinet",\n' >> /app/build-info.json && \
    printf '    "full_image": "%s/fortinet:%s"\n' "${REGISTRY_URL:-registry.jclee.me}" "${IMMUTABLE_TAG:-unknown}" >> /app/build-info.json && \
    printf '  }\n' >> /app/build-info.json && \
    printf '}\n' >> /app/build-info.json

# =============================================================================
# Runtime Configuration
# =============================================================================

# Switch to non-root user for security
USER fortinet

# Working directory
WORKDIR /app

# Expose port
EXPOSE ${WEB_APP_PORT}

# Volume mounts for data persistence
VOLUME ["/app/data", "/app/logs"]

# Default command
CMD ["/app/start.sh"]
