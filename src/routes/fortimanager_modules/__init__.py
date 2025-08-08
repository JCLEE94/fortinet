"""
FortiManager route modules

This package contains modular components for FortiManager API routes,
split by functionality to maintain the 500-line limit per file.
"""

from .advanced_routes import advanced_bp
from .device_routes import device_bp
from .monitoring_routes import monitoring_bp
from .policy_routes import policy_bp
from .status_routes import status_bp

__all__ = ["status_bp", "device_bp", "policy_bp", "monitoring_bp", "advanced_bp"]
