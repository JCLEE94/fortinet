"""
FortiManager API routes (Modularized for maintainability)

This file serves as a main router that aggregates route modules to maintain
the 500-line limit per file. Each functional area is split into separate modules.
"""

from flask import Blueprint, jsonify

from utils.unified_logger import get_logger
from utils.api_utils import is_test_mode

logger = get_logger(__name__)

# Create a new blueprint for FortiManager routes
fortimanager_bp = Blueprint("fortimanager", __name__, url_prefix="/api/fortimanager")


@fortimanager_bp.route("/status", methods=["GET"])
def get_fortimanager_status():
    """FortiManager connection status - backward compatibility endpoint"""
    if is_test_mode():
        return jsonify({
            "status": "connected",
            "mode": "test",
            "message": "Test mode - Mock FortiManager",
            "version": "7.0.5",
            "hostname": "FortiManager-Test"
        })

    # Production status check would go here
    return jsonify({
        "status": "disconnected",
        "mode": "production",
        "message": "FortiManager connection not configured"
    })


@fortimanager_bp.route("/analyze-packet-path", methods=["POST"])
def analyze_packet_path():
    """Analyze packet path through FortiManager - backward compatibility endpoint"""
    if is_test_mode():
        return jsonify({
            "success": True,
            "path": [
                {"hop": 1, "device": "FortiGate-1", "action": "allow"},
                {"hop": 2, "device": "FortiGate-2", "action": "route"}
            ],
            "mode": "test"
        })

    # Production analysis would go here
    return jsonify({
        "success": False,
        "message": "Packet path analysis not available in production mode"
    })


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
