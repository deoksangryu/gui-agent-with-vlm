# 🎯 ShowUI 헬퍼 시스템

Qwen2VL 기반의 ShowUI 자동화 전용 UI 요소 추출 도구입니다. 웹 애플리케이션 스크린샷을 분석하여 ShowUI 모델이 자동화 작업에 사용할 수 있는 상세한 UI 요소 정보를 제공합니다.

## ✨ 주요 특징

- **ShowUI 특화**: ShowUI 자동화에 최적화된 UI 요소 분석
- **정확한 위치 정보**: 각 UI 요소의 구체적인 위치 설명
- **상호작용 요소 식별**: 클릭, 입력, 스크롤 가능한 모든 요소 탐지
- **명령어 자동 생성**: ShowUI 명령어 시퀀스 자동 생성
- **다양한 분석 모드**: UI 요소/폼/네비게이션/콘텐츠 전문 분석

## 📁 파일 구조

```
ui-test/
├── qwen2vl_showui_helper.py     # 메인 ShowUI 헬퍼 (대화형)
├── showui_helper_api.py         # API 스타일 인터페이스
└── SHOWUI_HELPER_README.md      # 이 파일
```

## 🚀 설치 및 환경 설정

### 필요한 패키지 설치
```bash
pip install torch transformers pillow requests qwen-vl-utils
```

## 💻 사용법

### 1. 대화형 헬퍼 사용

```bash
cd ui-test
python qwen2vl_showui_helper.py
```

**사용 예시:**
```
🎯 ShowUI 헬퍼 - UI 요소 추출기
==================================================

📁 웹앱 스크린샷 경로를 입력하세요: screenshot.png

💬 이 웹앱에 대한 설명을 입력해주세요:
설명: 토스증권 메인 화면입니다.

🔍 분석 유형을 선택하세요:
1. UI 요소 추출 (모든 상호작용 요소)
2. ShowUI 명령어 생성
3. 폼 구조 분석
4. 네비게이션 구조 분석
5. 콘텐츠 영역 추출

선택 (1-5): 1

수행할 작업이 있다면 설명해주세요 (선택사항): 삼성전자 주식 검색하기
```

### 2. API 형태로 사용

```python
from showui_helper_api import ShowUIHelperAPI

# API 인스턴스 생성
api = ShowUIHelperAPI(device="auto")

# UI 요소 추출
result = api.extract_ui_elements(
    image_path="screenshot.png",
    context="토스증권 메인 화면입니다.",
    task="삼성전자 주식을 검색하고 싶습니다."
)

if result["success"]:
    print("UI 요소 정보:", result["result"])
else:
    print("오류:", result["error"])
```

### 3. 편의 함수 사용

```python
from showui_helper_api import extract_ui_elements_for_showui

# 간단한 UI 요소 추출
result = extract_ui_elements_for_showui(
    image_path="screenshot.png",
    context="온라인 쇼핑몰 상품 페이지",
    task="장바구니에 상품 추가하기"
)

print(result["result"])
```

## 🔍 분석 유형별 특징

### 1. UI 요소 추출 (extract_ui_elements)
**목적**: ShowUI가 상호작용할 수 있는 모든 요소 식별

**추출 정보**:
- 클릭 가능한 요소들 (버튼, 링크, 아이콘 등)
- 입력 가능한 요소들 (텍스트 박스, 드롭다운 등)
- 각 요소의 정확한 위치 설명
- 요소별 기능과 목적
- ShowUI 접근을 위한 식별 방법

### 2. ShowUI 명령어 생성 (generate_showui_commands)
**목적**: 특정 작업을 위한 ShowUI 명령어 시퀀스 생성

**제공 명령어**:
- `click("위치설명")` - 요소 클릭
- `type("위치설명", "텍스트")` - 텍스트 입력
- `scroll("방향", "정도")` - 스크롤
- `wait(시간)` - 대기

### 3. 폼 구조 분석 (identify_form_structure)
**목적**: 입력 양식의 구조적 분석

**분석 내용**:
- 각 입력 필드의 유형과 용도
- 필수/선택 필드 구분
- 자연스러운 입력 순서
- 검증 규칙 및 제한사항

### 4. 네비게이션 구조 분석 (analyze_navigation_structure)
**목적**: 페이지 이동 및 메뉴 구조 분석

**분석 내용**:
- 메인 네비게이션 (상단/사이드/하단 메뉴)
- 브레드크럼 및 경로 표시
- 검색 기능
- 페이지네이션

### 5. 콘텐츠 영역 추출 (extract_content_areas)
**목적**: 페이지의 주요 콘텐츠 영역 식별

**분석 내용**:
- 헤더/메인/사이드바/푸터 영역
- 텍스트 콘텐츠 정리
- 데이터 표시 영역
- 상호작용 요소 위치

## 📊 실제 사용 예제

### 예제 1: 온라인 쇼핑몰 자동화

