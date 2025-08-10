"""
FortiManager API routes (Modularized for maintainability)

This file serves as a main router that aggregates route modules to maintain
the 500-line limit per file. Each functional area is split into separate modules.
"""

from flask import Blueprint

from utils.unified_logger import get_logger

logger = get_logger(__name__)

# Create a new blueprint for FortiManager routes
fortimanager_bp = Blueprint("fortimanager", __name__, url_prefix="/api/fortimanager")
