"""
FortiManager API routes (Modularized for maintainability)

This file serves as a main router that aggregates route modules to maintain
the 500-line limit per file. Each functional area is split into separate modules.
"""

from flask import Blueprint, jsonify

# Removed test mode dependencies - using production APIs only
from utils.unified_logger import get_logger

logger = get_logger(__name__)

# Create a new blueprint for FortiManager routes
fortimanager_bp = Blueprint("fortimanager", __name__, url_prefix="/api/fortimanager")


@fortimanager_bp.route("/status", methods=["GET"])
def get_fortimanager_status():
    """FortiManager connection status - Real API implementation"""
    try:
        from api.clients.fortimanager_api_client import FortiManagerAPIClient

        client = FortiManagerAPIClient()
        if client.test_connection():
            return jsonify(
                {
                    "status": "connected",
                    "mode": "production",
                    "message": "FortiManager connected successfully",
                    "version": client.get_version(),
                    "hostname": client.get_hostname(),
                }
            )
        else:
            return jsonify(
                {
                    "status": "disconnected",
                    "mode": "production",
                    "message": "FortiManager connection failed - check configuration",
                }
            )
    except Exception as e:
        logger.error(f"FortiManager status check failed: {e}")
        return jsonify({"status": "error", "mode": "production", "message": f"FortiManager API error: {str(e)}"})


@fortimanager_bp.route("/analyze-packet-path", methods=["POST"])
def analyze_packet_path():
    """Analyze packet path through FortiManager - Real implementation"""
    try:
        from flask import request

        from analysis.fixed_path_analyzer import FixedPathAnalyzer

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        src_ip = data.get("src_ip")
        dst_ip = data.get("dst_ip")
        port = data.get("port", 80)

        if not src_ip or not dst_ip:
            return jsonify({"success": False, "message": "src_ip and dst_ip required"}), 400

        # Use real path analyzer
        analyzer = FixedPathAnalyzer()
        result = analyzer.analyze_path(src_ip, dst_ip, port)

        return jsonify(
            {
                "success": result["allowed"],
                "path": result["path"],
                "analysis": result["analysis_summary"],
                "policy": {
                    "matched": result["analysis_summary"]["matched_policy"],
                    "description": result["analysis_summary"]["policy_description"],
                    "action": "allow" if result["allowed"] else "deny",
                },
                "mode": "production",
            }
        )

    except Exception as e:
        logger.error(f"Packet path analysis failed: {e}")
        return jsonify({"success": False, "message": f"Analysis error: {str(e)}"}), 500


# Register sub-blueprints for modular organization
try:
    from .fortimanager.analytics_routes import analytics_bp
    from .fortimanager.compliance_routes import compliance_bp
    from .fortimanager.device_routes import device_bp

    fortimanager_bp.register_blueprint(analytics_bp)
    fortimanager_bp.register_blueprint(compliance_bp)
    fortimanager_bp.register_blueprint(device_bp)

    logger.info("FortiManager sub-blueprints registered successfully")
except ImportError as e:
    logger.warning(f"Some FortiManager sub-modules not available: {e}")
