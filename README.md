# FortiGate Nextrade

FortiGate 방화벽과 FortiManager를 위한 종합적인 네트워크 모니터링 및 분석 플랫폼입니다. 폐쇄망(오프라인) 환경에서 완전히 동작하도록 설계되었습니다.

## 🚀 주요 기능

- **실시간 모니터링**: 네트워크 트래픽, CPU, 메모리 사용률 모니터링
- **정책 분석**: 방화벽 정책 분석 및 패킷 경로 추적  
- **토폴로지 시각화**: 네트워크 구조 시각화
- **ITSM 연동**: 방화벽 정책 요청 및 티켓 관리
- **원격 배포**: 자동화된 다중 서버 배포 시스템
- **오프라인 모드**: 인터넷 연결 없이 동작하는 완전 오프라인 환경

## 📋 시스템 요구사항

### 최소 요구사항
- **OS**: Linux (Ubuntu 18.04+, CentOS 7+) 또는 Windows 10+
- **RAM**: 4GB 이상
- **Storage**: 20GB 이상 여유 공간  
- **Docker**: 20.10+ 또는 Podman 3.0+

### 권장 사양
- **OS**: Ubuntu 20.04 LTS 또는 CentOS 8
- **RAM**: 8GB 이상
- **Storage**: 50GB 이상 SSD
- **CPU**: 4 Core 이상

## 다운로드

### Git LFS를 사용한 다운로드
```bash
# Git LFS 설치 (최초 1회)
sudo apt-get install git-lfs  # Ubuntu/Debian
sudo yum install git-lfs       # RHEL/CentOS

# Git LFS 초기화 및 다운로드
git lfs install
git clone -b offline-deployment gitlab:nextrade/fortinet.git
```

### Git LFS 없이 다운로드
```bash
# 1. 코드만 다운로드
GIT_LFS_SKIP_SMUDGE=1 git clone -b offline-deployment gitlab:nextrade/fortinet.git

# 2. 설치 파일 직접 다운로드
cd fortinet
wget http://192.168.50.215:22080/nextrade/fortinet/-/raw/offline-deployment/fortinet-offline-deploy-20250604_182511.tar.gz
```

## 🚀 배포 방법

### 로컬 배포
```bash
# 기본 배포
./deploy.sh

# 테스트 모드
APP_MODE=test ./deploy.sh
```

### 원격 배포 (다중 서버)
```bash
# 1. Registry 설정
./setup-registry.sh local --port 5000

# 2. SSH 환경 설정
./setup-ssh.sh generate-key
./setup-ssh.sh setup-all --servers "server1,server2"

# 3. 원격 배포 실행
./remote-deploy.sh production --registry-push --parallel

# 4. 배포 테스트
./test-deploy.sh
```

### 환경별 배포
- **Development**: `./remote-deploy.sh development`
- **Staging**: `./remote-deploy.sh staging --registry-push`  
- **Production**: `./remote-deploy.sh production --registry-push --parallel`

## 빠른 시작

### Linux/Unix
```bash
# 1. 설치 (최초 1회) - 필수!
./fortinet-installer.sh install

# 2. FortiManager 연결 설정 (선택사항)
./fortinet-installer.sh config

# 3. 상태 확인
./fortinet-installer.sh status
```

### Windows PowerShell
```powershell
# 1. 실행 정책 설정 (최초 1회)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. 설치 (최초 1회) - 필수!
.\fortinet-installer.ps1 install

# 3. FortiManager 연결 설정 (선택사항)
.\fortinet-installer.ps1 config

# 4. 상태 확인
.\fortinet-installer.ps1 status
```

### ⚠️ 중요 사항
- **첫 번째로 반드시 `install` 명령을 실행하세요**
- 설치하지 않고 다른 명령을 실행하면 오류가 발생합니다
- tar 파일(`fortinet-offline-deploy-*.tar.gz`)이 같은 디렉토리에 있어야 합니다

## 접속 정보
- **URL**: http://localhost:7777
- **모드**: 운영 모드 (production)
- **포트**: 7777

## 주요 기능
✅ FortiGate 방화벽 정책 분석  
✅ 네트워크 토폴로지 시각화  
✅ 실시간 모니터링 대시보드  
✅ FortiManager API 통합  
✅ 경로 분석 및 추적  
❌ 패킷 스니퍼 (미구현)  
❌ ITSM 연동 (미구현)  

## 시스템 요구사항
- Docker 또는 Podman
- 4GB 이상 RAM
- 10GB 이상 디스크 공간
- Linux/Unix 또는 Windows 10 이상

### Windows 추가 요구사항
다음 중 하나가 필요합니다:
- **Windows 10 (1903 이상)** 또는 **Windows 11** (내장 tar 포함)
- **7-Zip** (https://www.7-zip.org/) - 구버전 Windows용
- 수동 압축 해제 (위 도구가 없는 경우)

## 관리 명령어

### Linux/Unix
```bash
./fortinet-installer.sh start     # 서비스 시작
./fortinet-installer.sh stop      # 서비스 중지
./fortinet-installer.sh restart   # 서비스 재시작
./fortinet-installer.sh status    # 상태 확인
./fortinet-installer.sh logs      # 로그 확인
./fortinet-installer.sh config    # 설정 변경
./fortinet-installer.sh uninstall # 제거
```

### Windows PowerShell
```powershell
.\fortinet-installer.ps1 start     # 서비스 시작
.\fortinet-installer.ps1 stop      # 서비스 중지
.\fortinet-installer.ps1 restart   # 서비스 재시작
.\fortinet-installer.ps1 status    # 상태 확인
.\fortinet-installer.ps1 logs      # 로그 확인
.\fortinet-installer.ps1 config    # 설정 변경
.\fortinet-installer.ps1 uninstall # 제거
```

## 문제 해결

### "tar 파일을 찾을 수 없습니다" 오류
```bash
# 현재 디렉토리에 tar 파일이 있는지 확인
ls -la *.tar.gz

# 스크립트가 찾는 파일명 확인  
./fortinet-installer.sh install  # 디버깅 정보가 표시됨
```

### Windows "tar 명령어를 찾을 수 없습니다" 오류
**해결 방법 (우선순위 순):**

1. **Windows 10/11 업데이트**
   - Windows 10 (1903 이상) 또는 Windows 11로 업데이트
   - 내장 tar 명령어 자동 사용

2. **7-Zip 설치**
   ```powershell
   # 7-Zip 다운로드 및 설치: https://www.7-zip.org/
   # 설치 후 자동으로 감지됨
   ```

3. **수동 압축 해제**
   ```powershell
   # 1. fortinet-offline-deploy-*.tar.gz 파일을 수동으로 압축 해제
   # 2. 압축 해제된 파일들을 스크립트와 같은 폴더에 복사
   # 3. 다시 설치 실행
   .\fortinet-installer.ps1 install
   ```

### PowerShell 실행 정책 오류
```powershell
# 관리자 권한으로 실행
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Docker Desktop 확인
```bash
docker version
docker ps
```

### 포트 충돌
기본 포트 7777이 사용 중인 경우, 설치 스크립트 내 PORT 변수를 수정하세요.

### "docker-compose.yml을 찾을 수 없습니다" 오류
이 오류는 `install` 명령을 먼저 실행하지 않았을 때 발생합니다.
```bash
# 해결 방법: 설치부터 실행
./fortinet-installer.sh install
```

## 라이선스
© 2025 Nextrade. All rights reserved.