"""
Mock data generator for FortiGate Nextrade application.
Provides dummy data for testing and development when real FortiManager/FortiGate is not available.
"""

import os
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List


class DummyDataGenerator:
    """Generates mock data for dashboard and testing purposes"""

    def __init__(self):
        self.device_types = ["FortiGate", "FortiSwitch", "FortiAP", "FortiAnalyzer"]
        self.statuses = ["online", "offline", "warning", "critical"]
        self.locations = ["Seoul", "Busan", "Daegu", "Incheon", "Gwangju", "Daejeon"]

    def generate_dashboard_stats(self) -> Dict[str, Any]:
        """Generate mock dashboard statistics"""
        return {
            "total_devices": random.randint(50, 200),
            "uptime_percentage": round(random.uniform(95.0, 99.9), 1),
            "network_traffic": f"{random.randint(1, 100)} Gbps",
            "active_alerts": random.randint(0, 15),
            "cpu_usage": round(random.uniform(10.0, 80.0), 1),
            "memory_usage": round(random.uniform(30.0, 85.0), 1),
            "disk_usage": round(random.uniform(20.0, 70.0), 1),
        }

    def generate_devices(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate mock device list"""
        devices = []
        for i in range(count):
            device = {
                "id": f"device_{i+1:03d}",
                "name": f"FW-{random.choice(self.locations)}-{i+1:02d}",
                "type": random.choice(self.device_types),
                "status": random.choice(self.statuses),
                "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 254)}",
                "location": random.choice(self.locations),
                "uptime": f"{random.randint(1, 365)} days",
                "version": f"{random.randint(6, 7)}.{random.randint(0, 4)}.{random.randint(0, 9)}",
                "last_seen": datetime.now() - timedelta(minutes=random.randint(0, 60)),
                "cpu_usage": round(random.uniform(5.0, 95.0), 1),
                "memory_usage": round(random.uniform(20.0, 90.0), 1),
                "interfaces": random.randint(8, 48),
                "active_sessions": random.randint(100, 5000),
            }
            devices.append(device)
        return devices

    def generate_security_events(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate mock security events"""
        event_types = [
            "Intrusion Attempt",
            "Malware Detected",
            "Policy Violation",
            "Authentication Failure",
            "Suspicious Traffic",
            "DoS Attack",
        ]
        severities = ["Low", "Medium", "High", "Critical"]

        events = []
        for i in range(count):
            event = {
                "id": f"event_{i+1:05d}",
                "type": random.choice(event_types),
                "severity": random.choice(severities),
                "source_ip": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "destination_ip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 254)}",
                "timestamp": datetime.now()
                - timedelta(minutes=random.randint(0, 1440)),
                "device": f"FW-{random.choice(self.locations)}-{random.randint(1, 20):02d}",
                "description": f"Security event detected on {random.choice(self.device_types)}",
                "action": random.choice(["Blocked", "Allowed", "Monitored"]),
                "count": random.randint(1, 100),
            }
            events.append(event)
        return sorted(events, key=lambda x: x["timestamp"], reverse=True)

    def generate_network_topology(self) -> Dict[str, Any]:
        """Generate mock network topology data"""
        nodes = []
        links = []

        # Generate nodes
        for i in range(random.randint(5, 15)):
            node = {
                "id": f"node_{i}",
                "name": f"Device-{i+1}",
                "type": random.choice(self.device_types),
                "status": random.choice(self.statuses),
                "x": random.randint(50, 950),
                "y": random.randint(50, 450),
            }
            nodes.append(node)

        # Generate links between nodes
        for i in range(len(nodes) - 1):
            if random.random() > 0.3:  # 70% chance of connection
                link = {
                    "source": nodes[i]["id"],
                    "target": nodes[i + 1]["id"],
                    "bandwidth": f"{random.randint(1, 10)} Gbps",
                    "utilization": round(random.uniform(10.0, 80.0), 1),
                }
                links.append(link)

        return {"nodes": nodes, "links": links}

    def generate_policy_analysis_result(
        self, src_ip: str, dst_ip: str, port: int
    ) -> Dict[str, Any]:
        """Generate mock policy analysis result"""
        policies = [
            {"id": 1, "name": "ALLOW_HTTP", "action": "allow"},
            {"id": 2, "name": "BLOCK_MALWARE", "action": "deny"},
            {"id": 3, "name": "INTERNAL_ACCESS", "action": "allow"},
            {"id": 4, "name": "DMZ_POLICY", "action": "allow"},
        ]

        matched_policy = random.choice(policies)

        return {
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "port": port,
            "protocol": "TCP",
            "matched_policy": matched_policy,
            "action": matched_policy["action"],
            "path": [
                {"device": "FW-Main-01", "interface": "port1", "zone": "internal"},
                {"device": "FW-Main-01", "interface": "port2", "zone": "dmz"},
                {"device": "FW-Edge-01", "interface": "port1", "zone": "external"},
            ],
            "analysis_time": datetime.now().isoformat(),
            "confidence": round(random.uniform(85.0, 99.0), 1),
        }

    def generate_monitoring_data(self) -> Dict[str, Any]:
        """Generate mock monitoring data"""
        return {
            "cpu_history": [random.randint(10, 80) for _ in range(24)],
            "memory_history": [random.randint(30, 85) for _ in range(24)],
            "network_history": [random.randint(1, 100) for _ in range(24)],
            "active_connections": random.randint(1000, 10000),
            "threats_blocked": random.randint(0, 50),
            "bandwidth_usage": {
                "upload": f"{random.randint(1, 50)} Mbps",
                "download": f"{random.randint(10, 200)} Mbps",
            },
        }


if __name__ == "__main__":
    # Test the data generator
    generator = DummyDataGenerator()

    print("✅ Dashboard Stats:")
    stats = generator.generate_dashboard_stats()
    print(f"   Total devices: {stats['total_devices']}")
    print(f"   Uptime: {stats['uptime_percentage']}%")

    print("\n✅ Devices:")
    devices = generator.generate_devices(3)
    for device in devices:
        print(f"   {device['name']} ({device['type']}) - {device['status']}")

    print("\n✅ Security Events:")
    events = generator.generate_security_events(3)
    for event in events:
        print(f"   {event['type']} - {event['severity']} - {event['source_ip']}")

    print("\n✅ Policy Analysis:")
    analysis = generator.generate_policy_analysis_result(
        os.getenv("TEST_SRC_IP", "10.10.1.100"),
        os.getenv("TEST_DST_IP", "10.20.1.50"),
        80,
    )
    print(
        f"   {analysis['src_ip']} -> {analysis['dst_ip']}:{analysis['port']} = {analysis['action']}"
    )

    print("\n✅ All mock data generators working correctly!")
