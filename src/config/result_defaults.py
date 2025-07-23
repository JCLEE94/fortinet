"""
결과 페이지 기본값 설정
"""


def get_default_result():
    """기본 분석 결과 데이터"""
    return {
        "allowed": True,
        "src_ip": "192.168.1.10",
        "dst_ip": "10.0.0.50",
        "port": 443,
        "protocol": "tcp",
        "path": [
            {
                "firewall_name": "FortiGate-HQ-01",
                "policy_id": "101",
                "action": "accept",
                "src_zone": "internal",
                "dst_zone": "dmz",
            }
        ],
        "summary": {
            "source_ip": "192.168.1.10",
            "destination_ip": "10.0.0.50",
            "total_hops": 3,
            "port": 443,
            "protocol": "tcp",
        },
    }
