#!/usr/bin/env python3
"""
Unit tests for Monitoring System
Tests for monitoring/* modules
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
import threading
from datetime import datetime, timedelta
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from monitoring.monitor import (
    SystemMonitor,
    MetricsCollector,
    AlertManager,
    PerformanceTracker
)


class TestSystemMonitor:
    """Test cases for SystemMonitor class"""
    
    @pytest.fixture
    def system_monitor(self):
        """Create a SystemMonitor instance for testing"""
        return SystemMonitor()
    
    def test_initialization(self, system_monitor):
        """Test SystemMonitor initialization"""
        assert system_monitor is not None
        assert hasattr(system_monitor, 'config')
        assert hasattr(system_monitor, 'logger')
        assert hasattr(system_monitor, 'is_running')
        assert system_monitor.is_running is False
    
    def test_start_monitoring(self, system_monitor):
        """Test starting monitoring"""
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance
            
            system_monitor.start_monitoring()
            
            assert system_monitor.is_running is True
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
    
    def test_stop_monitoring(self, system_monitor):
        """Test stopping monitoring"""
        system_monitor.is_running = True
        system_monitor.monitoring_thread = Mock()
        
        system_monitor.stop_monitoring()
        
        assert system_monitor.is_running is False
    
    def test_collect_system_metrics(self, system_monitor):
        """Test system metrics collection"""
        with patch('psutil.cpu_percent') as mock_cpu, \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            # Mock system metrics
            mock_cpu.return_value = 75.5
            mock_memory.return_value = Mock(percent=60.0, available=4000000000)
            mock_disk.return_value = Mock(percent=45.0, free=10000000000)
            
            metrics = system_monitor.collect_system_metrics()
            
            assert 'cpu_percent' in metrics
            assert 'memory_percent' in metrics
            assert 'disk_percent' in metrics
            assert metrics['cpu_percent'] == 75.5
            assert metrics['memory_percent'] == 60.0
            assert metrics['disk_percent'] == 45.0
    
    def test_collect_application_metrics(self, system_monitor):
        """Test application metrics collection"""
        with patch.object(system_monitor, '_get_process_info') as mock_process:
            mock_process.return_value = {
                'pid': 1234,
                'memory_info': Mock(rss=100000000),
                'cpu_percent': 25.0,
                'num_threads': 10
            }
            
            metrics = system_monitor.collect_application_metrics()
            
            assert 'process_id' in metrics
            assert 'memory_usage' in metrics
            assert 'cpu_usage' in metrics
            assert 'thread_count' in metrics
    
    def test_check_health_status(self, system_monitor):
        """Test health status checking"""
        # Mock healthy system
        healthy_metrics = {
            'cpu_percent': 50.0,
            'memory_percent': 40.0,
            'disk_percent': 30.0
        }
        
        with patch.object(system_monitor, 'collect_system_metrics') as mock_metrics:
            mock_metrics.return_value = healthy_metrics
            
            health_status = system_monitor.check_health_status()
            
            assert health_status['status'] == 'healthy'
            assert health_status['cpu_status'] == 'normal'
            assert health_status['memory_status'] == 'normal'
            assert health_status['disk_status'] == 'normal'
    
    def test_check_health_status_critical(self, system_monitor):
        """Test health status with critical metrics"""
        # Mock critical system
        critical_metrics = {
            'cpu_percent': 95.0,
            'memory_percent': 98.0,
            'disk_percent': 99.0
        }
        
        with patch.object(system_monitor, 'collect_system_metrics') as mock_metrics:
            mock_metrics.return_value = critical_metrics
            
            health_status = system_monitor.check_health_status()
            
            assert health_status['status'] == 'critical'
            assert health_status['cpu_status'] == 'critical'
            assert health_status['memory_status'] == 'critical'
            assert health_status['disk_status'] == 'critical'
    
    def test_get_monitoring_summary(self, system_monitor):
        """Test monitoring summary generation"""
        # Add some mock data
        system_monitor.metrics_history = [
            {'timestamp': time.time() - 60, 'cpu_percent': 50.0},
            {'timestamp': time.time() - 30, 'cpu_percent': 60.0},
            {'timestamp': time.time(), 'cpu_percent': 70.0}
        ]
        
        summary = system_monitor.get_monitoring_summary()
        
        assert 'total_data_points' in summary
        assert 'monitoring_duration' in summary
        assert 'average_cpu' in summary
        assert summary['total_data_points'] == 3
    
    def test_alert_threshold_checking(self, system_monitor):
        """Test alert threshold checking"""
        # Mock high CPU usage
        metrics = {'cpu_percent': 90.0, 'memory_percent': 40.0}
        
        with patch.object(system_monitor, 'trigger_alert') as mock_alert:
            system_monitor.check_alert_thresholds(metrics)
            
            mock_alert.assert_called()
            alert_args = mock_alert.call_args[0]
            assert 'cpu' in alert_args[0].lower()


class TestMetricsCollector:
    """Test cases for MetricsCollector class"""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create a MetricsCollector instance"""
        return MetricsCollector()
    
    def test_initialization(self, metrics_collector):
        """Test MetricsCollector initialization"""
        assert metrics_collector is not None
        assert hasattr(metrics_collector, 'metrics_buffer')
        assert hasattr(metrics_collector, 'collection_interval')
        assert isinstance(metrics_collector.metrics_buffer, list)
    
    def test_add_metric(self, metrics_collector):
        """Test adding metrics"""
        metric_data = {
            'metric_name': 'cpu_usage',
            'value': 75.5,
            'timestamp': time.time(),
            'tags': {'host': 'localhost'}
        }
        
        metrics_collector.add_metric(metric_data)
        
        assert len(metrics_collector.metrics_buffer) == 1
        assert metrics_collector.metrics_buffer[0] == metric_data
    
    def test_collect_custom_metrics(self, metrics_collector):
        """Test custom metrics collection"""
        custom_metrics = {
            'api_requests_per_second': 150,
            'database_connections': 25,
            'cache_hit_rate': 85.5
        }
        
        metrics_collector.collect_custom_metrics(custom_metrics)
        
        assert len(metrics_collector.metrics_buffer) == 3
        
        # Check specific metrics
        api_metric = next(m for m in metrics_collector.metrics_buffer 
                         if m['metric_name'] == 'api_requests_per_second')
        assert api_metric['value'] == 150
    
    def test_get_metrics_by_timerange(self, metrics_collector):
        """Test retrieving metrics by time range"""
        now = time.time()
        
        # Add metrics with different timestamps
        old_metric = {
            'metric_name': 'old_metric',
            'value': 100,
            'timestamp': now - 3600  # 1 hour ago
        }
        
        recent_metric = {
            'metric_name': 'recent_metric',
            'value': 200,
            'timestamp': now - 300  # 5 minutes ago
        }
        
        metrics_collector.add_metric(old_metric)
        metrics_collector.add_metric(recent_metric)
        
        # Get metrics from last 10 minutes
        recent_metrics = metrics_collector.get_metrics_by_timerange(
            start_time=now - 600,
            end_time=now
        )
        
        assert len(recent_metrics) == 1
        assert recent_metrics[0]['metric_name'] == 'recent_metric'
    
    def test_aggregate_metrics(self, metrics_collector):
        """Test metrics aggregation"""
        # Add multiple CPU metrics
        for i in range(5):
            metrics_collector.add_metric({
                'metric_name': 'cpu_usage',
                'value': 50 + i * 10,  # 50, 60, 70, 80, 90
                'timestamp': time.time() + i
            })
        
        aggregated = metrics_collector.aggregate_metrics('cpu_usage')
        
        assert aggregated['count'] == 5
        assert aggregated['average'] == 70.0  # (50+60+70+80+90)/5
        assert aggregated['min'] == 50.0
        assert aggregated['max'] == 90.0
    
    def test_export_metrics(self, metrics_collector):
        """Test metrics export functionality"""
        # Add some test metrics
        metrics_collector.add_metric({
            'metric_name': 'test_metric',
            'value': 123.45,
            'timestamp': time.time()
        })
        
        exported_data = metrics_collector.export_metrics(format='json')
        
        assert exported_data is not None
        assert isinstance(exported_data, str)
        assert 'test_metric' in exported_data
        assert '123.45' in exported_data
    
    def test_clear_old_metrics(self, metrics_collector):
        """Test clearing old metrics"""
        now = time.time()
        
        # Add old and new metrics
        metrics_collector.add_metric({
            'metric_name': 'old_metric',
            'value': 100,
            'timestamp': now - 86400  # 24 hours ago
        })
        
        metrics_collector.add_metric({
            'metric_name': 'new_metric',
            'value': 200,
            'timestamp': now
        })
        
        # Clear metrics older than 12 hours
        metrics_collector.clear_old_metrics(max_age_seconds=43200)
        
        assert len(metrics_collector.metrics_buffer) == 1
        assert metrics_collector.metrics_buffer[0]['metric_name'] == 'new_metric'


