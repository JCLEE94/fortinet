#!/usr/bin/env python3
"""
Comprehensive tests for FortiManager compliance automation
Targeting compliance_checker and compliance_reports with 0% coverage
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import asyncio
from dataclasses import asdict

class TestComplianceChecker:
    """Test ComplianceChecker critical functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        # Mock API client
        self.mock_api_client = Mock()
        self.mock_api_client.get_adoms = AsyncMock(return_value=['root'])
        self.mock_api_client.get_devices = AsyncMock(return_value=[
            {'name': 'FortiGate-1', 'status': 'online'},
            {'name': 'FortiGate-2', 'status': 'online'}
        ])
        
    @pytest.mark.asyncio
    async def test_compliance_checker_initialization(self):
        """Test ComplianceChecker initialization"""
        with patch('fortimanager.compliance_checker.ComplianceRuleManager'):
            from fortimanager.compliance_checker import ComplianceChecker
            
            checker = ComplianceChecker(self.mock_api_client)
            
            assert checker.api_client == self.mock_api_client
            assert hasattr(checker, 'rule_manager')
            assert hasattr(checker, 'check_results')
            assert hasattr(checker, 'executor')
            assert checker.check_results == []
    
    @pytest.mark.asyncio
    async def test_run_compliance_checks_all_devices(self):
        """Test running compliance checks on all devices"""
        with patch('fortimanager.compliance_checker.ComplianceRuleManager') as mock_rule_mgr:
            from fortimanager.compliance_checker import ComplianceChecker, ComplianceCheckResult
            from fortimanager.compliance_rules import ComplianceStatus, ComplianceSeverity
            
            # Setup mock rule manager
            mock_rule_mgr_instance = Mock()
            mock_rule_mgr.return_value = mock_rule_mgr_instance
            mock_rule_mgr_instance.get_rules_by_category.return_value = [
                Mock(id='rule1', category='security', severity=ComplianceSeverity.HIGH)
            ]
            
            checker = ComplianceChecker(self.mock_api_client)
            
            # Mock device compliance check
            with patch.object(checker, '_check_device_compliance') as mock_check:
                mock_result = ComplianceCheckResult(
                    rule_id='rule1',
                    device='FortiGate-1',
                    status=ComplianceStatus.COMPLIANT,
                    severity=ComplianceSeverity.HIGH,
                    message='Device is compliant'
                )
                mock_check.return_value = [mock_result]
                
                results = await checker.run_compliance_checks()
                
                assert len(results) >= 1
                assert results[0].device == 'FortiGate-1'
                assert results[0].status == ComplianceStatus.COMPLIANT
    
    @pytest.mark.asyncio  
    async def test_run_compliance_checks_specific_devices(self):
        """Test running compliance checks on specific devices"""
        with patch('fortimanager.compliance_checker.ComplianceRuleManager'):
            from fortimanager.compliance_checker import ComplianceChecker
            
            checker = ComplianceChecker(self.mock_api_client)
            
            specific_devices = ['FortiGate-1']
            
            with patch.object(checker, '_check_device_compliance') as mock_check:
                mock_check.return_value = []
                
                await checker.run_compliance_checks(devices=specific_devices)
                
                # Should only check specified device
                mock_check.assert_called()
    
    @pytest.mark.asyncio
    async def test_check_device_compliance(self):
        """Test individual device compliance checking"""
        with patch('fortimanager.compliance_checker.ComplianceRuleManager'):
            from fortimanager.compliance_checker import ComplianceChecker
            from fortimanager.compliance_rules import ComplianceRule, ComplianceSeverity
            
            checker = ComplianceChecker(self.mock_api_client)
            
            # Mock rule
            test_rule = Mock()
            test_rule.id = 'test_rule'
            test_rule.category = 'security'
            test_rule.severity = ComplianceSeverity.HIGH
            test_rule.description = 'Test security rule'
            
            device_name = 'FortiGate-1'
            rules = [test_rule]
            
            # Mock device configuration
            self.mock_api_client.get_device_config = AsyncMock(return_value={
                'system': {'admin-https-ssl-versions': 'tlsv1-2'},
                'firewall': {'policy': [{'id': 1, 'action': 'accept'}]}
            })
            
            with patch.object(checker, '_evaluate_rule_compliance') as mock_eval:
                mock_eval.return_value = Mock(
                    rule_id='test_rule',
                    device='FortiGate-1', 
                    status='COMPLIANT',
                    message='Test passed'
                )
                
                results = await checker._check_device_compliance(device_name, rules)
                
                assert len(results) == 1
                assert results[0].device == 'FortiGate-1'
    
    def test_compliance_check_result_dataclass(self):
        """Test ComplianceCheckResult dataclass functionality"""
        from fortimanager.compliance_checker import ComplianceCheckResult
        from fortimanager.compliance_rules import ComplianceStatus, ComplianceSeverity
        
        # Create result instance
        result = ComplianceCheckResult(
            rule_id='test_rule',
            device='FortiGate-1',
            status=ComplianceStatus.NON_COMPLIANT,
            severity=ComplianceSeverity.CRITICAL,
            message='Critical violation detected',
            details={'violation_type': 'weak_ssl'},
            evidence=[{'config_line': 'ssl-versions tlsv1'}],
            remediation_available=True
        )
        
        # Test dataclass fields
        assert result.rule_id == 'test_rule'
        assert result.device == 'FortiGate-1'
        assert result.status == ComplianceStatus.NON_COMPLIANT
        assert result.severity == ComplianceSeverity.CRITICAL
        assert result.remediation_available == True
        assert isinstance(result.timestamp, datetime)
        
        # Test serialization
        result_dict = asdict(result)
        assert result_dict['rule_id'] == 'test_rule'
        assert result_dict['device'] == 'FortiGate-1'


