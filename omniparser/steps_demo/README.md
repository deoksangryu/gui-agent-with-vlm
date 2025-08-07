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
**결과**: 다수의 문제점 발견  
**문제들**:
- ❌ 한국어 텍스트 대부분 누락
- ❌ 높은 OCR 임계값으로 작은 텍스트 미감지  
- ❌ Florence2 모델 호환성 문제

---

### 3단계: 한국어 OCR 지원 추가
```bash
python step3_korean_ocr_support.py
```
**목적**: 한국어 텍스트 인식을 위한 OCR 설정 수정  
**개선사항**:
- ✅ EasyOCR 언어 설정: `['en']` → `['ko', 'en']`
- ✅ utils.py 파일 자동 백업 및 수정
- ✅ "토스증권", "주식", "코스피" 등 한국어 텍스트 감지 시작

---

### 4단계: OCR 민감도 개선
```bash
python step4_improved_ocr_sensitivity.py
```
**목적**: 작은 텍스트와 저대비 텍스트 감지 개선  
**개선사항**:
- ✅ `text_threshold`: 0.9 → 0.6 (민감도 향상)
- ✅ 추가 파라미터: `low_text`, `link_threshold`, `canvas_size`, `mag_ratio`
- ✅ +11개 텍스트 추가 감지 (91개 → 102개)
- ✅ "1일", "3", "5", "동방" 등 작은 텍스트 감지 성공

---

### 5단계: BLIP2 모델 교체 (최종 해결)
```bash
python step5_blip2_model_switch.py
```
**목적**: Florence2 호환성 문제 해결  
**핵심 변경**:
- ✅ Florence2 → BLIP2 모델 교체
- ✅ `generate` 메서드 호환성 문제 완전 해결
- ✅ UI 요소 감지: 0개 → **127개** (극적 개선!)
- ✅ 캡션 생성 성공

---

### 6단계: 최종 요약 및 성과 정리
```bash
python step6_final_summary.py
```
**목적**: 전체 과정 요약 및 종합 보고서 생성  
**결과물**:
- 📊 단계별 성과 분석표
- 📄 `final_report.md` - 상세 프로젝트 보고서
- 🚀 `comprehensive_demo.py` - 최종 통합 데모 스크립트

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

## 📁 파일 구조

```
steps/
├── README.md                           # 이 파일
├── step1_basic_demo.py                 # 1단계: Excel 기본 데모
├── step2_toss_initial_attempt.py       # 2단계: 토스 이미지 문제 확인
├── step3_korean_ocr_support.py         # 3단계: 한국어 OCR 지원
├── step4_improved_ocr_sensitivity.py   # 4단계: OCR 민감도 개선
├── step5_blip2_model_switch.py         # 5단계: BLIP2 모델 교체
├── step6_final_summary.py              # 6단계: 최종 요약
├── step1_results/                      # 1단계 결과 폴더
├── step2_results/                      # 2단계 결과 폴더
├── step3_results/                      # 3단계 결과 폴더
├── step4_results/                      # 4단계 결과 폴더
├── step5_results/                      # 5단계 결과 폴더
├── comprehensive_demo.py               # 최종 통합 데모
├── final_report.md                     # 상세 프로젝트 보고서
└── blip2_test.py                      # BLIP2 간단 테스트
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

### 최종 통합 데모만 실행
```bash
cd steps
python comprehensive_demo.py
```

## ⚠️ 필요 조건

### 1. 이미지 파일
- `toss_page.png` 파일이 OmniParser 폴더에 있어야 함
- `excel.png` 파일이 OmniParser 폴더에 있어야 함

### 2. 모델 파일
- `weights/icon_detect/model.pt` - SOM 모델
- `weights/icon_caption_florence/` - Florence2 모델 (3-4단계용)
- BLIP2 모델은 자동 다운로드됨 (5단계)

### 3. Python 환경
```bash
# 가상환경 활성화
source ../bin/activate

# 필요 패키지 확인
pip install torch torchvision transformers ultralytics easyocr opencv-python
```

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

## 🔍 트러블슈팅

### 자주 발생하는 문제들

1. **BLIP2 모델 다운로드 오류**
   ```bash
   # 해결: 네트워크 연결 확인 후 재시도
   # 모델이 자동으로 다운로드됩니다 (~2.7GB)
   ```

2. **한국어 텍스트 감지 안됨**
   ```bash
   # 해결: 3단계 스크립트가 utils.py를 자동 수정
   # 백업파일 확인: util/utils_backup_step3.py
   ```

3. **메모리 부족 오류**
   ```bash
   # 해결: batch_size 조정 또는 CPU 모드 사용
   device = 'cpu'  # CUDA 대신 CPU 사용
   ```

## 📞 지원

- 각 스크립트는 상세한 로그 출력 제공
- 오류 발생 시 각 단계별 결과 폴더에서 중간 결과 확인 가능
- `final_report.md`에서 전체 기술적 세부사항 확인

---

🎉 **축하합니다!** 이 단계별 가이드를 통해 OmniParser를 한국어 모바일 앱에 성공적으로 적용하실 수 있습니다! 