# 🚀 OmniParser 토스 앱 UI 파싱 단계별 데모
===============================================

이 폴더는 OmniParser를 사용하여 토스 앱의 한국어 UI를 성공적으로 파싱하는 과정을 단계별로 보여주는 데모 스크립트들을 포함합니다.

## 📋 프로젝트 개요

- **목표**: 토스 앱 UI에서 한국어 텍스트와 UI 요소 완벽 파싱
- **도구**: Microsoft OmniParser v2.0
- **최종 성과**: 127개 UI 요소 감지 성공! 🏆

## 🎯 단계별 진행 과정

### 1단계: 기본 데모 (Excel 이미지)
```bash
cd steps
python step1_basic_demo.py
```
**목적**: OmniParser 기본 기능 검증  
**결과**: Excel 이미지에서 영어 텍스트 성공적 인식  
**문제**: 한국어 지원 없음

---

### 2단계: 토스 이미지 첫 시도
```bash
python step2_toss_initial_attempt.py
```
**목적**: 토스 앱에 기본 설정 적용 시 문제점 확인  
**문제들**:
- ❌ 한국어 텍스트 대부분 누락
- ❌ 높은 OCR 임계값으로 작은 텍스트 미감지  
- ❌ Florence2 모델 호환성 문제

---

### 3단계: 한국어 OCR 지원 추가
```bash
python step3_korean_ocr_support.py
```
**개선사항**:
- ✅ EasyOCR 언어 설정: `['en']` → `['ko', 'en']`
- ✅ "토스증권", "주식", "코스피" 등 한국어 텍스트 감지 시작

---

### 4단계: OCR 민감도 개선
```bash
python step4_improved_ocr_sensitivity.py
```
**개선사항**:
- ✅ `text_threshold`: 0.9 → 0.6 (민감도 향상)
- ✅ +11개 텍스트 추가 감지 (91개 → 102개)
- ✅ "1일", "3", "5", "동방" 등 작은 텍스트 감지 성공

---

### 5단계: BLIP2 모델 교체 (최종 해결)
```bash
python step5_blip2_model_switch.py
```
**핵심 변경**:
- ✅ Florence2 → BLIP2 모델 교체
- ✅ UI 요소 감지: 0개 → **127개** (극적 개선!)
- ✅ 캡션 생성 성공

---

### 6단계: 최종 요약 및 성과 정리
```bash
python step6_final_summary.py
```
**결과물**: 전체 과정 요약 및 성과 분석

## 📊 최종 성과 요약

| 구분 | 1단계 (Excel) | 2단계 (토스-문제) | 5단계 (토스-성공) |
|------|---------------|------------------|------------------|
| **OCR 텍스트** | 63개 | ~30개 | **102개** |
| **UI 요소** | 성공 | 0개 | **127개** |
| **한국어 지원** | ❌ | ❌ | ✅ |
| **모델 호환성** | ✅ | ❌ | ✅ |

## 🔧 핵심 기술 개선사항

### 1. 한국어 지원
```python
# 변경 전
reader = easyocr.Reader(['en'])

# 변경 후  
reader = easyocr.Reader(['ko', 'en'])
```

### 2. OCR 민감도 최적화
```python
easyocr_args = {
    'paragraph': False,
    'text_threshold': 0.6,    # 0.9 → 0.6
    'low_text': 0.3,         # 작은 텍스트
    'link_threshold': 0.4,    # 텍스트 연결
    'canvas_size': 3000,      # 고해상도
    'mag_ratio': 1.5          # 확대비율
}
```

### 3. 모델 호환성 해결
```python
# 변경 전 (문제)
caption_model_processor = get_caption_model_processor(
    model_name="florence2"
)

# 변경 후 (해결)
caption_model_processor = get_caption_model_processor(
    model_name="blip2"
)
```

## 🚀 실행 방법

### 전체 단계 순서대로 실행
```bash
cd steps

# 1단계: 기본 데모
python step1_basic_demo.py

# 2단계: 문제 확인  
python step2_toss_initial_attempt.py

# 3단계: 한국어 지원
python step3_korean_ocr_support.py

# 4단계: 민감도 개선
python step4_improved_ocr_sensitivity.py

# 5단계: BLIP2 교체 (최종 해결)
python step5_blip2_model_switch.py

# 6단계: 최종 요약
python step6_final_summary.py
```

## ⚠️ 필요 조건

### 1. 이미지 파일
- `toss_page.png` 파일이 OmniParser 폴더에 있어야 함
- `excel.png` 파일이 OmniParser 폴더에 있어야 함

### 2. 모델 파일
- `weights/icon_detect/model.pt` - SOM 모델
- `weights/icon_caption_florence/` - Florence2 모델 (3-4단계용)
- BLIP2 모델은 자동 다운로드됨 (5단계)

## 📈 각 단계별 예상 결과

| 단계 | OCR 텍스트 | UI 요소 | 주요 성과 |
|------|------------|---------|-----------|
| 1단계 | 63개 | ~70개 | Excel 성공 확인 |
| 2단계 | ~30개 | 0개 | 문제점 파악 |
| 3단계 | ~91개 | 0개 | 한국어 감지 시작 |
| 4단계 | 102개 | 0개 | 작은 텍스트 개선 |
| 5단계 | 102개 | **127개** | 완전 성공! |

## 🎯 실용적 활용

### UI 자동화
```python
# 클릭 가능한 요소들의 좌표 정보 활용
for element in parsed_content_list:
    if element['content'] == '토스증권':
        x, y = element['coordinate']
        # 자동 클릭 구현 가능
```

### 접근성 개선
- 시각 장애인을 위한 UI 음성 설명
- BLIP2 캡션으로 UI 컨텍스트 제공

### 테스팅 자동화
- 모바일 앱 UI 자동 테스트
- 다국어 UI 검증 도구

---

🎉 **축하합니다!** 이 단계별 가이드를 통해 OmniParser를 한국어 모바일 앱에 성공적으로 적용하실 수 있습니다!
