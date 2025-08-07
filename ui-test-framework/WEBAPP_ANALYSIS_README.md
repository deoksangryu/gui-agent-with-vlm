# 🌐 웹 애플리케이션 전문 분석 시스템

Qwen2VL 기반의 웹 애플리케이션 스크린샷 전문 분석 도구입니다. 사용자의 보충설명을 통해 더욱 정확하고 맥락적인 분석을 제공합니다.

## ✨ 주요 특징

- **웹앱 특화**: 웹 애플리케이션 UI/UX에 특화된 전문 분석
- **사용자 맥락 통합**: 보충설명을 통한 정확한 분석
- **다양한 분석 모드**: 빠른/종합/상세/워크플로우/접근성/디자인 시스템 분석
- **API 형태 제공**: 다른 프로젝트에서 쉽게 활용 가능
- **배치 처리 지원**: 여러 이미지 일괄 분석

## 📁 파일 구조

```
ui-test/
├── qwen2vl_webapp_analyzer.py    # 메인 웹앱 분석기 (대화형)
├── webapp_analysis_api.py        # API 스타일 인터페이스
└── WEBAPP_ANALYSIS_README.md     # 이 파일
```

## 🚀 설치 및 환경 설정

### 1. 필요한 패키지 설치
```bash
pip install torch transformers pillow requests qwen-vl-utils
```

### 2. GPU 설정 (선택사항)
- **CUDA**: NVIDIA GPU 사용 시 자동 감지
- **MPS**: Apple Silicon Mac 사용 시 자동 감지  
- **CPU**: GPU 없는 환경에서 자동 fallback

## 💻 사용법

### 1. 대화형 분석기 사용

```bash
cd ui-test
python qwen2vl_webapp_analyzer.py
```

**사용 예시:**
```
🌐 웹앱 분석기
==================================================
이 도구는 웹앱 스크린샷을 전문적으로 분석합니다.
사용자의 보충설명을 통해 더 정확한 분석을 제공합니다.

📁 웹앱 스크린샷 경로를 입력하세요: screenshot.png

💬 이 웹앱에 대한 보충설명을 입력해주세요:
설명: 온라인 쇼핑몰의 상품 상세 페이지입니다. 고객이 제품을 구매할 수 있는 화면입니다.

🔍 분석 유형을 선택하세요:
1. 종합 분석 (comprehensive)
2. 빠른 분석 (quick)
3. 상세 분석 (detailed)
4. 워크플로우 분석
5. 접근성 평가
6. 디자인 시스템 분석
7. 맥락 기반 비교 분석

선택 (1-7): 1
```

### 2. API 형태로 사용

```python
from webapp_analysis_api import WebAppAnalysisAPI

# API 인스턴스 생성
api = WebAppAnalysisAPI(device="auto")

# 빠른 분석
result = api.quick_analysis(
    image_path="screenshot.png",
    context="이것은 AI 챗봇 웹 애플리케이션입니다."
)

if result["success"]:
    print("분석 결과:", result["result"])
else:
    print("오류:", result["error"])
```

### 3. 편의 함수 사용

```python
from webapp_analysis_api import analyze_webapp_screenshot

# 간단한 분석
result = analyze_webapp_screenshot(
    image_path="screenshot.png",
    context="온라인 학습 플랫폼의 강의 목록 페이지",
    analysis_type="comprehensive"
)

print(result["result"])
```

## 🔍 분석 유형별 특징

### 1. 빠른 분석 (Quick Analysis)
- **용도**: 핵심 정보만 빠르게 파악
- **포함 내용**: 앱 유형, 주요 기능, UI 요소, 간단 평가
- **처리 시간**: 10-30초

### 2. 종합 분석 (Comprehensive Analysis)  
- **용도**: 전반적인 웹앱 평가
- **포함 내용**: 기본 정보, UI/UX 분석, 사용성 평가, 기술적 관찰
- **처리 시간**: 30-60초