class TestAlertManager:
    """Test cases for AlertManager class"""
    
    @pytest.fixture
    def alert_manager(self):
        """Create an AlertManager instance"""
        return AlertManager()
    
    def test_initialization(self, alert_manager):
        """Test AlertManager initialization"""
        assert alert_manager is not None
        assert hasattr(alert_manager, 'alert_rules')
        assert hasattr(alert_manager, 'active_alerts')
        assert isinstance(alert_manager.alert_rules, list)
        assert isinstance(alert_manager.active_alerts, list)
    
    def test_add_alert_rule(self, alert_manager):
        """Test adding alert rules"""
        rule = {
            'name': 'high_cpu_usage',
            'condition': 'cpu_percent > 80',
            'severity': 'warning',
            'message': 'CPU usage is high'
        }
        
        alert_manager.add_alert_rule(rule)
        
        assert len(alert_manager.alert_rules) == 1
        assert alert_manager.alert_rules[0] == rule
    
    def test_evaluate_alert_rules(self, alert_manager):
        """Test alert rule evaluation"""
        # Add a CPU alert rule
        alert_manager.add_alert_rule({
            'name': 'high_cpu',
            'condition': 'cpu_percent > 85',
            'severity': 'critical',
            'message': 'CPU usage critical'
        })
        
        # Test with high CPU
        metrics = {'cpu_percent': 90.0}
        
        with patch.object(alert_manager, 'trigger_alert') as mock_trigger:
            alert_manager.evaluate_alert_rules(metrics)
            
            mock_trigger.assert_called_once()
            alert_data = mock_trigger.call_args[0][0]
            assert alert_data['name'] == 'high_cpu'
            assert alert_data['severity'] == 'critical'
    
    def test_evaluate_alert_rules_no_trigger(self, alert_manager):
        """Test alert rule evaluation without triggering"""
        # Add a CPU alert rule
        alert_manager.add_alert_rule({
            'name': 'high_cpu',
            'condition': 'cpu_percent > 85',
            'severity': 'critical',
            'message': 'CPU usage critical'
        })
        
        # Test with normal CPU
        metrics = {'cpu_percent': 50.0}
        
        with patch.object(alert_manager, 'trigger_alert') as mock_trigger:
            alert_manager.evaluate_alert_rules(metrics)
            
            mock_trigger.assert_not_called()
    
    def test_trigger_alert(self, alert_manager):
        """Test alert triggering"""
        alert_data = {
            'name': 'test_alert',
            'severity': 'warning',
            'message': 'Test alert message',
            'timestamp': time.time()
        }
        
        with patch.object(alert_manager, 'send_notification') as mock_notify:
            alert_manager.trigger_alert(alert_data)
            
            # Check that alert is added to active alerts
            assert len(alert_manager.active_alerts) == 1
            assert alert_manager.active_alerts[0]['name'] == 'test_alert'
            
            # Check that notification is sent
            mock_notify.assert_called_once_with(alert_data)
    
    def test_resolve_alert(self, alert_manager):
        """Test alert resolution"""
        # Add an active alert
        alert_data = {
            'id': 'alert_123',
            'name': 'test_alert',
            'severity': 'warning',
            'timestamp': time.time()
        }
        alert_manager.active_alerts.append(alert_data)
        
        # Resolve the alert
        alert_manager.resolve_alert('alert_123')
        
        # Alert should be removed from active alerts
        assert len(alert_manager.active_alerts) == 0
    
    def test_get_active_alerts(self, alert_manager):
        """Test getting active alerts"""
        # Add multiple alerts
        alerts = [
            {'id': '1', 'name': 'alert1', 'severity': 'warning'},
            {'id': '2', 'name': 'alert2', 'severity': 'critical'},
            {'id': '3', 'name': 'alert3', 'severity': 'info'}
        ]
        
        for alert in alerts:
            alert_manager.active_alerts.append(alert)
        
        # Get all active alerts
        active = alert_manager.get_active_alerts()
        assert len(active) == 3
        
        # Get alerts by severity
        critical_alerts = alert_manager.get_active_alerts(severity='critical')
        assert len(critical_alerts) == 1
        assert critical_alerts[0]['name'] == 'alert2'
    
    def test_send_notification(self, alert_manager):
        """Test alert notification sending"""
        alert_data = {
            'name': 'test_alert',
            'severity': 'critical',
            'message': 'Critical system alert'
        }
        
        with patch('monitoring.monitor.logger') as mock_logger:
            alert_manager.send_notification(alert_data)
            
            # Should log the alert
            mock_logger.warning.assert_called()


