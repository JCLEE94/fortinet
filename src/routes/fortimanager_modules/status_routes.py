"""
FortiManager Status and Connection Routes
"""

import json
from flask import Blueprint, jsonify

from utils.api_utils import get_api_manager
from utils.unified_cache_manager import cached
from utils.unified_logger import get_logger

logger = get_logger(__name__)

status_bp = Blueprint("fortimanager_status", __name__)


@status_bp.route("/status", methods=["GET"])
@cached(ttl=30)  # Reduced TTL for more frequent updates
def get_fortimanager_status():
    """FortiManager 연결 상태 및 통계 조회"""
    try:
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()

        if not fm_client:
            return jsonify(
                {
                    "success": False,
                    "message": "FortiManager not configured",
                    "data": {"status": "not_configured", "mode": "production"},
                }
            )

        try:
            # Test token authentication first
            if fm_client.test_token_auth():
                status = "limited"  # Token auth but may have limited permissions

                # Try to get additional data
                try:
                    adom_list = fm_client.get_adom_list()
                    adom_count = len(adom_list) if adom_list else 0

                    devices = fm_client.get_managed_devices()
                    device_count = len(devices) if devices else 0

                    status_data = {
                        "status": "connected",
                        "mode": "production",
                        "connection": "established",
                        "api_version": getattr(fm_client, "api_version", "unknown"),
                        "statistics": {
                            "adom_count": adom_count,
                            "device_count": device_count,
                        },
                        "capabilities": ["basic_monitoring", "policy_management"],
                    }

                    if fm_client.test_comprehensive_access():
                        status = "full"
                        status_data["status"] = "fully_connected"
                        status_data["capabilities"].extend(
                            [
                                "advanced_analytics",
                                "compliance_checking", 
                                "security_fabric",
                                "packet_capture",
                            ]
                        )

                    return jsonify({"success": True, "data": status_data})

                except Exception as e:
                    logger.warning(f"Limited FortiManager access: {e}")
                    return jsonify(
                        {
                            "success": True,
                            "data": {
                                "status": "limited_access",
                                "mode": "production",
                                "connection": "established",
                                "message": "Connected but with limited permissions",
                            },
                        }
                    )

            else:
                return jsonify(
                    {
                        "success": False,
                        "message": "Authentication failed",
                        "data": {"status": "auth_failed", "mode": "production"},
                    }
                )

        except Exception as connection_error:
            logger.error(f"FortiManager connection error: {connection_error}")
            return jsonify(
                {
                    "success": False,
                    "message": f"Connection failed: {str(connection_error)}",
                    "data": {"status": "connection_failed", "mode": "production"},
                }
            )

    except Exception as e:
        logger.error(f"FortiManager status check failed: {e}")
        return jsonify(
            {
                "success": False,
                "message": f"Status check failed: {str(e)}",
                "data": {"status": "error", "mode": "production"},
            }
        )


@status_bp.route("/address-objects", methods=["GET"])
@cached(ttl=300)  # 5 minutes cache for relatively static data
def get_address_objects():
    """FortiManager 주소 객체 목록 조회"""
    try:
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        addresses = fm_client.get_firewall_addresses()
        return jsonify({"success": True, "data": addresses})

    except Exception as e:
        logger.error(f"Failed to get address objects: {e}")
        return jsonify({"success": False, "message": str(e)})


@status_bp.route("/service-objects", methods=["GET"])  
@cached(ttl=300)  # 5 minutes cache for relatively static data
def get_service_objects():
    """FortiManager 서비스 객체 목록 조회"""
    try:
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        services = fm_client.get_firewall_services()
        return jsonify({"success": True, "data": services})

    except Exception as e:
        logger.error(f"Failed to get service objects: {e}")
        return jsonify({"success": False, "message": str(e)})