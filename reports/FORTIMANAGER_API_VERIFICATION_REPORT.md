# FortiManager API 검증 및 리팩토링 보고서

## 📋 검증 개요

FortiManager API 공식 문서(https://how-to-fortimanager-api.readthedocs.io)를 기반으로 현재 구현을 검증하고, 방화벽 경로 분석 기능을 중심으로 리팩토링했습니다.

## 🔍 주요 발견사항

### ✅ 올바르게 구현된 부분

1. **JSON-RPC 표준 형식 준수**
   - `src/utils/api_common.py`의 `JsonRpcMixin` 클래스가 공식 표준을 올바르게 구현
   - `params`를 배열 형태로 전송: `"params": [{"url": "...", "data": {...}}]`
   - 세션 기반 인증과 토큰 기반 인증 모두 지원

2. **URL 구조 표준 준수**
   - Device Global Settings: `/pm/config/device/<device>/global/<cli>`
   - VDOM Security Settings: `/pm/config/device/<device>/vdom/<vdom>/<cli>`
   - Policy Package Management: `/pm/config/adom/<adom>/pkg/<package>/<cli>`

3. **방법론(Method) 올바른 사용**
   - `get`: 데이터 조회
   - `set`: 데이터 수정
   - `add`: 데이터 추가
   - `delete`: 데이터 삭제
   - `exec`: 명령 실행

### ⚠️ 개선이 필요한 부분

1. **패킷 경로 분석 기능 부족**
   - 현재 Mock 데이터에만 의존
   - 실제 FortiManager API를 활용한 경로 분석 로직 미흡
   - 라우팅 테이블과 인터페이스 정보 활용 부족

2. **API 응답 처리 개선 필요**
   - FortiManager 특정 에러 코드 처리 강화 필요
   - Task 모니터링 로직 개선 필요

## 🚀 리팩토링 완료 사항

### 1. FortiManager API 클라이언트 강화

**파일**: `src/api/clients/fortimanager_api_client.py`

#### 추가된 주요 메서드:

```python
# Device Settings vs Security Settings 분리
def get_device_global_settings(self, device_name: str, cli_path: str, adom: str = "root")
def set_device_global_settings(self, device_name: str, cli_path: str, data: Dict[str, Any], adom: str = "root")
def get_device_vdom_settings(self, device_name: str, vdom: str, cli_path: str, adom: str = "root")
def set_device_vdom_settings(self, device_name: str, vdom: str, cli_path: str, data: Dict[str, Any], adom: str = "root")

# Policy Package Management
def get_policy_package_settings(self, package_name: str, cli_path: str, adom: str = "root")

# 강화된 패킷 경로 분석
def analyze_packet_path(self, src_ip: str, dst_ip: str, port: int, protocol: str = "tcp", 
                       device_name: str = None, vdom: str = "root") -> Dict[str, Any]
```

#### 패킷 경로 분석 로직 강화:

1. **라우팅 테이블 분석**: `get_routes()` 메서드로 실제 라우팅 정보 수집
2. **인터페이스 정보 수집**: `get_interfaces()` 메서드로 네트워크 인터페이스 정보 획득
3. **정책 매칭**: `get_firewall_policies()` 메서드로 적용 가능한 정책 확인
4. **경로 결정**: 수집된 정보를 바탕으로 실제 패킷 흐름 경로 분석

### 2. 라우트 핸들러 개선

**파일**: `src/routes/fortimanager_routes.py`

#### `/analyze-packet-path` 엔드포인트 강화:

```python
@fortimanager_bp.route('/analyze-packet-path', methods=['POST'])
def analyze_packet_path():
    """패킷 경로 분석 (FortiManager API 기반)"""
    try:
        data = request.get_json()
        
        if is_test_mode():
            # Test mode - Mock 데이터 사용
            result = mock_fortigate.analyze_packet_path(...)
        else:
            # Production mode - 실제 FortiManager API 사용
            client = FortiManagerAPIClient(...)
            result = client.analyze_packet_path(...)
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### 개선 사항:
- Production 모드에서 실제 FortiManager API 사용
- 자동 인증 및 세션 관리
- 디바이스별 경로 분석 지원
- 상세한 에러 처리

### 3. JSON-RPC 표준 준수 강화

**파일**: `src/utils/api_common.py`

#### JSON-RPC 믹스인 개선:

```python
def build_json_rpc_request(self, method: str, url: str, data: Optional[Dict] = None, 
                          session: Optional[str] = None, verbose: int = 0) -> Dict[str, Any]:
    """JSON-RPC 요청 페이로드 생성 (FortiManager 공식 표준 준수)"""
    params_obj = {"url": url}
    
    if data:
        params_obj["data"] = data
        
    if verbose > 0:
        params_obj["verbose"] = verbose
    
    payload = {
        "id": self.get_next_request_id(),
        "method": method,
        "params": [params_obj]  # 배열 형태로 수정 (공식 표준)
    }
    
    if session:
        payload["session"] = session
        
    return payload

def parse_json_rpc_response(self, response: Dict[str, Any]) -> Tuple[bool, Any]:
    """JSON-RPC 응답 파싱 (FortiManager 공식 응답 형식 준수)"""
    if not isinstance(response, dict):
        return False, "Invalid response format"
    
    # JSON-RPC 오류 확인
    if "error" in response:
        error = response["error"]
        return False, f"JSON-RPC Error: {error.get('message', 'Unknown error')}"
    
    # FortiManager는 result가 배열 형태로 반환됨
    result = response.get("result")
    if isinstance(result, list) and len(result) > 0:
        first_result = result[0]
        status = first_result.get("status", {})
        
        # 상태 코드 0은 성공
        if status.get("code") == 0:
            return True, first_result.get("data", first_result)
        else:
            error_msg = status.get("message", "Unknown error")
            return False, f"FortiManager Error (Code {status.get('code')}): {error_msg}"
    
    return True, result
```

## 🔧 사용 방법

### 1. Device Settings 관리

```python
client = FortiManagerAPIClient(host="192.168.1.100", api_token="your_token")

# 인터페이스 설정 조회 (Global Settings)
interfaces = client.get_device_global_settings("FGT-001", "system/interface")

# DNS 설정 수정 (Global Settings)
dns_config = {"primary": "8.8.8.8", "secondary": "1.1.1.1"}
client.set_device_global_settings("FGT-001", "system/dns", dns_config)
```

### 2. Security Settings 관리

```python
# 방화벽 정책 조회 (VDOM Settings)
policies = client.get_device_vdom_settings("FGT-001", "root", "firewall/policy")

# 라우팅 설정 수정 (VDOM Settings)
route_config = {"dst": "10.0.0.0/8", "gateway": "192.168.1.1", "device": "port1"}
client.set_device_vdom_settings("FGT-001", "root", "router/static", route_config)
```

### 3. 패킷 경로 분석

```python
# HTTP 트래픽 경로 분석
result = client.analyze_packet_path(
    src_ip="192.168.1.100",
    dst_ip="10.0.0.50", 
    port=80,
    protocol="tcp",
    device_name="FGT-001",
    vdom="root"
)

print(f"Ingress Interface: {result['analysis_result']['ingress_interface']}")
print(f"Egress Interface: {result['analysis_result']['egress_interface']}")
print(f"Applied Policies: {len(result['analysis_result']['applied_policies'])}")
print(f"Final Action: {result['analysis_result']['final_action']}")
```

### 4. API 엔드포인트 사용

```bash
# 패킷 경로 분석 API 호출
curl -X POST http://localhost:7777/api/fortimanager/analyze-packet-path \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.1.100",
    "dst_ip": "172.16.10.100",
    "port": 80,
    "protocol": "tcp",
    "device_name": "FGT-001",
    "vdom": "root"
  }'
