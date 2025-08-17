#!/usr/bin/env python3
"""
Unit tests for Core Security Scanner
Tests for security/scanner/core_scanner.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import threading
from datetime import datetime
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from security.scanner.core_scanner import CoreSecurityScanner


class TestCoreSecurityScanner:
    """Test cases for CoreSecurityScanner class"""
    
    @pytest.fixture
    def scanner(self):
        """Create a scanner instance for testing"""
        return CoreSecurityScanner()
    
    def test_initialization(self, scanner):
        """Test scanner initialization"""
        assert not scanner.is_scanning
        assert scanner.scan_thread is None
        assert scanner.scan_results == []
        assert isinstance(scanner.vulnerability_database, dict)
        assert isinstance(scanner.security_policies, dict)
        assert isinstance(scanner.listeners, list)
        
        # Check scan configuration
        expected_config = {
            "port_scan": True,
            "vulnerability_scan": True,
            "file_integrity_check": True,
            "network_scan": True,
            "docker_security_scan": True,
            "log_analysis": True,
        }
        assert scanner.scan_config == expected_config
        
        # Check security baselines
        assert "open_ports" in scanner.security_baselines
        assert "critical_files" in scanner.security_baselines
        assert "max_cpu_usage" in scanner.security_baselines
        
    def test_start_continuous_scan(self, scanner):
        """Test starting continuous scan"""
        with patch.object(threading.Thread, 'start') as mock_start:
            scanner.start_continuous_scan(interval_hours=1)
            
            assert scanner.is_scanning
            assert scanner.scan_thread is not None
            assert scanner.scan_thread.daemon
            mock_start.assert_called_once()
    
    def test_start_continuous_scan_already_running(self, scanner):
        """Test starting scan when already running"""
        scanner.is_scanning = True
        
        with patch('security.scanner.core_scanner.logger') as mock_logger:
            scanner.start_continuous_scan()
            mock_logger.warning.assert_called_with("이미 스캔이 실행 중입니다")
    
    def test_stop_scanning(self, scanner):
        """Test stopping scan"""
        scanner.is_scanning = True
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        scanner.scan_thread = mock_thread
        
        with patch('security.scanner.core_scanner.logger') as mock_logger:
            scanner.stop_scanning()
            
            assert not scanner.is_scanning
            mock_logger.info.assert_called_with("스캔 중지 중...")
    
    @patch('security.scanner.core_scanner.datetime')
    def test_run_full_security_scan(self, mock_datetime, scanner):
        """Test full security scan execution"""
        # Mock datetime
        mock_start_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_end_time = datetime(2024, 1, 1, 12, 0, 30)
        mock_datetime.now.side_effect = [mock_start_time, mock_end_time]
        
        # Mock scan methods
        scanner.scan_open_ports = Mock(return_value={"total_open_ports": 5})
        scanner.scan_vulnerabilities = Mock(return_value={"total_vulnerabilities": 2})
        scanner.check_file_integrity = Mock(return_value={"changed_files": []})
        scanner.scan_network_security = Mock(return_value={"network_issues": 0})
        scanner.analyze_security_logs = Mock(return_value={"log_issues": 1})
        
        with patch.object(scanner, '_generate_scan_summary') as mock_summary, \
             patch.object(scanner, '_notify_listeners') as mock_notify:
            
            mock_summary.return_value = {"total_issues": 3}
            
            result = scanner.run_full_security_scan()
            
            # Verify scan ID format
            assert result["scan_id"].startswith("scan_")
            assert result["start_time"] == mock_start_time.isoformat()
            assert result["end_time"] == mock_end_time.isoformat()
            assert result["duration_seconds"] == 30.0
            
            # Verify all scan methods were called
            scanner.scan_open_ports.assert_called_once()
            scanner.scan_vulnerabilities.assert_called_once()
            scanner.check_file_integrity.assert_called_once()
            scanner.scan_network_security.assert_called_once()
            scanner.analyze_security_logs.assert_called_once()
            
            # Verify results structure
            assert "port_scan" in result["results"]
            assert "vulnerability_scan" in result["results"]
            assert "file_integrity" in result["results"]
            assert "network_scan" in result["results"]
            assert "log_analysis" in result["results"]
            
            mock_summary.assert_called_once()
            mock_notify.assert_called_once()
            
            # Verify results are stored
            assert len(scanner.scan_results) == 1
    
    def test_run_full_security_scan_selective_config(self, scanner):
        """Test scan with selective configuration"""
        # Disable some scans
        scanner.scan_config["port_scan"] = False
        scanner.scan_config["vulnerability_scan"] = False
        
        scanner.check_file_integrity = Mock(return_value={"changed_files": []})
        scanner.scan_network_security = Mock(return_value={"network_issues": 0})
        scanner.analyze_security_logs = Mock(return_value={"log_issues": 1})
        
        with patch.object(scanner, '_generate_scan_summary') as mock_summary, \
             patch.object(scanner, '_notify_listeners'):
            
            mock_summary.return_value = {"total_issues": 1}
            
            result = scanner.run_full_security_scan()
            
            # Verify only enabled scans are in results
            assert "port_scan" not in result["results"]
            assert "vulnerability_scan" not in result["results"]
            assert "file_integrity" in result["results"]
            assert "network_scan" in result["results"]
            assert "log_analysis" in result["results"]
    
    def test_get_security_dashboard_no_scans(self, scanner):
        """Test dashboard with no previous scans"""
        with patch.object(scanner, '_calculate_security_metrics') as mock_metrics, \
             patch.object(scanner, '_get_security_recommendations') as mock_recommendations:
            
            mock_metrics.return_value = {"score": 0, "trend": "unknown"}
            mock_recommendations.return_value = ["첫 보안 스캔을 실행하세요"]
            
            dashboard = scanner.get_security_dashboard()
            
            assert dashboard["status"] == "idle"
            assert dashboard["total_scans"] == 0
            assert dashboard["latest_scan"] is None
            assert dashboard["security_metrics"]["score"] == 0
            assert len(dashboard["recommendations"]) == 1
    
    def test_get_security_dashboard_with_scans(self, scanner):
        """Test dashboard with existing scans"""
        # Add mock scan result
        mock_scan = {
            "scan_id": "scan_123",
            "summary": {"total_issues": 5}
        }
        scanner.scan_results.append(mock_scan)
        scanner.is_scanning = True
        
        with patch.object(scanner, '_calculate_security_metrics') as mock_metrics, \
             patch.object(scanner, '_get_security_recommendations') as mock_recommendations:
            
            mock_metrics.return_value = {"score": 75, "trend": "improving"}
            mock_recommendations.return_value = ["보안 상태가 양호합니다"]
            
            dashboard = scanner.get_security_dashboard()
            
            assert dashboard["status"] == "scanning"
            assert dashboard["total_scans"] == 1
            assert dashboard["latest_scan"] == mock_scan
            assert dashboard["security_metrics"]["score"] == 75
    
    def test_generate_scan_summary(self, scanner):
        """Test scan summary generation"""
        results = {
            "port_scan": {
                "risk_level": "high",
                "suspicious_ports": 3
            },
            "vulnerability_scan": {
                "risk_level": "critical",
                "vulnerabilities": ["vuln1", "vuln2"]
            },
            "file_integrity": {
                "risk_level": "medium"
            }
        }
        
        summary = scanner._generate_scan_summary(results)
        
        assert summary["total_issues"] == 5  # 3 ports + 2 vulnerabilities
        assert summary["risk_levels"]["high"] == 1
        assert summary["risk_levels"]["critical"] == 1
        assert summary["risk_levels"]["medium"] == 1
        assert summary["risk_levels"]["low"] == 0
    
    def test_calculate_security_metrics_no_scans(self, scanner):
        """Test security metrics with no scans"""
        metrics = scanner._calculate_security_metrics()
        
        assert metrics["score"] == 0
        assert metrics["trend"] == "unknown"
    
    def test_calculate_security_metrics_single_scan(self, scanner):
        """Test security metrics with single scan"""
        scanner.scan_results = [{
            "summary": {"total_issues": 10}
        }]
        
        metrics = scanner._calculate_security_metrics()
        
        assert metrics["score"] == 50  # 100 - (10 * 5)
        assert metrics["total_issues"] == 10
        assert metrics["trend"] == "stable"
    
    def test_calculate_security_metrics_trend(self, scanner):
        """Test security metrics trend calculation"""
        scanner.scan_results = [
            {"summary": {"total_issues": 15}},  # Previous scan
            {"summary": {"total_issues": 10}}   # Latest scan
        ]
        
        metrics = scanner._calculate_security_metrics()
        
        assert metrics["trend"] == "improving"  # Issues decreased
        
        # Test worsening trend
        scanner.scan_results = [
            {"summary": {"total_issues": 5}},   # Previous scan
            {"summary": {"total_issues": 10}}   # Latest scan
        ]
        
        metrics = scanner._calculate_security_metrics()
        assert metrics["trend"] == "worsening"  # Issues increased
    
    def test_get_security_recommendations_no_scans(self, scanner):
        """Test recommendations with no scans"""
        recommendations = scanner._get_security_recommendations()
        
        assert len(recommendations) == 1
        assert recommendations[0] == "첫 보안 스캔을 실행하세요"
    
    def test_get_security_recommendations_with_issues(self, scanner):
        """Test recommendations with various issues"""
        scanner.scan_results = [{
            "results": {
                "port_scan": {"suspicious_ports": [8080, 9090]},
                "vulnerability_scan": {"total_vulnerabilities": 3},
                "file_integrity": {"changed_files": ["/etc/passwd"]}
            }
        }]
        
        recommendations = scanner._get_security_recommendations()
        
        assert len(recommendations) == 3
        assert any("포트" in rec for rec in recommendations)
        assert any("취약점" in rec for rec in recommendations)
        assert any("파일" in rec for rec in recommendations)
    
    def test_get_security_recommendations_good_state(self, scanner):
        """Test recommendations with good security state"""
        scanner.scan_results = [{
            "results": {
                "port_scan": {},
                "vulnerability_scan": {"total_vulnerabilities": 0},
                "file_integrity": {"changed_files": []}
            }
        }]
        
        recommendations = scanner._get_security_recommendations()
        
        assert len(recommendations) == 1
        assert recommendations[0] == "현재 보안 상태가 양호합니다"
    
    def test_listener_management(self, scanner):
        """Test listener add/remove functionality"""
        mock_listener = Mock()
        
        # Test adding listener
        scanner.add_listener(mock_listener)
        assert mock_listener in scanner.listeners
        
        # Test removing listener
        scanner.remove_listener(mock_listener)
        assert mock_listener not in scanner.listeners
    
    def test_notify_listeners(self, scanner):
        """Test listener notification"""
        mock_listener1 = Mock()
        mock_listener2 = Mock()
        failing_listener = Mock(side_effect=Exception("Test error"))
        
        scanner.add_listener(mock_listener1)
        scanner.add_listener(mock_listener2)
        scanner.add_listener(failing_listener)
        
        scan_results = {"scan_id": "test"}
        
        with patch('security.scanner.core_scanner.logger') as mock_logger:
            scanner._notify_listeners(scan_results)
            
            mock_listener1.assert_called_once_with(scan_results)
            mock_listener2.assert_called_once_with(scan_results)
            failing_listener.assert_called_once_with(scan_results)
            mock_logger.error.assert_called_once()


@pytest.mark.integration
class TestCoreSecurityScannerIntegration:
    """Integration tests for CoreSecurityScanner"""
    
    def test_continuous_scan_loop_with_mock_methods(self):
        """Test continuous scan loop with mocked methods"""
        scanner = CoreSecurityScanner()
        
        # Mock all required methods
        scanner.scan_open_ports = Mock(return_value={})
        scanner.scan_vulnerabilities = Mock(return_value={})
        scanner.check_file_integrity = Mock(return_value={})
        scanner.scan_network_security = Mock(return_value={})
        scanner.analyze_security_logs = Mock(return_value={})
        
        with patch.object(scanner, '_generate_scan_summary') as mock_summary, \
             patch.object(scanner, '_notify_listeners'):
            
            mock_summary.return_value = {"total_issues": 0}
            
            # Test loop runs once then stops
            scanner.is_scanning = True
            scanner._continuous_scan_loop(0.001)  # Very short interval
            
            # Verify scan was executed
            scanner.scan_open_ports.assert_called()
            scanner.scan_vulnerabilities.assert_called()
            
    def test_scan_error_handling(self):
        """Test error handling in continuous scan"""
        scanner = CoreSecurityScanner()
        
        # Mock methods to raise exception
        scanner.scan_open_ports = Mock(side_effect=Exception("Test error"))
        
        with patch('security.scanner.core_scanner.logger') as mock_logger, \
             patch('time.sleep') as mock_sleep:
            
            scanner.is_scanning = True
            
            # This should handle the exception and sleep
            scanner._continuous_scan_loop(0.001)
            
            mock_logger.error.assert_called()
            mock_sleep.assert_called_with(300)  # 5 minute wait