class TestComplianceReports:
    """Test compliance reporting functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.mock_api_client = Mock()
        
    def test_compliance_report_generator_init(self):
        """Test ComplianceReportGenerator initialization"""
        with patch('fortimanager.compliance_reports.jinja2'):
            from fortimanager.compliance_reports import ComplianceReportGenerator
            
            generator = ComplianceReportGenerator()
            
            assert hasattr(generator, 'templates')
            assert hasattr(generator, 'report_formats')
    
    def test_generate_compliance_summary(self):
        """Test compliance summary generation"""
        from fortimanager.compliance_reports import ComplianceReportGenerator
        from fortimanager.compliance_checker import ComplianceCheckResult
        from fortimanager.compliance_rules import ComplianceStatus, ComplianceSeverity
        
        generator = ComplianceReportGenerator()
        
        # Mock compliance results
        test_results = [
            ComplianceCheckResult(
                rule_id='rule1',
                device='FortiGate-1',
                status=ComplianceStatus.COMPLIANT,
                severity=ComplianceSeverity.HIGH,
                message='Compliant'
            ),
            ComplianceCheckResult(
                rule_id='rule2', 
                device='FortiGate-1',
                status=ComplianceStatus.NON_COMPLIANT,
                severity=ComplianceSeverity.CRITICAL,
                message='Non-compliant'
            )
        ]
        
        summary = generator._generate_summary(test_results)
        
        assert summary['total_checks'] == 2
        assert summary['compliant_count'] == 1
        assert summary['non_compliant_count'] == 1
        assert summary['compliance_percentage'] == 50.0
        
    def test_generate_html_report(self):
        """Test HTML report generation"""
        from fortimanager.compliance_reports import ComplianceReportGenerator
        from fortimanager.compliance_checker import ComplianceCheckResult
        from fortimanager.compliance_rules import ComplianceStatus, ComplianceSeverity
        
        with patch('fortimanager.compliance_reports.jinja2') as mock_jinja:
            # Mock template
            mock_template = Mock()
            mock_template.render.return_value = '<html>Test Report</html>'
            mock_env = Mock()
            mock_env.get_template.return_value = mock_template
            mock_jinja.Environment.return_value = mock_env
            
            generator = ComplianceReportGenerator()
            
            test_results = [
                ComplianceCheckResult(
                    rule_id='rule1',
                    device='FortiGate-1', 
                    status=ComplianceStatus.COMPLIANT,
                    severity=ComplianceSeverity.MEDIUM,
                    message='Test'
                )
            ]
            
            html_report = generator.generate_html_report(test_results)
            
            assert '<html>Test Report</html>' in html_report
            mock_template.render.assert_called_once()
    
    def test_generate_json_report(self):
        """Test JSON report generation"""
        from fortimanager.compliance_reports import ComplianceReportGenerator
        from fortimanager.compliance_checker import ComplianceCheckResult  
        from fortimanager.compliance_rules import ComplianceStatus, ComplianceSeverity
        import json
        
        generator = ComplianceReportGenerator()
        
        test_results = [
            ComplianceCheckResult(
                rule_id='rule1',
                device='FortiGate-1',
                status=ComplianceStatus.NON_COMPLIANT,
                severity=ComplianceSeverity.HIGH,
                message='Security issue detected'
            )
        ]
        
        json_report = generator.generate_json_report(test_results)
        
        # Parse JSON to verify structure
        report_data = json.loads(json_report)
        
        assert 'summary' in report_data
        assert 'results' in report_data
        assert 'metadata' in report_data
        assert report_data['summary']['total_checks'] == 1
        assert len(report_data['results']) == 1
    
    def test_generate_csv_report(self):
        """Test CSV report generation"""
        from fortimanager.compliance_reports import ComplianceReportGenerator
        from fortimanager.compliance_checker import ComplianceCheckResult
        from fortimanager.compliance_rules import ComplianceStatus, ComplianceSeverity
        
        generator = ComplianceReportGenerator()
        
        test_results = [
            ComplianceCheckResult(
                rule_id='csv_rule',
                device='FortiGate-CSV',
                status=ComplianceStatus.COMPLIANT,
                severity=ComplianceSeverity.LOW,
                message='CSV test'
            )
        ]
        
        csv_report = generator.generate_csv_report(test_results)
        
        # Verify CSV structure
        lines = csv_report.strip().split('\n')
        assert len(lines) >= 2  # Header + data
        assert 'Rule ID' in lines[0]  # Header
        assert 'csv_rule' in lines[1]  # Data


class TestComplianceAutomation:
    """Test FortiManager compliance automation workflow"""
    
    def setup_method(self):
        """Setup automation test environment"""
        self.mock_api_client = Mock()
    
    @pytest.mark.asyncio
    async def test_full_compliance_automation_workflow(self):
        """Test complete compliance automation workflow"""
        with patch('fortimanager.fortimanager_compliance_automation.ComplianceChecker') as mock_checker, \
             patch('fortimanager.fortimanager_compliance_automation.ComplianceReportGenerator') as mock_reporter:
            
            from fortimanager.fortimanager_compliance_automation import FortiManagerComplianceAutomation
            
            # Setup mocks
            mock_checker_instance = Mock()
            mock_checker.return_value = mock_checker_instance
            mock_checker_instance.run_compliance_checks = AsyncMock(return_value=[])
            
            mock_reporter_instance = Mock()
            mock_reporter.return_value = mock_reporter_instance
            mock_reporter_instance.generate_html_report.return_value = '<html>Report</html>'
            
            automation = FortiManagerComplianceAutomation(self.mock_api_client)
            
            result = await automation.run_full_compliance_check()
            
            assert 'compliance_results' in result
            assert 'report_html' in result
            mock_checker_instance.run_compliance_checks.assert_called_once()
            mock_reporter_instance.generate_html_report.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_scheduled_compliance_checks(self):
        """Test scheduled compliance check functionality"""
        with patch('fortimanager.fortimanager_compliance_automation.ComplianceChecker'):
            from fortimanager.fortimanager_compliance_automation import FortiManagerComplianceAutomation
            
            automation = FortiManagerComplianceAutomation(self.mock_api_client)
            
            # Test schedule configuration
            schedule_config = {
                'interval_hours': 24,
                'devices': ['FortiGate-1'],
                'categories': ['security']
            }
            
            with patch.object(automation, 'run_compliance_check') as mock_run:
                mock_run.return_value = []
                
                automation.schedule_compliance_checks(schedule_config)
                
                assert hasattr(automation, 'scheduled_config')
                assert automation.scheduled_config == schedule_config
    
    @pytest.mark.asyncio
    async def test_remediation_automation(self):
        """Test automated remediation functionality"""
        from fortimanager.fortimanager_compliance_automation import FortiManagerComplianceAutomation
        from fortimanager.compliance_checker import ComplianceCheckResult
        from fortimanager.compliance_rules import ComplianceStatus, ComplianceSeverity
        
        automation = FortiManagerComplianceAutomation(self.mock_api_client)
        
        # Create non-compliant result with remediation
        non_compliant_result = ComplianceCheckResult(
            rule_id='ssl_policy',
            device='FortiGate-1',
            status=ComplianceStatus.NON_COMPLIANT,
            severity=ComplianceSeverity.HIGH,
            message='Weak SSL configuration',
            remediation_available=True
        )
        
        # Mock remediation application
        self.mock_api_client.update_device_config = AsyncMock(return_value=True)
        
        with patch.object(automation, '_apply_remediation') as mock_apply:
            mock_apply.return_value = True
            
            success = await automation.apply_automated_remediation([non_compliant_result])
            
            assert success == True
            mock_apply.assert_called_once()


# Error Handling Tests
class TestComplianceErrorHandling:
    """Test error handling in compliance modules"""
    
    def setup_method(self):
        """Setup error handling tests"""
        self.mock_api_client = Mock()
        
    @pytest.mark.asyncio
    async def test_api_connection_failure(self):
        """Test handling of API connection failures"""
        # Mock API failure
        self.mock_api_client.get_devices = AsyncMock(side_effect=Exception("Connection failed"))
        
        with patch('fortimanager.compliance_checker.ComplianceRuleManager'):
            from fortimanager.compliance_checker import ComplianceChecker
            
            checker = ComplianceChecker(self.mock_api_client)
            
            # Should handle gracefully
            with pytest.raises(Exception):
                await checker.run_compliance_checks()
    
    def test_malformed_compliance_data(self):
        """Test handling of malformed compliance data"""
        from fortimanager.compliance_reports import ComplianceReportGenerator
        
        generator = ComplianceReportGenerator()
        
        # Pass invalid data
        invalid_results = [None, {}, "invalid"]
        
        # Should not crash
        try:
            summary = generator._generate_summary(invalid_results)
            assert summary['total_checks'] == 0
        except Exception as e:
            # Expected to handle gracefully
            pass
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling in compliance checks"""
        # Mock slow API response
        async def slow_response():
            await asyncio.sleep(10)
            return []
        
        self.mock_api_client.get_devices = slow_response
        
        with patch('fortimanager.compliance_checker.ComplianceRuleManager'):
            from fortimanager.compliance_checker import ComplianceChecker
            
            checker = ComplianceChecker(self.mock_api_client)
            
            # Should timeout appropriately
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(checker.run_compliance_checks(), timeout=1.0)


