"""
세션 관리 컴포넌트

분석 세션을 관리하고 세션별 데이터를 저장하는 책임을 담당합니다.
"""

import time
import uuid

from src.utils.unified_logger import setup_logger

logger = setup_logger("session_manager")


class SessionManager:
    """분석 세션 관리를 담당하는 클래스"""

    def __init__(self):
        """세션 매니저 초기화"""
        self.logger = logger
        self._sessions = {}  # 세션 ID별 저장 데이터
        self._session_timeout = 3600  # 1시간 (초)

    def create_session(self, user_id=None, session_name=None):
        """
        새 분석 세션 생성

        Args:
            user_id (str, optional): 사용자 ID
            session_name (str, optional): 세션 이름

        Returns:
            str: 생성된 세션 ID
        """
        session_id = str(uuid.uuid4())
        current_time = time.time()

        self._sessions[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "name": session_name or f"Session_{session_id[:8]}",
            "created_at": current_time,
            "last_accessed": current_time,
            "data": {},
            "analysis_history": [],
            "firewall_configs": {},
        }

        self.logger.info(f"새 분석 세션 생성: {session_id}")
        return session_id

    def get_session(self, session_id):
        """
        세션 정보 조회

        Args:
            session_id (str): 세션 ID

        Returns:
            dict or None: 세션 정보
        """
        if session_id not in self._sessions:
            self.logger.warning(f"존재하지 않는 세션: {session_id}")
            return None

        session = self._sessions[session_id]

        # 세션 타임아웃 확인
        if self._is_session_expired(session):
            self.logger.info(f"만료된 세션 제거: {session_id}")
            del self._sessions[session_id]
            return None

        # 마지막 접근 시간 업데이트
        session["last_accessed"] = time.time()
        return session

    def _is_session_expired(self, session):
        """세션 만료 여부 확인"""
        return (time.time() - session["last_accessed"]) > self._session_timeout

    def store_analysis_result(self, session_id, analysis_type, result):
        """
        분석 결과를 세션에 저장

        Args:
            session_id (str): 세션 ID
            analysis_type (str): 분석 유형
            result (dict): 분석 결과

        Returns:
            bool: 저장 성공 여부
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # 분석 이력에 추가
        analysis_record = {"timestamp": time.time(), "type": analysis_type, "result": result}

        session["analysis_history"].append(analysis_record)

        # 최근 100개 기록만 유지
        if len(session["analysis_history"]) > 100:
            session["analysis_history"] = session["analysis_history"][-100:]

        self.logger.info(f"분석 결과 저장: {session_id} - {analysis_type}")
        return True

    def get_analysis_history(self, session_id, analysis_type=None, limit=50):
        """
        분석 이력 조회

        Args:
            session_id (str): 세션 ID
            analysis_type (str, optional): 특정 분석 유형만 조회
            limit (int): 최대 조회 개수

        Returns:
            list: 분석 이력 목록
        """
        session = self.get_session(session_id)
        if not session:
            return []

        history = session["analysis_history"]

        # 특정 분석 유형 필터링
        if analysis_type:
            history = [h for h in history if h["type"] == analysis_type]

        # 최신 순으로 정렬하고 제한
        history = sorted(history, key=lambda x: x["timestamp"], reverse=True)
        return history[:limit]

    def store_firewall_config(self, session_id, firewall_id, config_data):
        """
        방화벽 설정을 세션에 저장

        Args:
            session_id (str): 세션 ID
            firewall_id (str): 방화벽 ID
            config_data (dict): 방화벽 설정 데이터

        Returns:
            bool: 저장 성공 여부
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session["firewall_configs"][firewall_id] = {"data": config_data, "stored_at": time.time()}

        self.logger.info(f"방화벽 설정 저장: {session_id} - {firewall_id}")
        return True

    def get_firewall_config(self, session_id, firewall_id):
        """
        세션에서 방화벽 설정 조회

        Args:
            session_id (str): 세션 ID
            firewall_id (str): 방화벽 ID

        Returns:
            dict or None: 방화벽 설정 데이터
        """
        session = self.get_session(session_id)
        if not session:
            return None

        config = session["firewall_configs"].get(firewall_id)
        return config["data"] if config else None

    def store_session_data(self, session_id, key, value):
        """
        세션에 임의 데이터 저장

        Args:
            session_id (str): 세션 ID
            key (str): 데이터 키
            value: 저장할 값

        Returns:
            bool: 저장 성공 여부
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session["data"][key] = value
        return True

    def get_session_data(self, session_id, key, default=None):
        """
        세션에서 데이터 조회

        Args:
            session_id (str): 세션 ID
            key (str): 데이터 키
            default: 기본값

        Returns:
            데이터 값 또는 기본값
        """
        session = self.get_session(session_id)
        if not session:
            return default

        return session["data"].get(key, default)

    def list_sessions(self, user_id=None):
        """
        세션 목록 조회

        Args:
            user_id (str, optional): 특정 사용자의 세션만 조회

        Returns:
            list: 세션 정보 목록
        """
        sessions = []

        for session_id, session in self._sessions.items():
            # 만료된 세션 제거
            if self._is_session_expired(session):
                continue

            # 사용자 필터링
            if user_id and session.get("user_id") != user_id:
                continue

            sessions.append(
                {
                    "id": session_id,
                    "name": session["name"],
                    "user_id": session["user_id"],
                    "created_at": session["created_at"],
                    "last_accessed": session["last_accessed"],
                    "analysis_count": len(session["analysis_history"]),
                    "firewall_count": len(session["firewall_configs"]),
                }
            )

        # 마지막 접근 시간 순으로 정렬
        sessions.sort(key=lambda x: x["last_accessed"], reverse=True)
        return sessions

    def delete_session(self, session_id):
        """
        세션 삭제

        Args:
            session_id (str): 세션 ID

        Returns:
            bool: 삭제 성공 여부
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            self.logger.info(f"세션 삭제: {session_id}")
            return True

        return False

    def cleanup_expired_sessions(self):
        """만료된 세션들 정리"""
        expired_sessions = []

        for session_id, session in self._sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self._sessions[session_id]
            self.logger.info(f"만료된 세션 정리: {session_id}")

        return len(expired_sessions)

    def get_session_statistics(self):
        """
        세션 통계 정보 반환

        Returns:
            dict: 세션 통계
        """
        # 만료된 세션 정리
        self.cleanup_expired_sessions()

        total_sessions = len(self._sessions)
        total_analyses = sum(len(s["analysis_history"]) for s in self._sessions.values())

        # 사용자별 세션 수
        user_sessions = {}
        for session in self._sessions.values():
            user_id = session.get("user_id", "anonymous")
            user_sessions[user_id] = user_sessions.get(user_id, 0) + 1

        return {
            "total_sessions": total_sessions,
            "total_analyses": total_analyses,
            "user_sessions": user_sessions,
            "average_analyses_per_session": total_analyses / total_sessions if total_sessions > 0 else 0,
        }
