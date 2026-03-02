# 🐳 K8s AI Engine (Py-K8s-Orchestrator)

**실시간 K8s 공식 문서 검색 기반의 AI 아키텍처 자동 설계 및 트러블슈팅 도구**

## 📖 프로젝트 소개
이 프로젝트는 쿠버네티스(Kubernetes) 인프라 구축 및 운영 시 발생하는 진입 장벽을 낮추고, 관리 효율성을 극대화하기 위해 개발된 파이썬 기반의 AI 오케스트레이터입니다. 
단순히 YAML 코드를 생성해 주는 것을 넘어, **최신 K8s 공식 문서를 실시간으로 검색(Search Grounding)**하여 아키텍처를 설계하고, 배포 과정에서 발생하는 **에러 로그를 낚아채어 초보자 눈높이에서 해설해 주는 자동 트러블슈팅 기능**을 갖추고 있습니다.

## ✨ 주요 기능
1. **자연어 기반 인프라 자동 배포 (Dynamic Deployment)**
   * 사용자가 한국어로 원하는 인프라 구조를 입력하면, K8s API(Dynamic Client)를 통해 클러스터에 즉각적으로 배포합니다.
2. **실시간 공식 문서 동기화 (Google Search Grounding)**
   * Gemini 2.5 모델이 `kubernetes.io` 및 `kubeflow.org` 등 최신 공식 문서를 실시간으로 검색한 후 YAML 매니페스트를 작성하여, 기술의 변화(API 버전 업데이트, Deprecated 정책 등)에 능동적으로 대응합니다.
3. **AI 기반 에러 분석 및 트러블슈팅 가이드 제공**
   * K8s API 서버가 거절한 에러(예: `Conflict`, `NotFound`, `Invalid`)를 포착하여, 에러의 발생 원인을 일상적인 비유(예: 공유 문서 편집, 스마트폰 앱 설치 등)를 들어 설명하고, 구체적인 해결 명령어와 공식 문서 출처를 제공합니다.

## 🛠 기술 스택
* **Language:** Python 3.x
* **AI / LLM:** Google Gemini API (gemini-2.5-flash / gemini-2.5-pro)
* **SDK:** `google-genai` (최신 공식 통합 SDK)
* **Infrastructure:** Kubernetes (Rancher Desktop / K3s)
* **Libraries:** `kubernetes-client`, `python-dotenv`, `PyYAML`

## 🚀 시작하기 (Getting Started)

### 1. 사전 준비
* 로컬 쿠버네티스 클러스터 (Rancher Desktop, Minikube 등)
* Google Gemini API Key 발급 (Google AI Studio)

### 2. 설치 및 실행
```bash
# 1. 저장소 클론
git clone [https://github.com/MyosoonHwang/k8s_engine.git](https://github.com/MyosoonHwang/k8s_engine.git)
cd k8s_engine

# 2. 가상 환경 생성 및 진입
python -m venv venv
venv\Scripts\activate  # Windows 환경 기준

# 3. 필수 패키지 설치
pip install google-genai kubernetes python-dotenv pyyaml

# 4. 환경 변수 설정
# 프로젝트 최상단에 .env 파일을 생성하고 아래 내용을 입력합니다.
GEMINI_API_KEY=당신의_API_키_입력

# 5. 프로그램 실행
python main.py