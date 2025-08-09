#!/usr/bin/env python3
"""
Fortinet Mock Server - Postman 컬렉션 기반 Mock API 서버
"""

import secrets
import time
import uuid
from datetime import datetime, timedelta

from flask import Flask, jsonify, request

from config.constants import DEFAULT_PORTS, TRAFFIC_THRESHOLDS

app = Flask(__name__)

# Mock 데이터 저장소
mock_data = {
    "devices": [],
    "policies": [],
    "logs": [],
    "topology": {"nodes": [], "links": []},
}


# 초기 데이터 생성
def initialize_mock_data():
    """Mock 데이터 초기화"""
    # FortiGate 장치 생성
    devices = [
        {
            "id": "FGT1001",
            "name": "FortiGate-Seoul-HQ",
            "ip": "192.168.1.100",
            "status": "online",
            "model": "FortiGate-100F",
            "firmware": "7.2.5",
            "location": "Seoul HQ",
        },
        {
            "id": "FGT1002",
            "name": "FortiGate-Busan-Branch",
            "ip": "192.168.2.100",
            "status": "online",
            "model": "FortiGate-60F",
            "firmware": "7.2.5",
            "location": "Busan Branch",
        },
        {
            "id": "FGT1003",
            "name": "FortiGate-Daejeon-DC",
            "ip": "192.168.3.100",
            "status": "online",
            "model": "FortiGate-200F",
            "firmware": "7.2.4",
            "location": "Daejeon DC",
        },
    ]
    mock_data["devices"] = devices

    # 토폴로지 노드 생성
    nodes = []
    for device in devices:
        nodes.append(
            {
                "id": device["id"],
                "name": device["name"],
                "type": "firewall",
                "status": device["status"],
                "ip": device["ip"],
                "location": device["location"],
                "x": secrets.randbelow(600) + 100,
                "y": secrets.randbelow(400) + 100,
            }
        )

    # 추가 네트워크 요소
    nodes.extend(
        [
            {
                "id": "SW001",
                "name": "Core-Switch-1",
                "type": "switch",
                "status": "online",
                "ip": "192.168.1.1",
                "x": 400,
                "y": 300,
            },
            {
                "id": "RT001",
                "name": "Edge-Router-1",
                "type": "router",
                "status": "online",
                "ip": "10.0.0.1",
                "x": 400,
                "y": 100,
            },
            {
                "id": "FAZ001",
                "name": "FortiAnalyzer",
                "type": "analyzer",
                "status": "online",
                "ip": "192.168.1.110",
                "x": 600,
                "y": 300,
            },
        ]
    )

    mock_data["topology"]["nodes"] = nodes

    # 연결 정보 생성
    links = [
        {"source": "FGT1001", "target": "SW001", "bandwidth": 1000, "utilization": 45},
        {"source": "FGT1002", "target": "SW001", "bandwidth": 100, "utilization": 30},
        {"source": "FGT1003", "target": "SW001", "bandwidth": 1000, "utilization": 60},
        {"source": "SW001", "target": "RT001", "bandwidth": 10000, "utilization": 70},
        {"source": "FGT1001", "target": "FAZ001", "bandwidth": 1000, "utilization": 20},
        {"source": "FGT1002", "target": "FAZ001", "bandwidth": 100, "utilization": 15},
        {"source": "FGT1003", "target": "FAZ001", "bandwidth": 1000, "utilization": 25},
    ]
    mock_data["topology"]["links"] = links

    # 방화벽 정책 생성
    for i in range(20):
        mock_data["policies"].append(
            {
                "policyid": i + 1,
                "name": f"Policy-{i+1}",
                "srcintf": ["port1"],
                "dstintf": ["port2"],
                "srcaddr": ["10.0.0.0/24"],
                "dstaddr": ["192.168.0.0/16"],
                "service": ["HTTP", "HTTPS"],
                "action": "accept" if i % 3 != 0 else "deny",
                "status": "enable" if i % 4 != 0 else "disable",
                "hits": secrets.randbelow(10000) if i % 5 != 0 else 0,
            }
        )

    # 로그 데이터 생성
    generate_mock_logs()


