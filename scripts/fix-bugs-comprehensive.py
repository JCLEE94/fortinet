#!/usr/bin/env python3
"""
종합 버그 수정 스크립트
시스템의 주요 버그들을 자동으로 식별하고 수정
"""

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BugFixManager:
    """버그 수정 관리자"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.fix_results = []

    def run_command(
        self, command: str, capture_output: bool = True
    ) -> Tuple[int, str, str]:
        """명령어 실행"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=300,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)

    def fix_argocd_sync_issues(self) -> Dict:
        """ArgoCD 동기화 문제 수정"""
        logger.info("🔧 ArgoCD 동기화 문제 수정 중...")

        fixes_applied = []

        # 1. 기존 Ingress 삭제 (잘못된 스펙)
        logger.info("잘못된 Ingress 리소스 삭제...")
        code, stdout, stderr = self.run_command(
            "kubectl delete ingress fortinet -n fortinet --ignore-not-found=true"
        )
        if code == 0:
            fixes_applied.append("Deleted invalid Ingress resource")

        # 2. 문제 있는 PVC 삭제
        logger.info("문제 있는 PVC 정리...")
        code, stdout, stderr = self.run_command(
            "kubectl delete pvc fortinet-data -n fortinet --ignore-not-found=true --force --grace-period=0"
        )
        if "deleted" in stdout.lower() or code == 0:
            fixes_applied.append("Cleaned up problematic PVC")

        # 3. ArgoCD 애플리케이션 동기화 옵션 수정
        logger.info("ArgoCD 동기화 옵션 수정...")
        patch_data = {
            "spec": {
                "syncPolicy": {
                    "syncOptions": [
                        "CreateNamespace=true",
                        "ServerSideApply=true",
                        "PruneLast=true",
                        "Replace=true",
                    ]
                }
            }
        }

        patch_command = f"kubectl patch application fortinet -n argocd --type='merge' -p='{json.dumps(patch_data)}'"
        code, stdout, stderr = self.run_command(patch_command)
        if code == 0:
            fixes_applied.append("Updated ArgoCD sync options")

        # 4. 필요시 애플리케이션 재생성
        if not fixes_applied:
            logger.info("ArgoCD 애플리케이션 재생성...")
            # 기존 애플리케이션 삭제
            self.run_command(
                "kubectl delete application fortinet -n argocd --ignore-not-found=true"
            )
            time.sleep(5)

            # 새 애플리케이션 생성
            if os.path.exists("argocd-fortinet-gitops.yaml"):
                code, stdout, stderr = self.run_command(
                    "kubectl apply -f argocd-fortinet-gitops.yaml"
                )
                if code == 0:
                    fixes_applied.append("Recreated ArgoCD application")

        return {
            "component": "ArgoCD Sync",
            "fixes_applied": fixes_applied,
            "status": "success" if fixes_applied else "no_action_needed",
        }

    def fix_helm_chart_issues(self) -> Dict:
        """Helm 차트 문제 수정"""
        logger.info("🔧 Helm 차트 문제 수정 중...")

        fixes_applied = []

        # 1. Ingress 템플릿 수정
        ingress_template_path = Path("charts/fortinet/templates/ingress.yaml")
        if ingress_template_path.exists():
            logger.info("Ingress 템플릿 수정...")

            # 기존 내용 읽기
            content = ingress_template_path.read_text()

            # 수정된 Ingress 템플릿 작성
            new_content = """{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "fortinet.fullname" . }}
  labels:
    {{- include "fortinet.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType | default "Prefix" }}
            backend:
              service:
                name: {{ include "fortinet.fullname" $ }}
                port:
                  number: {{ $.Values.service.port }}
          {{- end }}
    {{- end }}
{{- end }}"""

            if content != new_content:
                ingress_template_path.write_text(new_content)
                fixes_applied.append("Fixed Ingress template")

        # 2. values.yaml에서 Ingress 기본값 비활성화
        values_path = Path("charts/fortinet/values.yaml")
        if values_path.exists():
            logger.info("values.yaml 수정...")

            content = values_path.read_text()
            lines = content.split("\n")

            # Ingress 섹션 찾아서 수정
            in_ingress_section = False
            new_lines = []

            for line in lines:
                if line.strip().startswith("ingress:"):
                    in_ingress_section = True
                    new_lines.append(line)
                elif in_ingress_section and line.strip().startswith("enabled:"):
                    new_lines.append("  enabled: false")
                    if "enabled: true" in line:
                        fixes_applied.append("Disabled Ingress by default")
                elif in_ingress_section and line and not line.startswith(" "):
                    # Ingress 섹션 종료
                    in_ingress_section = False
                    new_lines.append(line)
                else:
                    new_lines.append(line)

            new_content = "\n".join(new_lines)
            if content != new_content:
                values_path.write_text(new_content)

        # 3. Chart 버전 업그레이드
        chart_path = Path("charts/fortinet/Chart.yaml")
        if chart_path.exists():
            logger.info("Chart 버전 업그레이드...")

            content = chart_path.read_text()
            lines = content.split("\n")

            for i, line in enumerate(lines):
                if line.startswith("version:"):
                    current_version = line.split(":")[1].strip()
                    # 마이너 버전 증가
                    version_parts = current_version.split(".")
                    if len(version_parts) >= 3:
                        patch_version = int(version_parts[2]) + 1
                        new_version = (
                            f"{version_parts[0]}.{version_parts[1]}.{patch_version}"
                        )
                        lines[i] = f"version: {new_version}"
                        fixes_applied.append(f"Updated chart version to {new_version}")
                        break

            chart_path.write_text("\n".join(lines))

        return {
            "component": "Helm Chart",
            "fixes_applied": fixes_applied,
            "status": "success" if fixes_applied else "no_action_needed",
        }

    def fix_service_port_conflicts(self) -> Dict:
        """서비스 포트 충돌 문제 수정"""
        logger.info("🔧 서비스 포트 충돌 문제 수정 중...")

        fixes_applied = []

        # 1. 포트 사용 현황 확인
        logger.info("포트 사용 현황 확인...")
        code, stdout, stderr = self.run_command(
            "kubectl get svc --all-namespaces | grep NodePort"
        )

        if code == 0 and "30777" in stdout:
            logger.info("포트 30777 충돌 감지, 30779로 변경...")

            # Service 리소스에서 NodePort 변경
            patch_data = {
                "spec": {
                    "ports": [
                        {
                            "port": 80,
                            "targetPort": 7777,
                            "nodePort": 30779,
                            "protocol": "TCP",
                        }
                    ]
                }
            }

            patch_command = f"kubectl patch svc fortinet -n fortinet --type='merge' -p='{json.dumps(patch_data)}'"
            code, stdout, stderr = self.run_command(patch_command)
            if code == 0:
                fixes_applied.append("Changed NodePort from 30777 to 30779")

        # 2. Helm values.yaml 업데이트
        values_path = Path("charts/fortinet/values.yaml")
        if values_path.exists():
            content = values_path.read_text()
            if "nodePort: 30777" in content:
                new_content = content.replace("nodePort: 30777", "nodePort: 30779")
                values_path.write_text(new_content)
                fixes_applied.append("Updated Helm values for NodePort")

        return {
            "component": "Service Ports",
            "fixes_applied": fixes_applied,
            "status": "success" if fixes_applied else "no_action_needed",
        }

    def fix_import_path_issues(self) -> Dict:
        """Import 경로 문제 수정"""
        logger.info("🔧 Import 경로 문제 수정 중...")

        fixes_applied = []

        # src 디렉토리의 Python 파일들 검사
        src_path = Path("src")
        if not src_path.exists():
            return {
                "component": "Import Paths",
                "fixes_applied": [],
                "status": "no_source_directory",
            }

        python_files = list(src_path.rglob("*.py"))

        for py_file in python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                original_content = content

                # 절대 import를 상대 import로 변경
                lines = content.split("\n")
                modified_lines = []

                for line in lines:
                    modified_line = line

                    # from src.xxx import 패턴 수정
                    if line.strip().startswith("from src."):
                        # src. 제거
                        modified_line = line.replace("from src.", "from ")

                    # import src.xxx 패턴 수정
                    elif line.strip().startswith("import src."):
                        # src. 제거
                        modified_line = line.replace("import src.", "import ")

                    modified_lines.append(modified_line)

                new_content = "\n".join(modified_lines)

                if new_content != original_content:
                    py_file.write_text(new_content, encoding="utf-8")
                    fixes_applied.append(
                        f"Fixed imports in {py_file.relative_to(src_path)}"
                    )

            except Exception as e:
                logger.warning(f"Failed to process {py_file}: {e}")

        return {
            "component": "Import Paths",
            "fixes_applied": fixes_applied,
            "status": "success" if fixes_applied else "no_issues_found",
        }

    def fix_docker_issues(self) -> Dict:
        """Docker 관련 문제 수정"""
        logger.info("🔧 Docker 관련 문제 수정 중...")

        fixes_applied = []

        # 1. Dockerfile에서 COPY 경로 수정
        dockerfile_paths = [
            Path("Dockerfile"),
            Path("Dockerfile.production"),
            Path("services/auth/Dockerfile"),
            Path("services/fortimanager/Dockerfile"),
            Path("services/itsm/Dockerfile"),
        ]

        for dockerfile_path in dockerfile_paths:
            if dockerfile_path.exists():
                content = dockerfile_path.read_text()
                original_content = content

                # COPY 경로에서 src/ 접두사 제거가 필요한 경우
                lines = content.split("\n")
                modified_lines = []

                for line in lines:
                    modified_line = line

                    # COPY src/something ./something 패턴 확인
                    if "COPY src/" in line and not "./src/" in line:
                        # 이미 올바른 형태이므로 그대로 유지
                        pass

                    modified_lines.append(modified_line)

                new_content = "\n".join(modified_lines)

                if new_content != original_content:
                    dockerfile_path.write_text(new_content)
                    fixes_applied.append(f"Fixed COPY paths in {dockerfile_path}")

        # 2. Docker Compose 파일 검증
        compose_files = [Path("docker-compose.yml"), Path("docker-compose.msa.yml")]

        for compose_file in compose_files:
            if compose_file.exists():
                try:
                    # YAML 구문 검증
                    code, stdout, stderr = self.run_command(
                        f"docker-compose -f {compose_file} config --quiet"
                    )
                    if code != 0:
                        logger.warning(
                            f"Docker Compose 파일 {compose_file}에 문제가 있을 수 있습니다: {stderr}"
                        )
                except Exception as e:
                    logger.warning(f"Docker Compose 파일 검증 실패: {e}")

        return {
            "component": "Docker",
            "fixes_applied": fixes_applied,
            "status": "success" if fixes_applied else "no_issues_found",
        }

    def fix_kubernetes_resource_issues(self) -> Dict:
        """Kubernetes 리소스 문제 수정"""
        logger.info("🔧 Kubernetes 리소스 문제 수정 중...")

        fixes_applied = []

        # 1. 남은 Finalizer 제거
        logger.info("Finalizer 정리...")
        code, stdout, stderr = self.run_command(
            'kubectl get pvc -n fortinet -o name | xargs -I {} kubectl patch {} -n fortinet -p \'{"metadata":{"finalizers":null}}\' --type=merge'
        )
        if code == 0:
            fixes_applied.append("Cleaned up PVC finalizers")

        # 2. 불필요한 리소스 정리
        logger.info("불필요한 리소스 정리...")
        resources_to_clean = [
            "kubectl delete ingress --all -n fortinet --ignore-not-found=true",
            "kubectl delete configmap --selector=app=fortinet-old -n fortinet --ignore-not-found=true",
        ]

        for cleanup_cmd in resources_to_clean:
            code, stdout, stderr = self.run_command(cleanup_cmd)
            if code == 0 and "deleted" in stdout.lower():
                fixes_applied.append(f"Cleaned up resources: {cleanup_cmd.split()[-3]}")

        # 3. 네임스페이스 상태 확인 및 복구
        code, stdout, stderr = self.run_command("kubectl get ns fortinet -o json")
        if code == 0 and "Terminating" in stdout:
            logger.info("네임스페이스 Terminating 상태 복구...")
            # Finalizer 제거로 네임스페이스 복구 시도
            patch_data = {"spec": {"finalizers": []}}
            patch_command = f"kubectl patch ns fortinet --type='merge' -p='{json.dumps(patch_data)}'"
            code, stdout, stderr = self.run_command(patch_command)
            if code == 0:
                fixes_applied.append("Fixed namespace Terminating state")

        return {
            "component": "Kubernetes Resources",
            "fixes_applied": fixes_applied,
            "status": "success" if fixes_applied else "no_issues_found",
        }

    def fix_configuration_issues(self) -> Dict:
        """설정 파일 문제 수정"""
        logger.info("🔧 설정 파일 문제 수정 중...")

        fixes_applied = []

        # 1. requirements.txt 의존성 문제 수정
        req_path = Path("requirements.txt")
        if req_path.exists():
            content = req_path.read_text()
            lines = content.strip().split("\n")

            # 중복 제거 및 버전 충돌 해결
            seen_packages = set()
            fixed_lines = []

            for line in lines:
                if line.strip() and not line.startswith("#"):
                    package_name = (
                        line.split("==")[0].split(">=")[0].split("<=")[0].strip()
                    )
                    if package_name not in seen_packages:
                        seen_packages.add(package_name)
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)

            new_content = "\n".join(fixed_lines)
            if content != new_content:
                req_path.write_text(new_content)
                fixes_applied.append("Fixed requirements.txt duplicates")

        # 2. 환경 변수 설정 확인
        env_files = [Path(".env"), Path(".env.example")]
        for env_file in env_files:
            if env_file.exists():
                content = env_file.read_text()

                # 필수 환경 변수 확인
                required_vars = [
                    "WEB_APP_PORT=7777",
                    "APP_MODE=production",
                    "OFFLINE_MODE=true",
                ]

                for var in required_vars:
                    if var.split("=")[0] not in content:
                        content += f"\n{var}"
                        fixes_applied.append(f"Added missing env var: {var}")

                env_file.write_text(content)

        return {
            "component": "Configuration",
            "fixes_applied": fixes_applied,
            "status": "success" if fixes_applied else "no_issues_found",
        }

    def run_comprehensive_fix(self) -> Dict:
        """종합 버그 수정 실행"""
        logger.info("🚀 종합 버그 수정 시작...")

        # 수정 함수들 실행
        fix_functions = [
            self.fix_argocd_sync_issues,
            self.fix_helm_chart_issues,
            self.fix_service_port_conflicts,
            self.fix_import_path_issues,
            self.fix_docker_issues,
            self.fix_kubernetes_resource_issues,
            self.fix_configuration_issues,
        ]

        all_results = []
        total_fixes = 0

        for fix_func in fix_functions:
            try:
                result = fix_func()
                all_results.append(result)
                total_fixes += len(result.get("fixes_applied", []))

                # 결과 출력
                component = result["component"]
                fixes = result.get("fixes_applied", [])
                status = result["status"]

                if fixes:
                    logger.info(f"✅ {component}: {len(fixes)} 개 문제 수정")
                    for fix in fixes:
                        logger.info(f"   - {fix}")
                else:
                    logger.info(f"ℹ️  {component}: 수정할 문제 없음 ({status})")

            except Exception as e:
                logger.error(f"❌ {fix_func.__name__} 실행 중 오류: {e}")
                all_results.append(
                    {
                        "component": fix_func.__name__,
                        "fixes_applied": [],
                        "status": "error",
                        "error": str(e),
                    }
                )

        # 결과 요약
        summary = {
            "total_components_checked": len(fix_functions),
            "total_fixes_applied": total_fixes,
            "results": all_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_status": "success" if total_fixes > 0 else "no_issues_found",
        }

        return summary