```python
from showui_helper_api import ShowUIHelperAPI

api = ShowUIHelperAPI()

# 상품 검색 페이지 분석
result = api.extract_ui_elements(
    image_path="shopping_search.png",
    context="온라인 쇼핑몰의 상품 검색 페이지입니다.",
    task="노트북을 검색하고 가격 필터를 적용하고 싶습니다."
)

print("검색 관련 UI 요소:", result["result"])

# ShowUI 명령어 생성
commands = api.generate_commands(
    image_path="shopping_search.png",
    context="온라인 쇼핑몰의 상품 검색 페이지입니다.",
    task_sequence="노트북 검색 → 가격 필터 20만원~50만원 → 정렬 낮은가격순"
)

print("자동화 명령어:", commands["result"])
```

### 예제 2: 금융 사이트 주식 거래

```python
from showui_helper_api import analyze_webpage_for_automation

# 증권사 사이트 전체 분석
result = analyze_webpage_for_automation(
    image_path="stock_trading.png",
    context="증권사 주식 거래 화면입니다.",
    target_task="삼성전자 주식 100주 시장가 매수 주문"
)

# 모든 분석 결과 확인
for analysis_type, analysis_result in result["results"].items():
    print(f"\n=== {analysis_type} ===")
    if analysis_result["success"]:
        print(analysis_result["result"])
    else:
        print(f"오류: {analysis_result['error']}")
```

### 예제 3: 폼 입력 자동화

```python
api = ShowUIHelperAPI()

# 회원가입 폼 분석
form_analysis = api.analyze_form(
    image_path="signup_form.png",
    context="회원가입 페이지입니다. 이메일, 비밀번호, 개인정보를 입력해야 합니다."
)

print("폼 구조:", form_analysis["result"])

# 자동 입력 명령어 생성
auto_fill = api.generate_commands(
    image_path="signup_form.png",
    context="회원가입 페이지입니다.",
    task_sequence="""
    1. 이메일 입력: test@example.com
    2. 비밀번호 입력: password123!
    3. 비밀번호 확인: password123!
    4. 이름 입력: 홍길동
    5. 전화번호 입력: 010-1234-5678
    6. 가입하기 버튼 클릭
    """
)

print("자동 입력 명령어:", auto_fill["result"])
```

## 🎯 ShowUI 명령어 형식

### 기본 명령어

1. **클릭 명령어**
   ```
   click("화면 우상단의 로그인 버튼")
   click("메인 메뉴의 '상품' 링크")
   click("검색 결과 첫 번째 상품 이미지")
   ```

2. **텍스트 입력 명령어**
   ```
   type("검색창", "삼성전자")
   type("이메일 입력 필드", "user@example.com")
   type("비밀번호 필드", "password123")
   ```

3. **스크롤 명령어**
   ```
   scroll("down", "medium")
   scroll("up", "small")
   scroll("right", "large")
   ```

4. **대기 명령어**
   ```
   wait(2)  # 2초 대기
   wait(5)  # 5초 대기
   ```

### 복합 작업 예시

```python
# 온라인 쇼핑 자동화 시퀀스
task_sequence = """
1. 상품 검색하기
2. 필터 옵션 설정하기  
3. 원하는 상품 선택하기
4. 장바구니에 추가하기
5. 결제 페이지로 이동하기
"""

commands = api.generate_commands(
    image_path="shopping_page.png",
    context="온라인 쇼핑몰 메인 페이지",
    task_sequence=task_sequence
)
```

## ⚙️ 고급 설정

### 1. 디바이스 설정

```python
# GPU 강제 사용
api = ShowUIHelperAPI(device="cuda")

# CPU 강제 사용
api = ShowUIHelperAPI(device="cpu") 

# Apple Silicon Mac
api = ShowUIHelperAPI(device="mps")
```

### 2. 배치 처리

```python
api = ShowUIHelperAPI()

# 여러 페이지 연속 분석
pages = [
    {"image": "page1.png", "context": "홈페이지"},
    {"image": "page2.png", "context": "상품 목록"},
    {"image": "page3.png", "context": "상품 상세"},
    {"image": "page4.png", "context": "장바구니"}
]

for page in pages:
    print(f"\n분석 중: {page['context']}")
    result = api.extract_ui_elements(
        page["image"], 
        page["context"]
    )
    
    if result["success"]:
        print(f"UI 요소 수: {len(result['result'].split('요소'))}")
    else:
        print(f"분석 실패: {result['error']}")
```

## 🔧 트러블슈팅

### 자주 발생하는 문제들

1. **모델 로딩 실패**
   ```
   ❌ 모델 로딩 실패: OutOfMemoryError
   ```
   **해결책**: CPU 모드 사용
   ```python
   api = ShowUIHelperAPI(device="cpu")
   ```

2. **UI 요소 인식 오류**
   ```
   UI 요소가 정확히 인식되지 않음
   ```
   **해결책**: 더 구체적인 컨텍스트 제공
   ```python
   context = "토스증권 주식 거래 화면. 검색창은 상단 중앙에, 매수/매도 버튼은 우측에 위치"
   ```

3. **이미지 해상도 문제**
   ```
   이미지가 너무 크거나 작아서 분석이 부정확함
   ```
   **해결책**: 적절한 해상도로 조정 (1920x1080 권장)

### 성능 최적화

1. **메모리 관리**
   ```python
   import torch
   
   # 분석 후 GPU 메모리 정리
   if torch.cuda.is_available():
       torch.cuda.empty_cache()
   ```

2. **분석 정확도 향상**
   ```python
   # 더 구체적인 컨텍스트 제공
   context = """
   이것은 네이버 쇼핑 검색 결과 페이지입니다.
   - 검색창: 상단 중앙
   - 카테고리 필터: 좌측 사이드바
   - 상품 리스트: 메인 영역 그리드 형태
   - 페이지네이션: 하단 중앙
   """
   ```

## 📈 ShowUI와 연동하는 방법

### 1. UI 요소 정보 추출

```python
# 1단계: UI 요소 추출
ui_info = api.extract_ui_elements(
    "webpage.png", 
    "온라인 뱅킹 로그인 페이지",
    "로그인하고 계좌 조회하기"
)

# 2단계: ShowUI 명령어 생성
commands = api.generate_commands(
    "webpage.png",
    "온라인 뱅킹 로그인 페이지", 
    "아이디: testuser, 비밀번호: pass123 입력 후 로그인"
)

# 3단계: ShowUI 실행 (예시)
# showui_model.execute(commands["result"])
```

### 2. 실시간 피드백 루프

```python
def automated_workflow(start_image, target_task):
    """ShowUI 자동화 워크플로우"""
    
    current_image = start_image
    step = 1
    
    while step <= 10:  # 최대 10단계
        print(f"단계 {step}: 현재 화면 분석 중...")
        
        # 현재 화면 분석
        analysis = api.extract_ui_elements(
            current_image,
            f"자동화 작업 {step}단계 화면",
            target_task
        )
        
        if not analysis["success"]:
            print(f"분석 실패: {analysis['error']}")
            break
            
        # 다음 액션 결정
        next_commands = api.generate_commands(
            current_image,
            f"자동화 작업 {step}단계 화면",
            f"목표: {target_task}, 현재 단계: {step}"
        )
        
        print(f"실행할 명령어: {next_commands['result']}")
        
        # ShowUI 실행 (실제 구현 필요)
        # current_image = execute_showui_commands(next_commands["result"])
        
        step += 1
        
        # 작업 완료 조건 확인
        if "완료" in analysis["result"] or "성공" in analysis["result"]:
            print("자동화 작업 완료!")
            break

# 사용 예시
# automated_workflow("banking_login.png", "계좌 잔액 조회하기")
```

## 🎉 실제 활용 사례

### 사례 1: E-commerce 자동 주문

```python
api = ShowUIHelperAPI()

# 쇼핑몰 자동 주문 프로세스
shopping_steps = [
    {
        "image": "homepage.png",
        "context": "쇼핑몰 홈페이지",
        "task": "노트북 카테고리로 이동"
    },
    {
        "image": "category.png", 
        "context": "노트북 카테고리 페이지",
        "task": "브랜드 필터 삼성 선택"
    },
    {
        "image": "filtered.png",
        "context": "필터링된 상품 목록",
        "task": "첫 번째 상품 선택"
    },
    {
        "image": "product.png",
        "context": "상품 상세 페이지", 
        "task": "옵션 선택 후 장바구니 추가"
    }
]

for step in shopping_steps:
    commands = api.generate_commands(
        step["image"],
        step["context"],
        step["task"]
    )
    print(f"단계: {step['task']}")
    print(f"명령어: {commands['result']}\n")
```

### 사례 2: 데이터 수집 자동화

```python
# 부동산 사이트 데이터 수집
data_collection = api.full_analysis(
    image_path="realestate_search.png",
    context="부동산 검색 사이트. 아파트 매매 정보를 검색할 수 있습니다.",
    target_task="강남구 아파트 매매 정보 수집하기"
)

# 데이터 추출 영역 확인
content_areas = data_collection["results"]["content_extraction"]
print("데이터 수집 가능 영역:", content_areas["result"])

# 자동 수집 명령어
collection_commands = data_collection["results"]["showui_commands"]
print("자동 수집 명령어:", collection_commands["result"])
```

## 🔒 보안 고려사항

1. **스크린샷 민감정보**: 개인정보나 금융정보가 포함된 스크린샷 주의
2. **로컬 처리**: 모든 분석이 로컬에서 수행되어 데이터 외부 유출 없음
3. **자동화 권한**: ShowUI 자동화 시 적절한 권한 확인 필요

## 📚 추가 자료

- [ShowUI 공식 문서](https://github.com/showlab/ShowUI)
- [Qwen2-VL 모델 정보](https://github.com/QwenLM/Qwen2-VL)
- [웹 자동화 모범 사례](https://selenium-python.readthedocs.io/)

---

**💡 팁**: ShowUI 자동화의 정확도를 높이려면 구체적이고 상세한 UI 요소 위치 정보를 제공하는 것이 중요합니다! 