class TestPerformanceTracker:
    """Test cases for PerformanceTracker class"""
    
    @pytest.fixture
    def performance_tracker(self):
        """Create a PerformanceTracker instance"""
        return PerformanceTracker()
    
    def test_initialization(self, performance_tracker):
        """Test PerformanceTracker initialization"""
        assert performance_tracker is not None
        assert hasattr(performance_tracker, 'performance_data')
        assert isinstance(performance_tracker.performance_data, dict)
    
    def test_start_tracking(self, performance_tracker):
        """Test starting performance tracking"""
        operation_id = performance_tracker.start_tracking('test_operation')
        
        assert operation_id is not None
        assert operation_id in performance_tracker.performance_data
        assert 'start_time' in performance_tracker.performance_data[operation_id]
    
    def test_end_tracking(self, performance_tracker):
        """Test ending performance tracking"""
        operation_id = performance_tracker.start_tracking('test_operation')
        
        # Simulate some work
        time.sleep(0.1)
        
        result = performance_tracker.end_tracking(operation_id)
        
        assert result is not None
        assert 'duration' in result
        assert 'end_time' in result
        assert result['duration'] > 0
    
    def test_track_function_performance(self, performance_tracker):
        """Test function performance tracking decorator"""
        
        @performance_tracker.track_performance
        def test_function():
            time.sleep(0.05)
            return "test_result"
        
        result = test_function()
        
        assert result == "test_result"
        # Check that performance data was recorded
        assert len(performance_tracker.performance_data) > 0
    
    def test_get_performance_stats(self, performance_tracker):
        """Test getting performance statistics"""
        # Track multiple operations
        for i in range(5):
            op_id = performance_tracker.start_tracking('test_op')
            time.sleep(0.01)
            performance_tracker.end_tracking(op_id)
        
        stats = performance_tracker.get_performance_stats('test_op')
        
        assert stats['count'] == 5
        assert 'average_duration' in stats
        assert 'min_duration' in stats
        assert 'max_duration' in stats
        assert stats['average_duration'] > 0
    
    def test_get_slowest_operations(self, performance_tracker):
        """Test getting slowest operations"""
        # Track operations with different durations
        operations = [
            ('fast_op', 0.01),
            ('medium_op', 0.05),
            ('slow_op', 0.1)
        ]
        
        for op_name, sleep_time in operations:
            op_id = performance_tracker.start_tracking(op_name)
            time.sleep(sleep_time)
            performance_tracker.end_tracking(op_id)
        
        slowest = performance_tracker.get_slowest_operations(limit=2)
        
        assert len(slowest) == 2
        assert slowest[0]['operation'] == 'slow_op'
        assert slowest[1]['operation'] == 'medium_op'
    
    def test_clear_performance_data(self, performance_tracker):
        """Test clearing performance data"""
        # Add some performance data
        performance_tracker.start_tracking('test_op')
        
        assert len(performance_tracker.performance_data) > 0
        
        # Clear data
        performance_tracker.clear_performance_data()
        
        assert len(performance_tracker.performance_data) == 0


