"""
FortiManager Monitoring and Packet Capture Routes
"""

from flask import Blueprint, jsonify, request

from utils.api_utils import get_api_manager
from utils.unified_cache_manager import cached
from utils.unified_logger import get_logger

logger = get_logger(__name__)

monitoring_bp = Blueprint("fortimanager_monitoring", __name__)


@monitoring_bp.route("/monitoring", methods=["GET"])
@cached(ttl=60)
def get_monitoring_data():
    """FortiManager 모니터링 데이터 조회"""
    try:
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()

        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        monitoring_data = {
            "system_status": fm_client.get_system_status() or {},
            "device_status": fm_client.get_device_status() or [],
            "alerts": fm_client.get_alerts() or [],
        }

        return jsonify({"success": True, "data": monitoring_data})

    except Exception as e:
        logger.error(f"Failed to get monitoring data: {e}")
        return jsonify({"success": False, "message": str(e)})


@monitoring_bp.route("/packet-capture/start", methods=["POST"])
def start_packet_capture():
    """패킷 캡처 시작"""
    try:
        data = request.get_json() or {}
        device_id = data.get("device_id")

        if not device_id:
            return jsonify({"success": False, "message": "Device ID required"})

        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()

        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        result = fm_client.start_packet_capture(device_id, data)
        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"Failed to start packet capture: {e}")
        return jsonify({"success": False, "message": str(e)})


@monitoring_bp.route("/packet-capture/stop", methods=["POST"])
def stop_packet_capture():
    """패킷 캡처 중지"""
    try:
        data = request.get_json() or {}
        capture_id = data.get("capture_id")

        if not capture_id:
            return jsonify({"success": False, "message": "Capture ID required"})

        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()

        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        result = fm_client.stop_packet_capture(capture_id)
        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"Failed to stop packet capture: {e}")
        return jsonify({"success": False, "message": str(e)})


@monitoring_bp.route("/packet-capture/results/<capture_id>", methods=["GET"])
def get_capture_results(capture_id):
    """패킷 캡처 결과 조회"""
    try:
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()

        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        results = fm_client.get_capture_results(capture_id)
        return jsonify({"success": True, "data": results})

    except Exception as e:
        logger.error(f"Failed to get capture results: {e}")
        return jsonify({"success": False, "message": str(e)})
