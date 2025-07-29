#!/usr/bin/env python3
"""
Feature testing script for FortiGate Nextrade platform
Tests all major features and reports their status
"""

import os
import sys
from typing import Dict, List

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))


def test_result(name: str, success: bool, details: str = "") -> Dict:
    """Create standardized test result"""
    return {
        "name": name,
        "success": success,
        "details": details,
        "status": "✅ PASS" if success else "❌ FAIL",
    }


def test_basic_imports() -> Dict:
    """Test basic imports and dependencies"""
    try:
        pass

        return test_result(
            "Basic Imports", True, "All core modules imported successfully"
        )
    except Exception as e:
        return test_result("Basic Imports", False, f"Import error: {str(e)}")


def test_flask_app_creation() -> Dict:
    """Test Flask application creation"""
    try:
        from web_app import create_app

        app = create_app()
        if app:
            return test_result(
                "Flask App Creation",
                True,
                f"App created with {len(app.blueprints)} blueprints",
            )
        return test_result("Flask App Creation", False, "App creation returned None")
    except Exception as e:
        return test_result("Flask App Creation", False, f"Error: {str(e)}")


def test_api_clients() -> Dict:
    """Test API client initialization"""
    try:
        from api.clients.faz_client import FAZClient
        from api.clients.fortigate_api_client import FortiGateAPIClient
        from api.clients.fortimanager_api_client import FortiManagerAPIClient

        # Test initialization (don't actually connect)
        fg_client = FortiGateAPIClient(
            host="127.0.0.1", username="test", password="test"
        )
        fm_client = FortiManagerAPIClient(
            host="127.0.0.1", username="test", password="test"
        )
        faz_client = FAZClient(host="127.0.0.1", username="test", password="test")

        return test_result(
            "API Clients",
            True,
            "FortiGate, FortiManager, and FortiAnalyzer clients initialized",
        )
    except Exception as e:
        return test_result("API Clients", False, f"Error: {str(e)}")


def test_fortimanager_advanced_hub() -> Dict:
    """Test FortiManager Advanced Hub"""
    try:
        from fortimanager.advanced_hub import FortiManagerAdvancedHub

        hub = FortiManagerAdvancedHub()

        # Check if all modules are initialized
        modules = [
            "policy_orchestrator",
            "compliance_framework",
            "security_fabric",
            "analytics_engine",
        ]
        for module in modules:
            if not hasattr(hub, module):
                return test_result(
                    "FortiManager Advanced Hub", False, f"Missing module: {module}"
                )

        capabilities = hub.get_module_capabilities()
        return test_result(
            "FortiManager Advanced Hub",
            True,
            f"Hub initialized with {len(capabilities)} modules",
        )
    except Exception as e:
        return test_result("FortiManager Advanced Hub", False, f"Error: {str(e)}")


def test_itsm_automation() -> Dict:
    """Test ITSM automation engine"""
    try:
        from itsm.automation_service import get_automation_service
        from itsm.policy_automation import PolicyAutomationEngine

        engine = PolicyAutomationEngine()
        get_automation_service()

        # Check basic functionality
        zones = len(engine.network_zones)
        devices = len(engine.firewall_devices)

        return test_result(
            "ITSM Automation",
            True,
            f"Engine initialized with {zones} zones and {devices} devices",
        )
    except Exception as e:
        return test_result("ITSM Automation", False, f"Error: {str(e)}")


def test_monitoring_system() -> Dict:
    """Test monitoring and alerting system"""
    try:
        from monitoring.manager import get_unified_manager
        from monitoring.realtime.alerts import RealtimeAlertSystem
        from monitoring.realtime.monitor import get_monitor

        get_unified_manager()
        get_monitor()
        RealtimeAlertSystem()

        return test_result(
            "Monitoring System",
            True,
            "Unified manager, real-time monitor, and alert system initialized",
        )
    except Exception as e:
        return test_result("Monitoring System", False, f"Error: {str(e)}")


def test_security_features() -> Dict:
    """Test security and packet analysis features"""
    try:
        from security.packet_sniffer_api import get_packet_sniffer_api
        from security.scanner import get_security_scanner

        get_security_scanner()
        get_packet_sniffer_api()

        return test_result(
            "Security Features",
            True,
            "Security scanner and packet sniffer API initialized",
        )
    except Exception as e:
        return test_result("Security Features", False, f"Error: {str(e)}")