@pytest.mark.integration
class TestMonitoringSystemIntegration:
    """Integration tests for the monitoring system"""
    
    def test_complete_monitoring_workflow(self):
        """Test complete monitoring workflow"""
        system_monitor = SystemMonitor()
        metrics_collector = MetricsCollector()
        alert_manager = AlertManager()
        
        # Set up alert rule
        alert_manager.add_alert_rule({
            'name': 'test_integration_alert',
            'condition': 'cpu_percent > 50',
            'severity': 'warning',
            'message': 'Integration test alert'
        })
        
        # Collect system metrics
        with patch('psutil.cpu_percent', return_value=75.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value = Mock(percent=60.0)
            mock_disk.return_value = Mock(percent=45.0)
            
            metrics = system_monitor.collect_system_metrics()
            
            # Add metrics to collector
            metrics_collector.add_metric({
                'metric_name': 'cpu_percent',
                'value': metrics['cpu_percent'],
                'timestamp': time.time()
            })
            
            # Evaluate alerts
            with patch.object(alert_manager, 'send_notification') as mock_notify:
                alert_manager.evaluate_alert_rules(metrics)
                
                # Should trigger alert since CPU > 50%
                mock_notify.assert_called_once()
                
                # Check active alerts
                active_alerts = alert_manager.get_active_alerts()
                assert len(active_alerts) > 0
    
    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration"""
        performance_tracker = PerformanceTracker()
        metrics_collector = MetricsCollector()
        
        # Track a function's performance
        @performance_tracker.track_performance
        def example_function():
            time.sleep(0.02)
            return "completed"
        
        # Execute function multiple times
        for _ in range(3):
            result = example_function()
            assert result == "completed"
        
        # Get performance stats
        stats = performance_tracker.get_performance_stats('example_function')
        
        assert stats['count'] == 3
        assert stats['average_duration'] > 0
        
        # Add performance metrics to collector
        metrics_collector.add_metric({
            'metric_name': 'function_performance',
            'value': stats['average_duration'],
            'timestamp': time.time(),
            'tags': {'function': 'example_function'}
        })
        
        # Verify metric was added
        function_metrics = [m for m in metrics_collector.metrics_buffer 
                          if m['metric_name'] == 'function_performance']
        assert len(function_metrics) == 1
    
    def test_real_time_monitoring_simulation(self):
        """Test real-time monitoring simulation"""
        system_monitor = SystemMonitor()
        
        monitoring_results = []
        
        def mock_monitoring_iteration():
            """Simulate one monitoring iteration"""
            with patch('psutil.cpu_percent', return_value=65.0), \
                 patch('psutil.virtual_memory') as mock_memory:
                
                mock_memory.return_value = Mock(percent=70.0)
                
                metrics = system_monitor.collect_system_metrics()
                health = system_monitor.check_health_status()
                
                monitoring_results.append({
                    'metrics': metrics,
                    'health': health,
                    'timestamp': time.time()
                })
        
        # Simulate multiple monitoring iterations
        for _ in range(3):
            mock_monitoring_iteration()
            time.sleep(0.01)  # Small delay between iterations
        
        # Verify results
        assert len(monitoring_results) == 3
        
        for result in monitoring_results:
            assert 'metrics' in result
            assert 'health' in result
            assert 'timestamp' in result
            assert result['metrics']['cpu_percent'] == 65.0
            assert result['health']['status'] in ['healthy', 'warning', 'critical']