### 3. 상세 분석 (Detailed Analysis)
- **용도**: 매우 자세한 UI/UX 분석
- **포함 내용**: 상세 UI 분석, UX 플로우, 디자인 시스템, 경쟁력 분석
- **처리 시간**: 60-90초

### 4. 워크플로우 분석 (Workflow Analysis)
- **용도**: 사용자 경험 관점 분석
- **포함 내용**: 사용자 목표, 경로 분석, 개선 제안
- **처리 시간**: 40-70초

### 5. 접근성 평가 (Accessibility Evaluation)
- **용도**: WCAG 기준 웹 접근성 평가
- **포함 내용**: 시각적/구조적/인터랙션 접근성, WCAG 준수도
- **처리 시간**: 40-70초

### 6. 디자인 시스템 분석 (Design System Analysis)
- **용도**: 디자인 일관성 및 브랜딩 분석
- **포함 내용**: 컬러/타이포그래피/레이아웃/컴포넌트 시스템 분석
- **처리 시간**: 50-80초

### 7. 맥락 기반 비교 분석 (Contextual Comparison)
- **용도**: 특정 기준과의 비교 분석
- **포함 내용**: 맥락 기반 분석, 기능적 분석, 경험 분석, 개선 제안
- **처리 시간**: 60-90초

## 📊 실제 사용 예제

### 예제 1: E-commerce 사이트 분석

```python
from webapp_analysis_api import WebAppAnalysisAPI

api = WebAppAnalysisAPI()

result = api.comprehensive_analysis(
    image_path="ecommerce_homepage.png",
    context="""
    이것은 패션 의류 온라인 쇼핑몰의 홈페이지입니다. 
    주요 고객층은 20-30대 여성이며, 트렌디한 옷을 판매합니다.
    최근 모바일 사용자가 70% 이상을 차지하고 있습니다.
    """
)

print("분석 결과:", result["result"])
```

### 예제 2: 접근성 평가

```python
from webapp_analysis_api import evaluate_webapp_accessibility

result = evaluate_webapp_accessibility(
    image_path="admin_dashboard.png",
    context="""
    회사 내부 관리자 대시보드입니다. 
    다양한 연령대의 직원들이 사용하며, 
    시각 장애가 있는 직원도 접근할 수 있어야 합니다.
    """
)

if result["success"]:
    print("접근성 평가:", result["result"])
```

### 예제 3: 배치 분석

```python
from webapp_analysis_api import WebAppAnalysisAPI

api = WebAppAnalysisAPI()

# 여러 페이지 일괄 분석
image_paths = [
    "homepage.png",
    "product_list.png", 
    "product_detail.png",
    "checkout.png"
]

context = "온라인 서점의 주요 페이지들입니다. 도서 구매 프로세스를 개선하고 싶습니다."

results = api.batch_analysis(
    image_paths=image_paths,
    context=context,
    analysis_type="quick"
)

for i, result in enumerate(results):
    print(f"\n=== {image_paths[i]} 분석 결과 ===")
    if result["success"]:
        print(result["result"])
    else:
        print(f"오류: {result['error']}")
```

## 🎯 사용자 컨텍스트 작성 팁

### 효과적인 보충설명 작성법

1. **앱의 목적과 비즈니스 모델**
   ```
   "B2B SaaS 플랫폼으로 중소기업의 재고 관리를 돕는 서비스입니다."
   ```

2. **타겟 사용자 정보**
   ```
   "주 사용자는 40-50대 매장 사장님들이며, 컴퓨터에 익숙하지 않은 분들이 많습니다."
   ```

3. **현재 상황이나 문제점**
   ```
   "기존 버전에서 사용자들이 결제 과정을 어려워해서 UI를 개선하고 있습니다."
   ```

4. **특별한 요구사항**
   ```
   "모바일 우선 설계로 터치 인터페이스 최적화가 중요합니다."
   ```

## ⚙️ 고급 설정

### 1. 디바이스 설정

```python
# GPU 강제 사용
api = WebAppAnalysisAPI(device="cuda")

# CPU 강제 사용  
api = WebAppAnalysisAPI(device="cpu")

# Apple Silicon Mac
api = WebAppAnalysisAPI(device="mps")
```

