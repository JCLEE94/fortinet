"""
FortiManager API routes (Modularized for maintainability)

This file serves as a main router that aggregates route modules to maintain
the 500-line limit per file. Each functional area is split into separate modules.
"""

from flask import Blueprint

from utils.unified_logger import get_logger

from .fortimanager_modules import (
    advanced_bp,
    device_bp,
    monitoring_bp,
    policy_bp,
    status_bp,
)

logger = get_logger(__name__)

# Main FortiManager blueprint that aggregates all sub-modules
fortimanager_bp = Blueprint("fortimanager", __name__, url_prefix="/api/fortimanager")

# Register all sub-module blueprints
fortimanager_bp.register_blueprint(status_bp)
fortimanager_bp.register_blueprint(device_bp)
fortimanager_bp.register_blueprint(policy_bp)
fortimanager_bp.register_blueprint(monitoring_bp)
fortimanager_bp.register_blueprint(advanced_bp)