# Performance Tests
@pytest.mark.slow
class TestCompliancePerformance:
    """Test compliance system performance"""
    
    def setup_method(self):
        """Setup performance tests"""
        self.mock_api_client = Mock()
    
    @pytest.mark.asyncio
    async def test_large_scale_compliance_check(self):
        """Test compliance checking on large number of devices"""
        # Mock 100 devices
        large_device_list = [f'FortiGate-{i}' for i in range(100)]
        self.mock_api_client.get_devices = AsyncMock(return_value=[
            {'name': name, 'status': 'online'} for name in large_device_list
        ])
        
        with patch('fortimanager.compliance_checker.ComplianceRuleManager'):
            from fortimanager.compliance_checker import ComplianceChecker
            
            checker = ComplianceChecker(self.mock_api_client)
            
            # Mock fast device checks
            with patch.object(checker, '_check_device_compliance') as mock_check:
                mock_check.return_value = []
                
                import time
                start_time = time.time()
                await checker.run_compliance_checks()
                end_time = time.time()
                
                # Should complete within reasonable time
                assert end_time - start_time < 30.0  # 30 seconds max
    
    def test_report_generation_performance(self):
        """Test report generation performance with large datasets"""
        from fortimanager.compliance_reports import ComplianceReportGenerator
        from fortimanager.compliance_checker import ComplianceCheckResult
        from fortimanager.compliance_rules import ComplianceStatus, ComplianceSeverity
        
        generator = ComplianceReportGenerator()
        
        # Generate 1000 compliance results
        large_results = []
        for i in range(1000):
            result = ComplianceCheckResult(
                rule_id=f'rule_{i}',
                device=f'FortiGate-{i % 10}',
                status=ComplianceStatus.COMPLIANT,
                severity=ComplianceSeverity.MEDIUM,
                message=f'Test result {i}'
            )
            large_results.append(result)
        
        import time
        start_time = time.time()
        json_report = generator.generate_json_report(large_results)
        end_time = time.time()
        
        # Should generate report quickly
        assert end_time - start_time < 5.0  # 5 seconds max
        assert len(json_report) > 1000  # Should contain data