```

## 📊 검증 결과

### ✅ 공식 API 표준 준수 확인

1. **JSON-RPC 형식**: ✅ 완전 준수
   - `params` 배열 형태 사용
   - 올바른 세션 및 토큰 인증
   - 표준 응답 파싱

2. **URL 구조**: ✅ 완전 준수
   - Device Global: `/pm/config/device/{device}/global/{cli}`
   - VDOM Security: `/pm/config/device/{device}/vdom/{vdom}/{cli}`
   - Policy Package: `/pm/config/adom/{adom}/pkg/{package}/{cli}`

3. **HTTP 메서드**: ✅ 올바른 JSON-RPC 메서드 사용
   - `get`, `set`, `add`, `delete`, `exec`

### 🚀 방화벽 경로 분석 기능 강화

1. **실제 API 활용**: FortiManager API를 통한 실제 네트워크 정보 수집
2. **종합적 분석**: 라우팅, 인터페이스, 정책을 종합한 경로 분석
3. **상세한 결과**: 입구/출구 인터페이스, 적용 정책, 최종 액션 제공

### 🔄 Test Mode vs Production Mode

- **Test Mode**: Mock FortiGate 데이터 사용 (개발/테스트용)
- **Production Mode**: 실제 FortiManager API 사용 (운영용)

## 📝 추후 개선 계획

1. **Task 모니터링**: Install Device Settings 작업의 진행 상황 추적
2. **캐싱 강화**: 자주 조회되는 데이터의 캐싱 최적화
3. **에러 처리**: FortiManager 특정 에러 코드에 대한 상세 처리
4. **성능 최적화**: 배치 처리 및 비동기 요청 지원

## ✅ 결론

현재 구현이 FortiManager 공식 API 표준을 올바르게 준수하고 있으며, 특히 방화벽 경로 분석 기능이 실제 API를 활용하여 크게 개선되었습니다. 

Mock 모드와 Production 모드를 모두 지원하여 개발부터 운영까지 원활한 사용이 가능하며, JSON-RPC 표준 준수로 안정적인 API 통신이 보장됩니다.