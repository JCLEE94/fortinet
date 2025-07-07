#!/usr/bin/env python3
"""
ArgoCD API 테스트 스크립트
API 키를 사용하여 ArgoCD 상태를 확인합니다.
"""

import requests
import json
import os
from datetime import datetime

# ArgoCD 설정
ARGOCD_SERVER = "https://argo.jclee.me"
ARGOCD_TOKEN = os.getenv("ARGOCD_TOKEN", "")  # 환경변수로 토큰 전달

def test_argocd_api():
    """ArgoCD API 테스트"""
    
    if not ARGOCD_TOKEN:
        print("❌ ARGOCD_TOKEN 환경변수를 설정해주세요!")
        print("사용법: ARGOCD_TOKEN='your-token' python test-argocd-api.py")
        return
    
    # SSL 검증 비활성화 (자체 서명 인증서인 경우)
    session = requests.Session()
    session.verify = False
    
    # 헤더 설정
    headers = {
        "Authorization": f"Bearer {ARGOCD_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"🔧 ArgoCD API 테스트 시작: {ARGOCD_SERVER}")
    print(f"📅 테스트 시간: {datetime.now()}")
    print("=" * 50)
    
    # 1. 버전 확인
    try:
        print("\n1️⃣ ArgoCD 버전 확인...")
        response = session.get(f"{ARGOCD_SERVER}/api/version", headers=headers)
        if response.status_code == 200:
            version = response.json()
            print(f"✅ ArgoCD 버전: {version.get('Version', 'Unknown')}")
        else:
            print(f"❌ 버전 확인 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 2. 애플리케이션 목록
    try:
        print("\n2️⃣ 애플리케이션 목록 조회...")
        response = session.get(f"{ARGOCD_SERVER}/api/v1/applications", headers=headers)
        if response.status_code == 200:
            apps = response.json()
            print(f"✅ 총 애플리케이션 수: {len(apps.get('items', []))}")
            for app in apps.get('items', []):
                app_name = app['metadata']['name']
                print(f"   - {app_name}")
        else:
            print(f"❌ 애플리케이션 목록 조회 실패: {response.status_code}")
            print(f"   응답: {response.text}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 3. fortinet 앱 상태 확인
    try:
        print("\n3️⃣ fortinet 애플리케이션 상태 확인...")
        response = session.get(f"{ARGOCD_SERVER}/api/v1/applications/fortinet", headers=headers)
        if response.status_code == 200:
            app = response.json()
            status = app.get('status', {})
            print(f"✅ 앱 이름: {app['metadata']['name']}")
            print(f"   - Sync 상태: {status.get('sync', {}).get('status', 'Unknown')}")
            print(f"   - Health 상태: {status.get('health', {}).get('status', 'Unknown')}")
            print(f"   - 네임스페이스: {app['spec']['destination']['namespace']}")
            
            # 리소스 상태
            resources = status.get('resources', [])
            print(f"   - 리소스 수: {len(resources)}")
            
            # 문제가 있는 리소스 찾기
            unhealthy = [r for r in resources if r.get('health', {}).get('status') != 'Healthy']
            if unhealthy:
                print("   ⚠️ 문제가 있는 리소스:")
                for r in unhealthy:
                    print(f"      - {r['kind']}/{r['name']}: {r.get('health', {}).get('status')}")
        else:
            print(f"❌ fortinet 앱 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 4. 동기화 실행
    try:
        print("\n4️⃣ fortinet 앱 동기화 테스트...")
        sync_request = {
            "revision": "HEAD",
            "prune": True,
            "dryRun": True  # 실제로 동기화하지 않고 테스트만
        }
        response = session.post(
            f"{ARGOCD_SERVER}/api/v1/applications/fortinet/sync",
            headers=headers,
            json=sync_request
        )
        if response.status_code == 200:
            print("✅ 동기화 테스트 성공 (dry-run)")
        else:
            print(f"❌ 동기화 테스트 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("\n" + "=" * 50)
    print("✅ API 테스트 완료!")

if __name__ == "__main__":
    # SSL 경고 비활성화
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    test_argocd_api()