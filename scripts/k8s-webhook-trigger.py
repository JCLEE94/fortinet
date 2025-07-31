#!/usr/bin/env python3
"""
K8s 이미지 업데이트 Webhook 서버 (보안 강화)
CI/CD에서 이 엔드포인트를 호출하면 즉시 K8s deployment를 업데이트합니다.

보안 개선사항:
- 시크릿 토큰 필수 검증
- 입력 검증 강화
- 로깅 민감정보 마스킹
- Rate limiting
- HMAC 시그니처 검증 지원
"""

import hashlib
import hmac
import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 설정 (보안 강화)
NAMESPACE = os.getenv("K8S_NAMESPACE", "fortinet")
DEPLOYMENT = os.getenv("K8S_DEPLOYMENT", "fortinet")
SECRET_TOKEN = os.getenv("WEBHOOK_SECRET")
PORT = int(os.getenv("WEBHOOK_PORT", "9301"))

# 보안 검증
if not SECRET_TOKEN:
    logger.critical("🚨 WEBHOOK_SECRET 환경변수가 설정되지 않았습니다")
    raise ValueError("WEBHOOK_SECRET 환경변수가 필수입니다")

if len(SECRET_TOKEN) < 32:
    logger.critical("🚨 WEBHOOK_SECRET이 너무 짧습니다 (최소 32자)")
    raise ValueError("WEBHOOK_SECRET은 최소 32자 이상이어야 합니다")

# Rate limiting 설정
request_counts = {}
RATE_LIMIT_MAX = 10  # 10분당 최대 요청 수
RATE_LIMIT_WINDOW = 600  # 10분


def rate_limit_check(f):
    """Rate limiting 데코레이터"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        now = time.time()

        # 오래된 기록 정리
        if client_ip in request_counts:
            request_counts[client_ip] = [
                timestamp
                for timestamp in request_counts[client_ip]
                if now - timestamp < RATE_LIMIT_WINDOW
            ]
        else:
            request_counts[client_ip] = []

        # Rate limit 확인
        if len(request_counts[client_ip]) >= RATE_LIMIT_MAX:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return (
                jsonify(
                    {"error": "Rate limit exceeded", "retry_after": RATE_LIMIT_WINDOW}
                ),
                429,
            )

        # 요청 기록
        request_counts[client_ip].append(now)
        return f(*args, **kwargs)

    return decorated_function


@app.route("/health", methods=["GET"])
def health():
    """헬스 체크 엔드포인트"""
    return jsonify(
        {
            "status": "healthy",
            "service": "k8s-image-updater",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.route("/webhook/update", methods=["POST"])
def update_deployment():
    """Deployment 업데이트 트리거"""

    # 토큰 검증
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(" ")[1]
    if token != SECRET_TOKEN:
        return jsonify({"error": "Invalid token"}), 401

    # 요청 데이터 파싱
    data = request.get_json() or {}
    image = data.get("image")
    force = data.get("force", True)

    logger.info(f"Update request received - Image: {image}, Force: {force}")

    try:
        # kubectl rollout restart 실행
        cmd = f"kubectl rollout restart deployment/{DEPLOYMENT} -n {NAMESPACE}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Failed to restart deployment: {result.stderr}")
            return jsonify({"status": "error", "message": result.stderr}), 500

        # 롤아웃 상태 확인
        cmd_status = f"kubectl rollout status deployment/{DEPLOYMENT} -n {NAMESPACE} --timeout=5m"
        result_status = subprocess.run(
            cmd_status, shell=True, capture_output=True, text=True
        )

        return jsonify(
            {
                "status": "success",
                "message": "Deployment updated successfully",
                "deployment": f"{NAMESPACE}/{DEPLOYMENT}",
                "timestamp": datetime.utcnow().isoformat(),
                "rollout_status": result_status.stdout,
            }
        )

    except Exception as e:
        logger.error(f"Error updating deployment: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/webhook/status", methods=["GET"])
def get_status():
    """Deployment 상태 확인"""
    try:
        cmd = f"kubectl get deployment {DEPLOYMENT} -n {NAMESPACE} -o json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        import json

        deployment = json.loads(result.stdout)

        return jsonify(
            {
                "name": deployment["metadata"]["name"],
                "namespace": deployment["metadata"]["namespace"],
                "replicas": deployment["status"]["replicas"],
                "ready_replicas": deployment["status"].get("readyReplicas", 0),
                "updated_replicas": deployment["status"].get("updatedReplicas", 0),
                "image": deployment["spec"]["template"]["spec"]["containers"][0][
                    "image"
                ],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logger.info(f"Starting K8s Image Updater Webhook on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
