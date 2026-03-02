import os
import yaml
from google import genai
from google.genai import types
from dotenv import load_dotenv
from kubernetes import config, dynamic
from kubernetes.client import api_client
from kubernetes.client.rest import ApiException

# 1. 환경 변수 로드 (.env 파일에서 API 키 읽기)
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError("🚨 API 키를 찾을 수 없습니다. .env 파일에 GEMINI_API_KEY가 설정되어 있는지 확인하세요.")

# 🌟 핵심 1: 구글의 최신 공식 SDK 클라이언트로 초기화
client = genai.Client(api_key=api_key)

def select_gemini_model():
    # API 호출 에러를 방지하기 위해 가장 안정적인 모델만 엄선
    models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
    
    print("🔍 사용 가능한 Gemini 모델을 준비했습니다.")
    print("\n[🤖 지원되는 Gemini 모델 목록]")
    for i, m in enumerate(models):
        print(f"{i + 1}. {m}")
        
    while True:
        try:
            choice = int(input("\n사용할 모델의 번호를 선택하세요: "))
            if 1 <= choice <= len(models):
                selected_model = models[choice - 1]
                print(f"✅ '{selected_model}' 모델이 선택되었습니다.\n")
                return selected_model
            else:
                print("⚠️ 목록에 있는 올바른 번호를 입력해주세요.")
        except ValueError:
            print("⚠️ 숫자를 입력해주세요.")

def generate_yaml_with_gemini(user_input, model_name):
    print(f"🧠 {model_name} 모델이 최신 K8s 공식 문서를 실시간으로 검색하여 아키텍처를 설계 중입니다...")
    
    prompt = f"""
    너는 쿠버네티스(Kubernetes) 수석 시스템 엔지니어야.
    사용자의 요청을 분석하기 전에, 반드시 'kubernetes.io' 공식 문서를 실시간으로 검색하여 
    가장 최신의 권장 사항(Best Practices)과 API 버전을 확인해.
    
    [규칙]
    1. 검색한 최신 공식 문서의 내용을 바탕으로 마크다운 코드 블록(```yaml ... ```) 안에 오직 YAML 코드만 작성할 것.
    2. 부연 설명이나 인사말은 절대 포함하지 말 것.
    3. 여러 개의 리소스가 필요하다면 '---' 로 구분할 것.
    
    사용자 요청: {user_input}
    """
    
    # 🌟 핵심 2: 최신 SDK의 문법을 사용한 완벽한 Google Search Grounding
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.1 # 인프라 코드이므로 온도를 낮춰 정확도 극대화
        )
    )
    
    yaml_text = response.text.strip()
    
    # 마크다운 포맷 깔끔하게 제거
    if yaml_text.startswith("```yaml"):
        yaml_text = yaml_text[7:].strip()
    elif yaml_text.startswith("```"):
        yaml_text = yaml_text[3:].strip()
        
    if yaml_text.endswith("```"):
        yaml_text = yaml_text[:-3].strip()
        
    return yaml_text

def analyze_error_with_gemini(error_message, resource_kind, resource_name, model_name):
    print(f"\n[🚨 에러 감지!] {model_name} 모델이 실시간 검색을 통해 원인을 분석하고 해결책을 찾고 있습니다...")
    
    prompt = f"""
    너는 쿠버네티스를 처음 배우는 초보자를 돕는 친절한 멘토이자 전문가야.
    사용자가 쿠버네티스에 '{resource_kind}' 리소스('{resource_name}')를 배포하려다가 다음 에러가 발생했어.
    
    [에러 메시지]
    {error_message}
    
    [요청 사항]
    1. 먼저 쿠버네티스 공식 문서(kubernetes.io)를 실시간으로 검색하여 이 에러의 정확한 최신 원인을 파악해.
    2. 이 에러가 왜 발생했는지 초보자가 이해하기 쉬운 비유를 들어 한국어로 원인을 설명해 줘.
    3. 이 문제를 해결하려면 사용자가 어떤 조치를 취해야 하는지 구체적인 해결책을 1~2가지 제시해 줘.
    4. 마지막에 반드시 참고한 쿠버네티스 공식 문서의 출처(URL)를 명확하게 제공해 줘.
    """
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    
    print("\n==================================================")
    print("💡 [AI 트러블슈팅 해설 및 가이드]")
    print(response.text.strip())
    print("==================================================\n")

def deploy_to_kubernetes(yaml_string, model_name):
    config.load_kube_config()
    k8s_client = dynamic.DynamicClient(api_client.ApiClient())
    
    print("\n[📝 최신 공식 문서가 반영된 K8s 아키텍처]")
    print(yaml_string)
    
    manifests = yaml.safe_load_all(yaml_string)
    
    print("\n🚀 클러스터에 동적 배포를 시작합니다...")
    for manifest in manifests:
        if not manifest:
            continue
            
        api_version = manifest.get("apiVersion")
        kind = manifest.get("kind")
        name = manifest.get("metadata", {}).get("name", "unknown")
        
        try:
            resource_api = k8s_client.resources.get(api_version=api_version, kind=kind)
            resource_api.create(body=manifest, namespace="default")
            print(f"✅ 배포 성공: {kind} '{name}'가 생성되었습니다.")
            
        except ApiException as e:
            # 쿠버네티스 API가 뱉어내는 명확한 에러 캐치
            analyze_error_with_gemini(e.reason or str(e), kind, name, model_name)
        except Exception as e:
            # 기타 파이썬 로컬 에러 캐치
            analyze_error_with_gemini(str(e), kind, name, model_name)

if __name__ == '__main__':
    print("=== 🐳 실시간 K8s 동기화 오케스트레이터 및 트러블슈팅 ===")
    
    selected_model = select_gemini_model()
    user_request = input("구축하고 싶은 쿠버네티스 인프라를 설명해주세요: ")
    
    try:
        generated_yaml = generate_yaml_with_gemini(user_request, selected_model)
        deploy_to_kubernetes(generated_yaml, selected_model)
    except Exception as e:
        print(f"\n시스템 심각한 오류: {e}")