### 2. 커스텀 프롬프트 (내부 수정 필요)

`qwen2vl_webapp_analyzer.py`에서 프롬프트를 수정하여 특정 도메인에 특화된 분석 제공 가능:

```python
# 예: 헬스케어 도메인 특화
system_prompt = """
당신은 헬스케어 웹 애플리케이션 전문 분석가입니다.
의료진과 환자가 사용하는 웹앱의 특성을 고려하여 분석해주세요.
"""
```

## 🔧 트러블슈팅

### 자주 발생하는 문제들

1. **모델 로딩 실패**
   ```
   ❌ 모델 로딩 실패: OutOfMemoryError
   ```
   **해결책**: CPU 모드로 전환
   ```python
   api = WebAppAnalysisAPI(device="cpu")
   ```

2. **이미지 로드 오류**
   ```
   ❌ 파일을 찾을 수 없습니다
   ```
   **해결책**: 파일 경로 확인 및 권한 체크

3. **응답 생성 실패**
   ```
   ❌ 분석 중 오류 발생
   ```
   **해결책**: 이미지 크기 축소 또는 재시도

### 성능 최적화

1. **GPU 메모리 관리**
   ```python
   import torch
   torch.cuda.empty_cache()  # GPU 메모리 정리
   ```

2. **배치 처리 시 메모리 효율화**
   ```python
   # 큰 배치를 작은 단위로 분할
   batch_size = 3
   for i in range(0, len(image_paths), batch_size):
       batch = image_paths[i:i+batch_size]
       results.extend(api.batch_analysis(batch, context))
   ```

## 📈 분석 결과 활용법

### 1. 개발팀 리포트 작성
- 분석 결과를 기반으로 UI/UX 개선 사항 도출
- 우선순위별 개발 로드맵 수립

### 2. 사용자 테스트 준비
- 분석에서 지적된 문제점을 테스트 시나리오에 포함
- 특정 사용자 그룹에 대한 맞춤형 테스트 계획

### 3. 경쟁 분석
- 경쟁사 웹사이트와 비교 분석
- 벤치마킹 포인트 도출

## 🔒 보안 고려사항

1. **민감한 정보**: 스크린샷에 개인정보나 기밀정보가 포함되지 않도록 주의
2. **로컬 실행**: 모델이 로컬에서 실행되므로 데이터가 외부로 전송되지 않음
3. **임시 파일**: 분석 완료 후 임시 파일 자동 삭제

## 🎉 실제 활용 사례

### 사례 1: 스타트업 MVP 검증
```python
# 초기 프로토타입 분석
result = api.quick_analysis(
    "mvp_prototype.png",
    "핀테크 스타트업의 첫 MVP입니다. 투자자 데모데이용으로 만들었습니다."
)
```

### 사례 2: 리뉴얼 프로젝트
```python
# 기존 버전과 신규 버전 비교
old_result = api.comprehensive_analysis("old_version.png", context)
new_result = api.comprehensive_analysis("new_version.png", context)
```

### 사례 3: 접근성 컨설팅
```python
# 정부 웹사이트 접근성 평가
result = api.accessibility_evaluation(
    "government_portal.png",
    "시민들이 사용하는 정부 온라인 포털입니다. 웹 접근성 법규 준수가 필수입니다."
)
```

## 📚 추가 자료

- [Qwen2-VL 공식 문서](https://github.com/QwenLM/Qwen2-VL)
- [웹 접근성 가이드라인 (WCAG)](https://www.w3.org/WAI/WCAG21/quickref/)
- [UI/UX 디자인 원칙](https://www.nngroup.com/articles/)

## 🤝 기여하기

이 도구의 개선에 참여하고 싶다면:

1. 새로운 분석 유형 제안
2. 프롬프트 최적화
3. 성능 개선 아이디어
4. 버그 리포트

---

**💡 팁**: 더 정확한 분석을 위해서는 구체적이고 상세한 사용자 컨텍스트를 제공하는 것이 중요합니다! 