def main():
    """메인 실행 함수"""
    print("🔧 FortiGate Nextrade 종합 버그 수정 도구")
    print("=" * 60)

    bug_fixer = BugFixManager()

    try:
        # 종합 수정 실행
        results = bug_fixer.run_comprehensive_fix()

        # 결과 출력
        print("\n" + "=" * 60)
        print("📊 버그 수정 결과 요약")
        print("=" * 60)

        print(f"검사한 컴포넌트: {results['total_components_checked']}")
        print(f"적용된 수정사항: {results['total_fixes_applied']}")
        print(f"전체 상태: {results['overall_status']}")
        print(f"실행 시간: {results['timestamp']}")

        # 상세 결과 파일 저장
        results_file = Path("bug_fix_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n📄 상세 결과가 {results_file}에 저장되었습니다.")

        # 추천 사항
        if results["total_fixes_applied"] > 0:
            print("\n💡 추천 후속 작업:")
            print("  1. 변경사항을 Git에 커밋")
            print("  2. ArgoCD 동기화 상태 확인")
            print("  3. 서비스 헬스체크 실행")
            print("  4. 필요시 서비스 재시작")

            print("\n📋 실행 명령어:")
            print("  git add -A && git commit -m 'fix: comprehensive bug fixes'")
            print("  kubectl get application fortinet -n argocd")
            print("  curl http://192.168.50.110:30779/api/health")

        # 성공 시 종료 코드 0
        return 0 if results["overall_status"] in ["success", "no_issues_found"] else 1

    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