def generate_mock_logs():
    """Mock 로그 생성"""
    log_types = ["traffic", "threat", "event", "system"]
    severities = ["critical", "high", "medium", "low", "info"]

    for i in range(100):
        timestamp = datetime.now() - timedelta(minutes=secrets.randbelow(1440))
        mock_data["logs"].append(
            {
                "logid": str(uuid.uuid4()),
                "type": secrets.choice(log_types),
                "subtype": "forward",
                "time": int(timestamp.timestamp()),
                "date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "srcip": f"10.{secrets.randbelow(256)}.{secrets.randbelow(256)}.{secrets.randbelow(256)}",
                "dstip": f"192.168.{secrets.randbelow(256)}.{secrets.randbelow(256)}",
                "srcport": secrets.randbelow(65535 - 1024) + 1024,
                "dstport": secrets.choice([80, 443, 22, 3389]),
                "severity": secrets.choice(severities),
                "msg": f"Sample log message {i}",
            }
        )


# FortiGate API Endpoints
@app.route("/api/v2/cmdb/firewall/policy", methods=["GET"])
def get_policies():
    """방화벽 정책 조회"""
    return jsonify({"status": "success", "results": mock_data["policies"]})


@app.route("/api/v2/cmdb/system/interface", methods=["GET"])
def get_interfaces():
    """인터페이스 정보 조회"""
    interfaces = []
    for i in range(4):
        interfaces.append(
            {
                "name": f"port{i+1}",
                "ip": f"192.168.{i+1}.1/24",
                "status": "up",
                "type": "physical",
                "speed": "1Gbps",
            }
        )
    return jsonify({"status": "success", "results": interfaces})


# FortiManager API Endpoints
@app.route("/jsonrpc", methods=["POST"])
def fortimanager_api():
    """FortiManager JSON-RPC API"""
    data = request.get_json()
    method = data.get("method")

    if method == "get":
        url = data["params"][0]["url"]

        if "/device/adom/root/device" in url:
            return jsonify(
                {
                    "id": data["id"],
                    "result": [
                        {
                            "status": {"code": 0, "message": "OK"},
                            "data": mock_data["devices"],
                        }
                    ],
                }
            )
        elif "/pm/config/device" in url and "/global/system/interface" in url:
            return jsonify(
                {
                    "id": data["id"],
                    "result": [
                        {
                            "status": {"code": 0, "message": "OK"},
                            "data": get_interfaces()["results"],
                        }
                    ],
                }
            )

    return jsonify(
        {
            "id": data.get("id", 1),
            "result": [{"status": {"code": 0, "message": "OK"}, "data": []}],
        }
    )


# FortiAnalyzer API Endpoints
@app.route("/jsonrpc", methods=["POST"])
def fortianalyzer_api():
    """FortiAnalyzer JSON-RPC API"""
    data = request.get_json()

    if data.get("method") == "get":
        url = data["params"][0]["url"]

        if "/logview/adom/root/device" in url:
            return jsonify(
                {
                    "id": data["id"],
                    "result": [
                        {
                            "status": {"code": 0, "message": "OK"},
                            "data": mock_data["logs"],
                        }
                    ],
                }
            )

    return jsonify(
        {
            "id": data.get("id", 1),
            "result": [{"status": {"code": 0, "message": "OK"}, "data": []}],
        }
    )


