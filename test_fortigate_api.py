#!/usr/bin/env python3
"""
FortiGate API 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://localhost:7777"

def test_health():
    """헬스체크 테스트"""
    print("1. 헬스체크 테스트")
    response = requests.get(f"{BASE_URL}/api/health")
    if response.status_code == 200:
        print("✅ 헬스체크 성공")
        data = response.json()
        print(f"  - 상태: {data['status']}")
        print(f"  - 버전: {data['version']}")
    else:
        print(f"❌ 헬스체크 실패: {response.status_code}")

def test_fortimanager_status():
    """FortiManager 상태 테스트"""
    print("\n2. FortiManager 상태 테스트")
    response = requests.get(f"{BASE_URL}/api/fortimanager/status")
    if response.status_code == 200:
        print("✅ FortiManager 상태 확인 성공")
        data = response.json()
        print(f"  - 상태: {data.get('status')}")
        print(f"  - 모드: {data.get('mode')}")
    else:
        print(f"❌ FortiManager 상태 확인 실패: {response.status_code}")

def test_packet_path_analysis():
    """패킷 경로 분석 테스트"""
    print("\n3. 패킷 경로 분석 테스트")
    
    test_cases = [
        {
            "name": "Internal to DMZ",
            "data": {
                "src_ip": "192.168.1.10",
                "dst_ip": "172.16.10.100",
                "port": 443
            }
        },
        {
            "name": "Internal to Internet",
            "data": {
                "src_ip": "192.168.1.10",
                "dst_ip": "8.8.8.8",
                "port": 443
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n  테스트: {test['name']}")
        response = requests.post(
            f"{BASE_URL}/api/fortimanager/analyze-packet-path",
            json=test['data']
        )
        
        if response.status_code == 200:
            print(f"  ✅ 분석 성공")
            data = response.json()
            if 'path' in data:
                print(f"    - 경로 홉 수: {len(data['path'])}")
            print(f"    - 성공 여부: {data.get('success', False)}")
        else:
            print(f"  ❌ 분석 실패: {response.status_code}")

def test_advanced_fortigate():
    """Advanced FortiGate API 테스트"""
    print("\n4. Advanced FortiGate API 테스트")
    
    # 방화벽 정책 가져오기
    response = requests.get(f"{BASE_URL}/api/advanced-fortigate/policies")
    if response.status_code == 200:
        print("✅ 방화벽 정책 조회 성공")
        data = response.json()
        if 'policies' in data:
            print(f"  - 정책 수: {len(data['policies'])}")
    else:
        print(f"❌ 방화벽 정책 조회 실패: {response.status_code}")

def test_monitoring():
    """모니터링 API 테스트"""
    print("\n5. 모니터링 API 테스트")
    
    # WebSocket 상태 확인
    response = requests.get(f"{BASE_URL}/ws/status")
    if response.status_code == 200:
        print("✅ WebSocket 상태 확인 성공")
        data = response.json()
        print(f"  - 활성화: {data.get('enabled', False)}")
        print(f"  - 대시보드 활성: {data.get('dashboard_active', False)}")
    else:
        print(f"❌ WebSocket 상태 확인 실패: {response.status_code}")

def main():
    print("="*50)
    print("FortiGate API 테스트 시작")
    print("="*50)
    
    test_health()
    test_fortimanager_status()
    test_packet_path_analysis()
    test_advanced_fortigate()
    test_monitoring()
    
    print("\n" + "="*50)
    print("테스트 완료")
    print("="*50)

if __name__ == "__main__":
    main()