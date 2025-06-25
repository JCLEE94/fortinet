"""
FortiGate Nextrade 설정 모듈

통합 설정 시스템:
- 환경변수 우선
- JSON 설정 파일 보조
- 타입 안전성 보장
- 환경별 설정 전환
- 하드코딩 값 제거 및 중앙화
"""

from .unified_settings import unified_settings as settings, UnifiedSettings

# 기존 호환성을 위한 export
__all__ = ['settings', 'UnifiedSettings']

# 설정 검증
if not hasattr(settings, 'app_mode'):
    raise ImportError("설정 시스템이 올바르게 초기화되지 않았습니다.")

# 추가 설정 모듈 임포트 (하드코딩 제거를 위해 추가)
try:
    from .network import *
    from .services import *
    from .ports import *
    from .paths import *
    from .limits import *
except ImportError:
    # 새 설정 모듈이 없는 경우 무시 (기존 호환성)
    pass