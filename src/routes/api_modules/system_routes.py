"""
System-related API routes
"""

from flask import current_app
from utils.common_imports import Blueprint, jsonify, os, time

from config.unified_settings import unified_settings
from utils.unified_cache_manager import cached
from utils.unified_logger import get_logger

from .utils import (format_uptime, get_cpu_usage, get_memory_usage,
                    get_system_uptime, optimized_response)

logger = get_logger(__name__)

system_bp = Blueprint("api_system", __name__)


@system_bp.route("/health", methods=["GET"])
@cached(ttl=10)  # Short cache for health checks
def health_check():
    """System health check endpoint"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "version": getattr(current_app, "version", "1.0.0"),
            "uptime": format_uptime(get_system_uptime()),
            "environment": getattr(unified_settings, "APP_MODE", "production"),
        }

        # Add additional health metrics
        try:
            memory = get_memory_usage()
            cpu_usage = get_cpu_usage()

            health_status["metrics"] = {
                "memory_usage_percent": memory["usage_percent"],
                "cpu_usage_percent": cpu_usage,
                "disk_usage_percent": 45.2,  # Placeholder
            }
        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            health_status["metrics"] = {"error": "metrics unavailable"}

        return jsonify(health_status)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return (
            jsonify({"status": "unhealthy", "timestamp": time.time(), "error": str(e)}),
            500,
        )


@system_bp.route("/system/stats", methods=["GET"])
@cached(ttl=60)  # 1 minute cache for system stats
@optimized_response(cache_key="system_stats", ttl=60)
def get_system_stats():
    """시스템 통계 정보 조회"""
    try:
        # Get system information
        uptime = get_system_uptime()
        memory = get_memory_usage()
        cpu_usage = get_cpu_usage()

        stats = {
            "system": {
                "uptime": format_uptime(uptime),
                "uptime_seconds": uptime,
                "load_average": [0.5, 0.7, 0.8],  # Placeholder
                "boot_time": time.time() - uptime,
            },
            "resources": {
                "cpu": {
                    "usage_percent": cpu_usage,
                    "cores": os.cpu_count() or 4,
                    "architecture": "x86_64",  # Placeholder
                },
                "memory": {
                    "total_bytes": memory["total"],
                    "used_bytes": memory["used"],
                    "available_bytes": memory["available"],
                    "usage_percent": memory["usage_percent"],
                },
                "disk": {
                    "total_gb": 100,  # Placeholder
                    "used_gb": 45,
                    "available_gb": 55,
                    "usage_percent": 45.0,
                },
            },
            "network": {
                "connections": {
                    "established": 25,
                    "listening": 12,
                    "time_wait": 8,
                },
                "interfaces": [
                    {"name": "eth0", "status": "up", "ip": "192.168.1.100"},
                    {"name": "lo", "status": "up", "ip": "127.0.0.1"},
                ],
            },
            "services": {
                "web_server": {"status": "running", "port": 7777},
                "cache": {"status": "running", "type": "redis"},
                "database": {"status": "running", "type": "json_files"},
            },
            "application": {
                "version": getattr(current_app, "version", "1.0.0"),
                "mode": unified_settings.get("app_mode", "production"),
                "debug": current_app.debug,
                "workers": 1,
            },
            "timestamp": time.time(),
        }

        return jsonify({"success": True, "data": stats})

    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        return jsonify({"success": False, "message": str(e)})


@system_bp.route("/topology/data", methods=["GET"])
@cached(ttl=300)  # 5 minute cache for topology data
def get_topology_data():
    """네트워크 토폴로지 데이터 조회"""
    try:
        from .utils import generate_topology_data

        topology = generate_topology_data()

        return jsonify({"success": True, "data": topology})

    except Exception as e:
        logger.error(f"Failed to get topology data: {e}")
        return jsonify({"success": False, "message": str(e)})


@system_bp.route("/generate_token", methods=["POST"])
def generate_access_token():
    """API 액세스 토큰 생성"""
    try:
        import hashlib
        import secrets

        # Generate a random token
        token = secrets.token_urlsafe(32)

        # Create a hash for storage (in a real implementation, store this securely)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        response_data = {
            "token": token,
            "expires_in": 3600,  # 1 hour
            "token_type": "Bearer",
            "created_at": time.time(),
        }

        logger.info("API token generated successfully")
        return jsonify({"success": True, "data": response_data})

    except Exception as e:
        logger.error(f"Failed to generate token: {e}")
        return jsonify({"success": False, "message": str(e)})
