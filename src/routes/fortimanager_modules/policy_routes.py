"""
FortiManager Policy Management Routes
"""

from flask import Blueprint, jsonify, request

from utils.api_utils import get_api_manager
from utils.unified_logger import get_logger

logger = get_logger(__name__)

policy_bp = Blueprint("fortimanager_policy", __name__)


@policy_bp.route("/policies", methods=["GET"])
def get_policies():
    """정책 목록 조회"""
    try:
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        policies = fm_client.get_firewall_policies()
        return jsonify({"success": True, "data": policies or []})

    except Exception as e:
        logger.error(f"Failed to get policies: {e}")
        return jsonify({"success": False, "message": str(e)})


@policy_bp.route("/analyze-packet-path", methods=["POST"])
def analyze_packet_path():
    """패킷 경로 분석"""
    try:
        data = request.get_json() or {}
        
        # Required parameters
        src_ip = data.get("src_ip")
        dst_ip = data.get("dst_ip")
        port = data.get("port")
        protocol = data.get("protocol", "tcp")
        
        if not all([src_ip, dst_ip, port]):
            return jsonify({"success": False, "message": "Missing required parameters"})

        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        result = fm_client.analyze_packet_path(src_ip, dst_ip, port, protocol)
        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"Failed to analyze packet path: {e}")
        return jsonify({"success": False, "message": str(e)})
