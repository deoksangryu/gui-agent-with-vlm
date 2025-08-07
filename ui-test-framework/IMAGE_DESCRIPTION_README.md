# ShowUI 이미지 설명 가이드

ShowUI 모델을 사용하여 이미지를 분석하고 설명하는 기능에 대한 가이드입니다.

## 🎯 주요 기능

### 1. **전체 이미지 설명**
- 화면의 전반적인 구성과 레이아웃 분석
- 주요 UI 요소들의 식별
- 색상과 디자인 특징 설명

### 2. **UI 요소 분석**
- 버튼, 입력창, 메뉴 등 UI 요소 목록화
- 각 요소의 위치와 기능 설명
- 클릭 가능한 요소 식별

### 3. **텍스트 추출**
- 화면에 표시된 모든 텍스트 인식
- 제목, 본문, 버튼 텍스트 등 분류
- 텍스트의 위치와 중요도 분석

### 4. **액션 제안**
- 사용자가 수행할 수 있는 주요 액션 제안
- 각 액션의 예상 결과 설명
- 사용법 가이드 제공

## 📁 파일 구조

```
ui-test/
├── showui_describe_test.py    # 메인 이미지 설명 클래스
├── example_usage.py           # 간단한 사용 예제
├── IMAGE_DESCRIPTION_README.md # 이 가이드 파일
└── test_screenshot.png        # 테스트용 이미지 (준비 필요)
```

## 🚀 사용법

### 기본 사용법

```python
from showui_describe_test import ShowUIDescriber

# ShowUI 설명기 초기화
describer = ShowUIDescriber()

# 이미지 설명 생성
description = describer.describe_image("your_image.png")
print(description)
```

### 상세 기능 사용

```python
# 1. 전체 이미지 설명
description = describer.describe_image("image.png")

# 2. UI 요소 분석
ui_elements = describer.analyze_ui_elements("image.png")

# 3. 텍스트 추출
text_content = describer.extract_text_content("image.png")

# 4. 액션 제안
actions = describer.suggest_actions("image.png")

# 5. 사용자 정의 질문
custom_answer = describer.describe_image("image.png", "이 앱의 주요 기능은 무엇인가요?")
```

## 🔧 설치 및 설정

### 필요한 패키지

```bash
pip install torch transformers pillow requests qwen-vl-utils
```

### 환경 설정

1. **GPU 사용 (권장)**:
   ```python
   describer = ShowUIDescriber(device="cuda")
   ```

2. **CPU 사용**:
   ```python
   describer = ShowUIDescriber(device="cpu")
   ```

3. **Apple Silicon Mac (MPS)**:
   ```python
   describer = ShowUIDescriber(device="mps")
   ```

## 💡 실행 예제

### 1. 전체 테스트 실행

```bash
cd ui-test
python showui_describe_test.py
```

### 2. 간단한 예제 실행

```bash
python example_usage.py
```

### 3. 대화형 모드

```python
# showui_describe_test.py 실행 후
# 대화형 모드 선택 (y)
# 이미지 경로와 질문 입력
```

## 📋 입력 형식

### 지원하는 이미지 형식
- **로컬 파일**: `"path/to/image.png"`
- **URL**: `"https://example.com/image.jpg"`
- **PIL Image 객체**: `PIL.Image.open("image.png")`

### 지원하는 파일 확장자
- PNG, JPG, JPEG, BMP, GIF, TIFF

## 🎨 예제 질문들

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

## ⚠️ 주의사항

### 모델 로딩 시간
- 첫 실행 시 모델 다운로드로 시간이 걸릴 수 있습니다
- 로컬에 캐시된 후에는 빠르게 로드됩니다

### 메모리 사용량
- ShowUI-2B 모델은 약 4GB의 메모리를 사용합니다
- GPU 메모리가 부족한 경우 CPU 모드를 사용하세요

### 응답 시간
- CPU 모드: 30초 ~ 2분
- GPU 모드: 5초 ~ 30초
- 이미지 크기에 따라 처리 시간이 달라집니다

## 🔍 트러블슈팅

### 1. 모델 로딩 실패
```python
# 인터넷 연결 확인
# Hugging Face 토큰 설정 (필요한 경우)
# 디스크 공간 확인 (최소 8GB)
```

### 2. 메모리 부족
```python
# CPU 모드 사용
describer = ShowUIDescriber(device="cpu")

# 또는 이미지 크기 줄이기
image = Image.open("large_image.png")
image = image.resize((800, 600))
```

### 3. 느린 처리 속도
```python
# GPU 사용 (CUDA 설치 필요)
describer = ShowUIDescriber(device="cuda")

# 또는 더 작은 이미지 사용
# max_new_tokens 줄이기 (응답 길이 단축)
```

## 📊 성능 최적화

### 배치 처리 (여러 이미지)

```python
# 여러 이미지를 순차적으로 처리
images = ["img1.png", "img2.png", "img3.png"]
results = []

for image_path in images:
    result = describer.describe_image(image_path)
    results.append(result)
```

### 결과 캐싱

```python
import json

# 결과 저장
results = {
    "image1.png": describer.describe_image("image1.png"),
    "image2.png": describer.describe_image("image2.png"),
}

with open("analysis_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

## 🤝 기여하기

버그 리포트나 기능 제안은 이슈를 통해 알려주세요!

### 개발 가이드라인
1. 코드에 주석 추가
2. 에러 처리 포함
3. 예제 코드 작성
4. 테스트 케이스 추가

---

**📄 Last Updated**: 2024년 12월
**🔧 Version**: 1.0.0
**👨‍💻 Author**: ShowUI Team 