"""
API routes (Modularized for maintainability)

This file serves as a main router that aggregates route modules to maintain
the 500-line limit per file. Each functional area is split into separate modules.
"""

from flask import Blueprint

from utils.unified_logger import get_logger

from .api_modules import system_bp

logger = get_logger(__name__)

# Main API blueprint that aggregates all sub-modules
api_bp = Blueprint("api", __name__, url_prefix="/api")

# Register all sub-module blueprints
api_bp.register_blueprint(system_bp)
