#!/usr/bin/env python3
"""
FortiManager 사용자명 1411로 테스트
"""

import requests
import json
import urllib3

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://hjsim-1034-451984.fortidemo.fortinet.com:14005"
API_KEY = "o5a7bdmmsni3uwdpj8wnnpj6tkanyk81"
USERNAME = "1411"

def test_with_username_1411():
    """사용자명 1411로 다양한 인증 시도"""
    
    print(f"🔐 FortiManager 인증 테스트 - 사용자명: {USERNAME}")
    print("=" * 80)
    
    # 1. 사용자명/API키로 로그인
    print("\n1. 로그인 시도 (username: 1411, password: API key)")
    login_request = {
        "id": 1,
        "method": "exec",
        "params": [{
            "url": "/sys/login/user",
            "data": {
                "user": USERNAME,
                "passwd": API_KEY
            }
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/jsonrpc",
            headers=headers,
            json=login_request,
            verify=False,
            timeout=10
        )
        
        result = response.json()
        print(f"로그인 응답: {json.dumps(result, indent=2)}")
        
        # 세션 ID 확인
        if 'session' in result:
            session_id = result['session']
            print(f"\n✅ 로그인 성공! 세션 ID: {session_id}")
            
            # 세션 ID로 테스트
            print("\n2. 세션 ID로 상태 조회")
            session_test = {
                "id": 1,
                "session": session_id,
                "method": "get",
                "params": [{"url": "/sys/status"}]
            }
            
            response = requests.post(
                f"{BASE_URL}/jsonrpc",
                headers=headers,
                json=session_test,
                verify=False
            )
            
            print(f"세션 테스트 결과: {json.dumps(response.json(), indent=2)}")
            
    except Exception as e:
        print(f"에러: {e}")
    
    # 2. API 키와 사용자명 헤더 조합
    print("\n\n3. API 키 + 사용자명 헤더")
    headers_with_user = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        "X-Username": USERNAME,
        "X-User": USERNAME
    }
    
    test_request = {
        "id": 1,
        "method": "get",
        "params": [{"url": "/sys/status"}]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/jsonrpc",
            headers=headers_with_user,
            json=test_request,
            verify=False
        )
        
        result = response.json()
        print(f"응답: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"에러: {e}")
    
    # 3. 다른 패스워드 시도
    print("\n\n4. 다른 패스워드 조합 시도")
    passwords = [
        API_KEY,
        "1411",
        "password",
        "admin",
        "",
        "fortinet"
    ]
    
    for pwd in passwords:
        print(f"\n패스워드 시도: {pwd[:10]}...")
        login_attempt = {
            "id": 1,
            "method": "exec",
            "params": [{
                "url": "/sys/login/user",
                "data": {
                    "user": USERNAME,
                    "passwd": pwd
                }
            }]
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/jsonrpc",
                headers={"Content-Type": "application/json"},
                json=login_attempt,
                verify=False
            )
            
            result = response.json()
            if 'result' in result:
                code = result['result'][0]['status']['code']
                if code == 0:
                    print(f"✅ 로그인 성공! 패스워드: {pwd}")
                    if 'session' in result:
                        print(f"세션 ID: {result['session']}")
                    break
                elif code == -22:
                    print(f"❌ 로그인 실패")
                else:
                    print(f"⚠️  다른 에러: {code}")
                    
        except Exception as e:
            print(f"에러: {str(e)[:50]}")
    
    print("\n" + "="*80)
    print("테스트 완료!")

if __name__ == "__main__":
    test_with_username_1411()