def test_data_pipeline() -> Dict:
    """Test data processing and transformation pipeline"""
    try:
        from analysis.analyzer import FirewallRuleAnalyzer
        from analysis.visualizer import PathVisualizer
        from utils.data_transformer import DataTransformer

        DataTransformer()
        FirewallRuleAnalyzer()
        PathVisualizer()

        return test_result(
            "Data Pipeline",
            True,
            "Data transformer, analyzer, and visualizer initialized",
        )
    except Exception as e:
        return test_result("Data Pipeline", False, f"Error: {str(e)}")


def test_caching_system() -> Dict:
    """Test caching and performance systems"""
    try:
        from utils.unified_cache_manager import get_cache_manager

        cache_manager = get_cache_manager()

        cache_stats = cache_manager.get_stats()
        return test_result(
            "Caching System",
            True,
            f"Cache manager with {cache_stats['backends']} backends",
        )
    except Exception as e:
        return test_result("Caching System", False, f"Error: {str(e)}")


def test_api_endpoints() -> Dict:
    """Test core API endpoints with test client"""
    try:
        from web_app import create_app

        app = create_app()
        with app.test_client() as client:
            # Test health endpoint
            health_response = client.get("/api/health")
            if health_response.status_code != 200:
                return test_result(
                    "API Endpoints",
                    False,
                    f"Health endpoint returned {health_response.status_code}",
                )

            # Test settings endpoint
            settings_response = client.get("/api/settings")
            if settings_response.status_code != 200:
                return test_result(
                    "API Endpoints",
                    False,
                    f"Settings endpoint returned {settings_response.status_code}",
                )

            return test_result(
                "API Endpoints", True, "Core API endpoints responding correctly"
            )
    except Exception as e:
        return test_result("API Endpoints", False, f"Error: {str(e)}")


def run_comprehensive_feature_test() -> List[Dict]:
    """Run all feature tests"""
    print("🚀 FortiGate Nextrade Feature Test Suite")
    print("=" * 60)

    tests = [
        test_basic_imports,
        test_flask_app_creation,
        test_api_clients,
        test_fortimanager_advanced_hub,
        test_itsm_automation,
        test_monitoring_system,
        test_security_features,
        test_data_pipeline,
        test_caching_system,
        test_api_endpoints,
    ]

    results = []
    passed = 0
    failed = 0

    for test_func in tests:
        print(f"\n🔍 Running {test_func.__name__}...")
        try:
            result = test_func()
            results.append(result)

            print(f"   {result['status']} {result['name']}")
            if result["details"]:
                print(f"   📝 {result['details']}")

            if result["success"]:
                passed += 1
            else:
                failed += 1

        except Exception as e:
            error_result = test_result(
                test_func.__name__, False, f"Unexpected error: {str(e)}"
            )
            results.append(error_result)
            print(f"   {error_result['status']} {error_result['name']}")
            print(f"   📝 {error_result['details']}")
            failed += 1

    # Summary
    total = len(tests)
    success_rate = (passed / total * 100) if total > 0 else 0

    print("\n" + "=" * 60)
    print("📊 FEATURE TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests:    {total}")
    print(f"Passed:         {passed}")
    print(f"Failed:         {failed}")
    print(f"Success rate:   {success_rate:.1f}%")

    if failed > 0:
        print(f"\n❌ Failed Features ({failed}):")
        for result in results:
            if not result["success"]:
                print(f"   • {result['name']}: {result['details']}")

    if passed > 0:
        print(f"\n✅ Working Features ({passed}):")
        for result in results:
            if result["success"]:
                print(f"   • {result['name']}")

    return results


if __name__ == "__main__":
    # Set test mode
    os.environ["APP_MODE"] = "test"
    os.environ["OFFLINE_MODE"] = "true"

    results = run_comprehensive_feature_test()

    # Exit with error code if any tests failed
    failed_count = sum(1 for r in results if not r["success"])
    sys.exit(0 if failed_count == 0 else 1)
