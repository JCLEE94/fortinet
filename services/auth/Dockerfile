FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY services/auth/ ./auth/
COPY src/core/auth_manager.py ./shared/
COPY src/utils/unified_logger.py ./shared/
COPY src/utils/security.py ./shared/

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV SERVICE_NAME=auth-service
ENV SERVICE_PORT=8081

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# 서비스 시작
CMD ["python", "auth/main.py"]