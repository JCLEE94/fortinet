"""
FortiManager Advanced Features Routes
"""

from flask import Blueprint, jsonify, request

from fortimanager.advanced_hub import FortiManagerAdvancedHub
from utils.api_utils import get_api_manager
from utils.unified_logger import get_logger

logger = get_logger(__name__)

advanced_bp = Blueprint("fortimanager_advanced", __name__)


@advanced_bp.route("/advanced/initialize", methods=["POST"])
def initialize_advanced_features():
    """고급 기능 초기화"""
    try:
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        # Initialize Advanced Hub
        hub = FortiManagerAdvancedHub(fm_client)
        result = hub.initialize()
        
        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"Failed to initialize advanced features: {e}")
        return jsonify({"success": False, "message": str(e)})


@advanced_bp.route("/advanced/compliance/check", methods=["POST"])
def check_compliance():
    """컴플라이언스 확인"""
    try:
        data = request.get_json() or {}
        
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        hub = FortiManagerAdvancedHub(fm_client)
        result = hub.compliance_framework.check_compliance(data)
        
        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"Failed to check compliance: {e}")
        return jsonify({"success": False, "message": str(e)})


@advanced_bp.route("/advanced/policy/analyze-conflicts", methods=["POST"])
def analyze_policy_conflicts():
    """정책 충돌 분석"""
    try:
        data = request.get_json() or {}
        
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        hub = FortiManagerAdvancedHub(fm_client)
        result = hub.policy_orchestrator.analyze_conflicts(data)
        
        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"Failed to analyze policy conflicts: {e}")
        return jsonify({"success": False, "message": str(e)})


@advanced_bp.route("/advanced/analytics/report", methods=["POST"])
def generate_analytics_report():
    """고급 분석 리포트 생성"""
    try:
        data = request.get_json() or {}
        
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({"success": False, "message": "FortiManager not configured"})

        hub = FortiManagerAdvancedHub(fm_client)
        result = hub.analytics_engine.generate_report(data)
        
        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"Failed to generate analytics report: {e}")
        return jsonify({"success": False, "message": str(e)})