# 네트워크 토폴로지 전용 엔드포인트
@app.route("/api/topology/data", methods=["GET"])
def get_topology():
    """네트워크 토폴로지 데이터"""
    return jsonify(
        {
            "status": "success",
            "data": {
                "nodes": mock_data["topology"]["nodes"],
                "links": mock_data["topology"]["links"],
                "summary": {
                    "total_devices": len(
                        [
                            n
                            for n in mock_data["topology"]["nodes"]
                            if n["type"] == "firewall"
                        ]
                    ),
                    "online_devices": len(
                        [
                            n
                            for n in mock_data["topology"]["nodes"]
                            if n["status"] == "online"
                        ]
                    ),
                    "total_links": len(mock_data["topology"]["links"]),
                    "avg_utilization": sum(
                        link["utilization"] for link in mock_data["topology"]["links"]
                    )
                    / len(mock_data["topology"]["links"]),
                },
            },
        }
    )


@app.route("/api/topology/update", methods=["POST"])
def update_topology():
    """토폴로지 업데이트 (노드 위치 등)"""
    data = request.get_json()
    node_id = data.get("node_id")

    for node in mock_data["topology"]["nodes"]:
        if node["id"] == node_id:
            node["x"] = data.get("x", node["x"])
            node["y"] = data.get("y", node["y"])
            break

    return jsonify({"status": "success"})


# 실시간 트래픽 시뮬레이션
@app.route("/api/realtime/traffic", methods=["GET"])
def realtime_traffic():
    """실시간 트래픽 데이터"""
    data = []
    for i in range(10):
        data.append(
            {
                "timestamp": int(time.time()) - i * 10,
                "inbound": secrets.randbelow(1500) + 500,
                "outbound": secrets.randbelow(1200) + 300,
                "sessions": secrets.randbelow(400) + 100,
            }
        )
    return jsonify({"status": "success", "data": data})


# 시스템 상태
@app.route("/api/v2/monitor/system/status", methods=["GET"])
def system_status():
    """시스템 상태"""
    return jsonify(
        {
            "status": "success",
            "results": {
                "hostname": "FortiGate-Mock",
                "version": "7.2.5",
                "serial": "FGT1001MOCK",
                "status": "online",
                "uptime": 864000,
                "cpu": secrets.randbelow(60) + 20,
                "memory": secrets.randbelow(40) + 30,
            },
        }
    )


# 정책 분석
@app.route("/api/policy/analysis", methods=["POST"])
def policy_analysis():
    """정책 분석"""
    unused_policies = [p for p in mock_data["policies"] if p["hits"] == 0]
    duplicate_policies = []

    # 중복 정책 찾기 (간단한 예시)
    seen = []
    for policy in mock_data["policies"]:
        key = f"{policy['srcaddr'][0]}-{policy['dstaddr'][0]}-{policy['service'][0]}"
        if key in seen:
            duplicate_policies.append(policy["policyid"])
        seen.append(key)

    return jsonify(
        {
            "status": "success",
            "data": {
                "total_policies": len(mock_data["policies"]),
                "active_policies": len(
                    [p for p in mock_data["policies"] if p["status"] == "enable"]
                ),
                "unused_policies": [p["policyid"] for p in unused_policies],
                "duplicate_policies": duplicate_policies,
                "policy_hits": {
                    "high": len(
                        [
                            p
                            for p in mock_data["policies"]
                            if p["hits"] > TRAFFIC_THRESHOLDS["HIGH"]
                        ]
                    ),
                    "medium": len(
                        [
                            p
                            for p in mock_data["policies"]
                            if TRAFFIC_THRESHOLDS["MEDIUM"]
                            < p["hits"]
                            <= TRAFFIC_THRESHOLDS["HIGH"]
                        ]
                    ),
                    "low": len(
                        [
                            p
                            for p in mock_data["policies"]
                            if 0 < p["hits"] <= TRAFFIC_THRESHOLDS["MEDIUM"]
                        ]
                    ),
                    "zero": len(unused_policies),
                },
            },
        }
    )


if __name__ == "__main__":
    initialize_mock_data()
    import os

    app.run(
        host="0.0.0.0",
        port=DEFAULT_PORTS["MOCK_SERVER"],
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )
