# Qwen2VL 이미지 설명 가이드

검증된 **Qwen2VL-2B-Instruct** 모델을 사용하여 이미지를 분석하고 설명하는 기능에 대한 가이드입니다.

## 🎯 주요 특징

### ✅ **검증된 안정성**
- ShowUI 프로젝트에서 실제 사용되는 검증된 코드 기반
- Qwen2VL-2B-Instruct 모델로 신뢰성 높은 응답 생성
- 메모리 효율적인 GPU 설정으로 안정적인 동작

### 🚀 **핵심 기능들**

1. **📝 전체 이미지 설명** - 화면 구성, UI 요소, 색상, 디자인 종합 분석
2. **🔍 UI 요소 분석** - 버튼, 입력창, 메뉴 등 세부 요소 목록화
3. **📄 텍스트 추출** - 화면의 모든 텍스트 인식 및 분류
4. **🎯 액션 제안** - 사용자가 수행할 수 있는 행동 제안
5. **🏷️ 앱 종류 식별** - 앱/웹사이트 카테고리 및 특징 분석
6. **❓ 사용자 정의 질문** - 원하는 정보에 대한 맞춤형 질문 응답

## 📁 파일 구조

```
ui-test/
├── qwen2vl_describe_test.py     # 메인 Qwen2VL 이미지 설명 클래스
├── qwen2vl_simple_test.py       # 빠른 테스트용 스크립트
├── QWEN2VL_README.md            # 이 가이드 파일
├── test_screenshot.png          # 테스트용 이미지 (준비 필요)
└── ShowUI/                      # ShowUI 프로젝트 (의존성)
```

## 🔧 설치 및 환경 설정

### 필수 패키지 설치

```bash
# 기본 패키지
pip install torch transformers pillow requests

# Qwen VL 유틸리티 (필수!)
pip install qwen-vl-utils

# GPU 지원 (선택사항, 권장)
# CUDA 설치된 환경에서:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 시스템 요구사항

- **메모리**: 최소 8GB RAM (CPU 모드), 4GB+ GPU 메모리 (GPU 모드)
- **저장공간**: 모델 다운로드를 위한 6GB+ 여유공간
- **Python**: 3.8+ 버전

## 🚀 사용법

### 기본 사용법

```python
from qwen2vl_describe_test import Qwen2VLDescriber

# 모델 초기화
describer = Qwen2VLDescriber()

# 이미지 설명 생성
description = describer.describe_image("test_screenshot.png")
print(description)
```

### 상세 기능 활용

```python
# 1. 전체 이미지 설명
description = describer.describe_image("image.png")

# 2. UI 요소 분석
ui_elements = describer.analyze_ui_elements("image.png")

# 3. 텍스트 추출
text_content = describer.extract_text_content("image.png")

# 4. 액션 제안
actions = describer.suggest_actions("image.png")

# 5. 앱 종류 식별
app_type = describer.identify_app_type("image.png")

# 6. 사용자 정의 질문
custom_answer = describer.describe_image("image.png", "이 앱의 주요 기능은 무엇인가요?")
```

### 디바이스 선택

```python
# 자동 선택 (기본값)
describer = Qwen2VLDescriber(device="auto")

# GPU 사용 (권장)
describer = Qwen2VLDescriber(device="cuda")

# CPU 사용 (메모리 부족시)
describer = Qwen2VLDescriber(device="cpu")

# Apple Silicon Mac
describer = Qwen2VLDescriber(device="mps")
```

## 💡 실행 예제

### 1. 전체 테스트 실행

```bash
cd ui-test
python qwen2vl_describe_test.py
```

### 2. 빠른 테스트

```bash
python qwen2vl_simple_test.py
```

### 3. 대화형 모드

메인 스크립트 실행 후 대화형 모드 선택

## 📋 지원 형식

### 이미지 입력 형식
- **로컬 파일**: `"path/to/image.png"`
- **URL**: `"https://example.com/image.jpg"`
- **PIL Image 객체**: `Image.open("image.png")`

### 지원 파일 확장자
- PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP

## 🎨 질문 예제

### 일반적인 질문
```python
questions = [
    "이 이미지를 설명해주세요.",
    "이 앱의 주요 기능은 무엇인가요?",
    "사용자가 다음에 할 수 있는 행동은 무엇인가요?",
    "이 화면에서 가장 중요한 요소는 무엇인가요?",
    "모든 텍스트를 읽어주세요.",
]
```

### 상세 분석 질문
```python
detailed_questions = [
    "이 UI의 접근성은 어떤가요?",
    "모바일에 최적화되어 있나요?",
    "어떤 디자인 패턴을 사용하고 있나요?",
    "사용자 경험 관점에서 개선점은?",
    "이 화면의 주요 사용 시나리오는?",
]
```

### 업무 특화 질문
```python
work_questions = [
    "이 앱은 어떤 비즈니스 목적을 가지고 있나요?",
    "경쟁사 대비 차별화 포인트는?",
    "수익 모델은 무엇일까요?",
    "타겟 고객층은 누구인가요?",
    "마케팅 전략을 제안해주세요.",
]
```

## ⚡ 성능 최적화

### 응답 속도
- **GPU 모드**: 5-15초
- **CPU 모드**: 30초-2분
- **첫 실행**: 모델 다운로드로 추가 시간 소요

### 메모리 최적화
```python
# 메모리 절약을 위한 설정
torch.backends.cuda.enable_mem_efficient_sdp(False)
torch.backends.cuda.enable_flash_sdp(False)

# 배치 크기 조정 (메모리 부족시)
# generate() 함수에서 max_new_tokens 값 줄이기
```

### 배치 처리
```python
# 여러 이미지 순차 처리
images = ["img1.png", "img2.png", "img3.png"]
results = []

for image_path in images:
    result = describer.describe_image(image_path)
    results.append(result)
    print(f"완료: {image_path}")
```

## 🔍 트러블슈팅

### 1. 모델 로딩 실패
```
❌ 문제: transformers 라이브러리 버전 호환성
✅ 해결: pip install transformers>=4.37.0
```

### 2. qwen-vl-utils 없음
```
❌ 문제: ModuleNotFoundError: No module named 'qwen_vl_utils'
✅ 해결: pip install qwen-vl-utils
```

### 3. GPU 메모리 부족
```python
# CPU 모드로 전환
describer = Qwen2VLDescriber(device="cpu")

# 또는 이미지 크기 줄이기
from PIL import Image
image = Image.open("large_image.png")
image = image.resize((800, 600))
```

### 4. 느린 처리 속도
```python
# GPU 사용 확인
import torch
print(f"CUDA 사용 가능: {torch.cuda.is_available()}")

# 모델 최적화
describer = Qwen2VLDescriber(device="cuda")
```

### 5. 한국어 응답 품질
```python
# 프롬프트에 명시적 언어 지정
prompt = "이 이미지를 한국어로 자세히 설명해주세요."
response = describer.describe_image("image.png", prompt)
```

## 📊 성능 벤치마크

### 모델 정보
- **모델명**: Qwen2-VL-2B-Instruct
- **파라미터 수**: 20억개
- **모델 크기**: ~4GB
- **지원 언어**: 다국어 (한국어 포함)

### 정확도 특징
- ✅ **텍스트 인식**: 매우 높음
- ✅ **UI 요소 식별**: 높음
- ✅ **한국어 응답**: 자연스러움
- ✅ **상황 이해**: 우수
- ⚠️ **세밀한 위치 정보**: 대략적

## 🆚 ShowUI vs Qwen2VL 비교

| 특징 | ShowUI | Qwen2VL |
|------|--------|---------|
| **주목적** | UI 자동화 + 설명 | 범용 VL 모델 |
| **클릭 좌표** | ✅ 정확 | ❌ 없음 |
| **이미지 설명** | ⚠️ 간단 | ✅ 상세 |
| **안정성** | ⚠️ 개발중 | ✅ 검증됨 |
| **한국어** | ⚠️ 제한적 | ✅ 우수 |
| **응답 속도** | 빠름 | 보통 |
| **메모리 사용** | 높음 | 보통 |

## 💼 실제 활용 사례

### 1. **웹 접근성 감사**
```python
accessibility_prompt = """
이 웹페이지의 접근성을 평가해주세요:
1. 색상 대비는 적절한가요?
2. 텍스트 크기는 읽기 좋은가요?
3. 버튼은 명확하게 식별되나요?
4. 키보드 접근이 가능해 보이나요?
5. 개선 제안사항은?
"""
result = describer.describe_image("webpage.png", accessibility_prompt)
```

### 2. **경쟁사 분석**
```python
competitor_prompt = """
이 앱을 경쟁사 관점에서 분석해주세요:
1. 주요 기능과 차별화 포인트
2. UI/UX의 강점과 약점
3. 타겟 사용자층
4. 비즈니스 모델 추정
5. 벤치마킹 포인트
"""
analysis = describer.describe_image("competitor_app.png", competitor_prompt)
```

### 3. **사용성 테스트**
```python
usability_prompt = """
사용성 관점에서 이 화면을 평가해주세요:
1. 첫 사용자가 이해하기 쉬운가요?
2. 주요 액션을 찾기 쉬운가요?
3. 정보 구조가 논리적인가요?
4. 개선이 필요한 부분은?
"""
usability = describer.describe_image("app_screen.png", usability_prompt)
```

## 🤝 기여하기

버그 리포트나 기능 제안은 이슈를 통해 알려주세요!

### 개발 가이드라인
1. 코드에 한국어 주석 추가
2. 에러 처리 포함
3. 예제 코드 작성
4. 성능 최적화 고려

---

**📄 Last Updated**: 2024년 12월  
**🔧 Version**: 1.0.0  
**👨‍💻 Author**: Qwen2VL Team  
**🏷️ Based on**: Qwen2-VL-2B-Instruct 