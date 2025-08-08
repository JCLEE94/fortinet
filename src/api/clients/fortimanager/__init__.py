#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FortiManager API Client Modular Components
Modular implementation for better maintainability
"""

from .advanced_features import AdvancedFeaturesMixin
from .auth_connection import AuthConnectionMixin
from .device_management import DeviceManagementMixin
from .policy_management import PolicyManagementMixin

__all__ = [
    "AuthConnectionMixin",
    "DeviceManagementMixin",
    "PolicyManagementMixin",
    "AdvancedFeaturesMixin",
]
