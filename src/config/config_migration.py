#!/usr/bin/env python3
"""
설정 시스템 마이그레이션 도구
기존 설정을 새로운 통합 설정 시스템으로 마이그레이션합니다.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from src.config.unified_settings import UnifiedSettings, unified_settings


class ConfigMigration:
    """설정 마이그레이션 클래스"""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.backup_dir = self.base_dir / "config_backup"
        self.legacy_settings_file = self.base_dir / "src" / "config" / "settings.py"
        self.old_config_file = self.base_dir / "data" / "config.json"
        self.default_config_file = self.base_dir / "data" / "default_config.json"

    def backup_existing_configs(self):
        """기존 설정 파일들을 백업"""
        print("🔄 기존 설정 파일 백업 중...")

        self.backup_dir.mkdir(exist_ok=True)

        files_to_backup = [
            self.legacy_settings_file,
            self.old_config_file,
            self.default_config_file,
        ]

        for file_path in files_to_backup:
            if file_path.exists():
                backup_path = self.backup_dir / f"{file_path.name}.backup"
                backup_path.write_text(file_path.read_text(), encoding="utf-8")
                print(f"  ✅ {file_path.name} → {backup_path}")

    def validate_migration(self) -> bool:
        """마이그레이션 유효성 검증"""
        print("\n🔍 마이그레이션 검증 중...")

        try:
            # 새로운 설정 시스템 로드 테스트
            settings = UnifiedSettings()

            # 기본 설정 확인
            checks = [
                ("APP_MODE 설정", settings.app_mode == "production"),
                ("FortiManager 설정", hasattr(settings, "fortimanager")),
                ("FortiGate 설정", hasattr(settings, "fortigate")),
                ("웹앱 설정", hasattr(settings, "webapp")),
                ("JSON 저장 테스트", self._test_json_save(settings)),
            ]

            all_passed = True
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"  {status} {check_name}")
                if not result:
                    all_passed = False

            return all_passed

        except Exception as e:
            print(f"  ❌ 설정 로드 실패: {e}")
            return False

    def _test_json_save(self, settings: UnifiedSettings) -> bool:
        """JSON 저장 테스트"""
        try:
            settings.save_to_json()
            return True
        except Exception:
            return False

    def update_import_statements(self):
        """기존 코드의 import 문 업데이트"""
        print("\n🔄 Import 문 업데이트 중...")

        # 업데이트할 파일들
        files_to_update = [
            self.base_dir / "src" / "web_app.py",
            self.base_dir / "src" / "main.py",
            self.base_dir / "src" / "routes" / "api_routes.py",
            self.base_dir / "src" / "routes" / "main_routes.py",
            self.base_dir / "src" / "routes" / "fortimanager_routes.py",
        ]

        old_import = "from src.config.settings import settings"
        new_import = (
            "from src.config.unified_settings import unified_settings as settings"
        )

        for file_path in files_to_update:
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if old_import in content:
                        updated_content = content.replace(old_import, new_import)
                        file_path.write_text(updated_content, encoding="utf-8")
                        print(f"  ✅ {file_path.relative_to(self.base_dir)}")
                except Exception as e:
                    print(f"  ❌ {file_path.relative_to(self.base_dir)}: {e}")

    def generate_migration_report(self) -> Dict[str, Any]:
        """마이그레이션 보고서 생성"""
        settings = unified_settings

        report = {
            "migration_status": "completed",
            "timestamp": str(Path(__file__).stat().st_mtime),
            "current_settings": {
                "app_mode": settings.app_mode,
                "offline_mode": settings.offline_mode,
                "enabled_services": {
                    "fortimanager": settings.is_service_enabled("fortimanager"),
                    "fortigate": settings.is_service_enabled("fortigate"),
                    "fortianalyzer": settings.is_service_enabled("fortianalyzer"),
                    "redis": settings.redis.enabled,
                },
                "webapp_config": {
                    "port": settings.webapp.port,
                    "debug": settings.webapp.debug,
                },
            },
            "configuration_priorities": {
                "1": "환경변수 (.env)",
                "2": "JSON 설정 파일 (data/config.json)",
                "3": "기본값 (코드에 정의된 기본값)",
            },
            "migration_benefits": [
                "설정 우선순위 명확화",
                "중복 설정 제거",
                "일관된 필드명 사용",
                "환경별 설정 전환 자동화",
                "설정 유효성 검증",
                "타입 안전성 보장",
            ],
        }

        return report

    def run_migration(self):
        """전체 마이그레이션 실행"""
        print("🚀 FortiGate Nextrade 설정 시스템 마이그레이션 시작\n")

        # 1. 기존 설정 백업
        self.backup_existing_configs()

        # 2. 새로운 설정 시스템 로드 및 검증
        if not self.validate_migration():
            print("\n❌ 마이그레이션 검증 실패. 백업된 파일을 확인하세요.")
            return False

        # 3. Import 문 업데이트
        self.update_import_statements()

        # 4. 마이그레이션 보고서 생성
        report = self.generate_migration_report()

        print("\n" + "=" * 50)
        print("✅ 설정 시스템 마이그레이션 완료!")
        print("=" * 50)
        print(f"📁 백업 디렉토리: {self.backup_dir}")
        print(f"🔧 현재 모드: {report['current_settings']['app_mode']}")
        print(f"🌐 웹앱 포트: {report['current_settings']['webapp_config']['port']}")
        print(
            f"📊 활성화된 서비스: {list(k for k, v in report['current_settings']['enabled_services'].items() if v)}"
        )

        return True


def main():
    """메인 함수"""
    if len(sys.argv) > 1 and sys.argv[1] == "--validate-only":
        # 검증만 실행
        migration = ConfigMigration()
        if migration.validate_migration():
            print("✅ 설정 시스템이 올바르게 작동합니다.")
            return 0
        else:
            print("❌ 설정 시스템에 문제가 있습니다.")
            return 1
    else:
        # 전체 마이그레이션 실행
        migration = ConfigMigration()
        if migration.run_migration():
            return 0
        else:
            return 1


if __name__ == "__main__":
    sys.exit(main())
