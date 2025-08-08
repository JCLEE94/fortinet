"""
FortiManager Device Management Routes
"""

import time
from flask import Blueprint, jsonify, request

from utils.api_utils import get_api_manager
from utils.unified_cache_manager import cached
from utils.unified_logger import get_logger

logger = get_logger(__name__)

device_bp = Blueprint("fortimanager_device", __name__)


@device_bp.route("/dashboard", methods=["GET"])
@cached(ttl=60)  # 1 minute cache for dashboard data
def get_dashboard():
    """FortiManager 대시보드 정보 조회"""
    try:
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()

        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        # Get dashboard data
        dashboard_data = {
            "devices": fm_client.get_managed_devices() or [],
            "adoms": fm_client.get_adom_list() or [],
            "system_info": fm_client.get_system_status() or {},
        }

        return jsonify({"success": True, "data": dashboard_data})

    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        return jsonify({"success": False, "message": str(e)})


@device_bp.route("/devices", methods=["GET"])
@cached(ttl=120)  # 2 minutes cache for device list
def get_devices():
    """FortiManager 관리 장치 목록 조회"""
    try:
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()

        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        devices = fm_client.get_managed_devices()
        return jsonify({"success": True, "data": devices or []})

    except Exception as e:
        logger.error(f"Failed to get devices: {e}")
        return jsonify({"success": False, "message": str(e)})


@device_bp.route("/device/<device_id>", methods=["GET"])
@cached(ttl=300)  # 5 minutes cache for individual device info
def get_device_details(device_id):
    """특정 장치의 상세 정보 조회"""
    try:
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()

        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        device_info = fm_client.get_device_details(device_id)
        if not device_info:
            return jsonify({"success": False, "message": "Device not found"})

        return jsonify({"success": True, "data": device_info})

    except Exception as e:
        logger.error(f"Failed to get device details for {device_id}: {e}")
        return jsonify({"success": False, "message": str(e)})


@device_bp.route("/device/<device_id>/interfaces", methods=["GET"])
@cached(ttl=600)  # 10 minutes cache for interface data
def get_device_interfaces(device_id):
    """특정 장치의 인터페이스 정보 조회"""
    try:
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()

        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        interfaces = fm_client.get_device_interfaces(device_id)
        return jsonify({"success": True, "data": interfaces or []})

    except Exception as e:
        logger.error(f"Failed to get interfaces for device {device_id}: {e}")
        return jsonify({"success": False, "message": str(e)})


@device_bp.route("/topology", methods=["GET"])
@cached(ttl=1800)  # 30 minutes cache for topology data
def get_network_topology():
    """네트워크 토폴로지 정보 조회"""
    try:
        # Get parameters
        include_details = request.args.get("include_details", "false").lower() == "true"
        device_filter = request.args.get("device_filter", "").strip()

        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()

        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        # Basic topology structure
        topology = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "generated_at": time.time(),
                "include_details": include_details,
                "device_filter": device_filter,
            },
        }

        # Get devices
        devices = fm_client.get_managed_devices() or []

        # Filter devices if specified
        if device_filter:
            devices = [d for d in devices if device_filter.lower() in d.get("name", "").lower()]

        # Process devices into topology nodes
        for device in devices:
            device_id = device.get("name", device.get("device_id", "unknown"))
            
            node = {
                "id": device_id,
                "name": device.get("name", device_id),
                "type": device.get("type", "firewall"),
                "status": device.get("status", "unknown"),
                "ip": device.get("ip", "unknown"),
            }

            if include_details:
                # Add detailed information
                try:
                    details = fm_client.get_device_details(device_id)
                    if details:
                        node["details"] = {
                            "version": details.get("version", "unknown"),
                            "model": details.get("model", "unknown"),
                            "serial": details.get("serial", "unknown"),
                            "interfaces": details.get("interfaces", []),
                        }
                except Exception as e:
                    logger.warning(f"Failed to get details for device {device_id}: {e}")
                    node["details"] = {"error": str(e)}

            topology["nodes"].append(node)

        # Create basic connections based on device relationships
        # This is simplified - in a real implementation, you'd analyze routing tables, 
        # interface connections, etc.
        for i, device in enumerate(topology["nodes"]):
            # Connect devices in sequence as example
            if i < len(topology["nodes"]) - 1:
                edge = {
                    "source": device["id"],
                    "target": topology["nodes"][i + 1]["id"],
                    "type": "network",
                    "status": "active",
                }
                topology["edges"].append(edge)

        return jsonify({"success": True, "data": topology})

    except Exception as e:
        logger.error(f"Failed to get network topology: {e}")
        return jsonify({"success": False, "message": str(e)})