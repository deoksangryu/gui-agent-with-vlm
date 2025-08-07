# OmniParser 한글 UI 파악을 위한 OCR → BLIP2 전환 분석

## 개요

OmniParser에서 한글 UI를 효과적으로 파악하기 위해 OCR(Optical Character Recognition) 시스템을 BLIP2 모델로 전환한 과정과 결과를 분석합니다.

## 문제 상황

### 초기 문제점
1. **한글 텍스트 인식 부족**: 기본 EasyOCR이 영어만 지원
2. **Florence2 모델 호환성 문제**: 캡션 생성 실패
3. **작은 텍스트 감지 부족**: 높은 임계값(0.9)으로 인한 누락
4. **UI 요소 캡션 생성 실패**: 모델 호환성 문제

## 단계별 해결 과정

### 1단계: 한국어 OCR 지원 추가

**파일**: `steps/step3_korean_ocr_support.py`

**핵심 변경사항**:
```python
# 변경 전
reader = easyocr.Reader(['en'])

# 변경 후  
reader = easyocr.Reader(['ko', 'en'])
```

**개선 효과**:
- 한국어 텍스트 감지 시작: '토스증권', '주식', '코스피'
- OCR 텍스트: ~30개 → ~91개 (+61개 증가)
- 한국어 감지율: 0% → 70%+

**남은 문제**:
- 여전히 높은 임계값 (0.9)
- 작은 텍스트 '3', '4', '5', '6' 누락
- Florence2 모델 호환성 문제 지속

### 2단계: OCR 민감도 개선

**파일**: `steps/step4_improved_ocr_sensitivity.py`

**개선된 OCR 설정**:
```python
easyocr_args = {
    'paragraph': False,
    'text_threshold': 0.6,  # 0.9 → 0.6
    'low_text': 0.3,
    'link_threshold': 0.4,
    'canvas_size': 3000,
    'mag_ratio': 1.5
}
```

**개선 효과**:
- OCR 텍스트: 91개 → 102개 (+11개 추가 감지)
- 작은 텍스트 성공 감지: '1일', '3', '5', '동방'
- 저대비 텍스트 인식 개선
- 고해상도 이미지 처리 최적화

**남은 문제**:
- Florence2 모델 호환성 문제 지속
- 일부 작은 숫자 '4', '6' 여전히 누락
- UI 요소 캡션 생성 실패

### 3단계: BLIP2 모델로 교체 (최종 해결)

**파일**: `steps/step5_blip2_model_switch.py`

**핵심 변경사항**:
```python
# 변경 전 (문제)
caption_model_processor = get_caption_model_processor(
    model_name='florence2'
)

# 변경 후 (해결)
caption_model_processor = get_caption_model_processor(
    model_name='blip2',
    model_name_or_path='Salesforce/blip2-opt-2.7b'
)
```

**극적인 개선 결과**:
- UI 요소 감지: 0개 → 127개 (완전 성공!)
- OCR 텍스트: 102개 (이전 단계 유지)
- 캡션 생성: 성공 (BLIP2 영어 설명)
- 처리 시간: ~79초 (OCR 3초 + SOM 76초)

## 기술적 구현 세부사항

### 1. 캡션 모델 처리기 구현

**파일**: `util/utils.py` - `get_caption_model_processor()`

```python
def get_caption_model_processor(model_name, model_name_or_path="Salesforce/blip2-opt-2.7b", device=None):
    if not device:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    if model_name == "blip2":
        from transformers import Blip2Processor, Blip2ForConditionalGeneration
        processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
        if device == 'cpu':
            model = Blip2ForConditionalGeneration.from_pretrained(
                model_name_or_path, device_map=None, torch_dtype=torch.float32
            ) 
        else:
            model = Blip2ForConditionalGeneration.from_pretrained(
                model_name_or_path, device_map=None, torch_dtype=torch.float16
            ).to(device)
    
    elif model_name == "florence2":
        from transformers import AutoProcessor, AutoModelForCausalLM 
        processor = AutoProcessor.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)
        if device == 'cpu':
            model = AutoModelForCausalLM.from_pretrained(model_name_or_path, torch_dtype=torch.float32, trust_remote_code=True)
        else:
            model = AutoModelForCausalLM.from_pretrained(model_name_or_path, torch_dtype=torch.float16, trust_remote_code=True).to(device)
    
    return {'model': model.to(device), 'processor': processor}
```

### 2. 캡션 생성 함수

**파일**: `util/utils.py` - `get_parsed_content_icon()`

```python
@torch.inference_mode()
def get_parsed_content_icon(filtered_boxes, starting_idx, image_source, caption_model_processor, prompt=None, batch_size=128):
    # 이미지 크롭 및 전처리
    croped_pil_image = []
    for i, coord in enumerate(non_ocr_boxes):
        try:
            xmin, xmax = int(coord[0]*image_source.shape[1]), int(coord[2]*image_source.shape[1])
            ymin, ymax = int(coord[1]*image_source.shape[0]), int(coord[3]*image_source.shape[0])
            cropped_image = image_source[ymin:ymax, xmin:xmax, :]
            cropped_image = cv2.resize(cropped_image, (64, 64))
            croped_pil_image.append(to_pil(cropped_image))
        except:
            continue

    model, processor = caption_model_processor['model'], caption_model_processor['processor']
    
    # 모델별 프롬프트 설정
    if not prompt:
        if 'florence' in model.config.name_or_path:
            prompt = "<CAPTION>"
        else:
            prompt = "The image shows"
    
    # 배치 처리로 캡션 생성
    generated_texts = []
    for i in range(0, len(croped_pil_image), batch_size):
        batch = croped_pil_image[i:i+batch_size]
        inputs = processor(images=batch, text=[prompt]*len(batch), return_tensors="pt").to(device=device)
        
        if 'florence' in model.config.name_or_path:
            generated_ids = model.generate(input_ids=inputs["input_ids"], pixel_values=inputs["pixel_values"], max_new_tokens=20, num_beams=1, do_sample=False)
        else:
            generated_ids = model.generate(**inputs, max_length=100, num_beams=5, no_repeat_ngram_size=2, early_stopping=True, num_return_sequences=1)
        
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)
        generated_text = [gen.strip() for gen in generated_text]
        generated_texts.extend(generated_text)
    
    return generated_texts
```

### 3. OCR 설정 개선

**파일**: `util/utils.py` - `check_ocr_box()`

```python
def check_ocr_box(image_source: Union[str, Image.Image], display_img = True, output_bb_format='xywh', goal_filtering=None, easyocr_args=None, use_paddleocr=False):
    if use_paddleocr:
        # PaddleOCR 사용 (한국어 지원)
        if easyocr_args is None:
            text_threshold = 0.5
        else:
            text_threshold = easyocr_args['text_threshold']
        result = paddle_ocr.ocr(image_np, cls=False)[0]
        coord = [item[0] for item in result if item[1][1] > text_threshold]
        text = [item[1][0] for item in result if item[1][1] > text_threshold]
    else:
        # EasyOCR 사용 (한국어 + 영어)
        if easyocr_args is None:
            easyocr_args = {}
        result = reader.readtext(image_np, **easyocr_args)
        coord = [item[0] for item in result]
        text = [item[1] for item in result]
```

## 최종 성과 분석

### 📊 성능 지표
- **UI 요소 감지**: 0개 → 127개 (완전 성공!)
- **OCR 텍스트**: 102개 (한국어 + 영어)
- **캡션 생성**: 성공 (BLIP2 영어 설명)
- **처리 시간**: ~79초 (OCR 3초 + SOM 76초)

### 🎯 세부 분석
- **텍스트 요소**: 79개 (OCR 기반)
- **SOM + OCR 결합**: 20개 (한국어 UI 요소)
- **SOM + BLIP2 캡션**: 27개 (영어 설명)
- **총 클릭 가능 요소**: 127개

### 🤖 BLIP2 캡션 예시
- "The image shows the number seven in korean"
- "The image shows a red line that is going up and down"
- "The image shows a graph of the stock market"

## 실행 방법

### 1. 기본 실행
```bash
python omniparser_demo.py -i toss_page.png -o toss_blip2_success --caption-model blip2 --threshold 0.02
```

### 2. 단계별 실행
```bash
# 1단계: 한국어 OCR 지원
python steps/step3_korean_ocr_support.py

# 2단계: OCR 민감도 개선
python steps/step4_improved_ocr_sensitivity.py

# 3단계: BLIP2 모델 전환
python steps/step5_blip2_model_switch.py
```

## 결론

한글 UI 파악을 위한 OCR → BLIP2 전환은 다음과 같은 성과를 달성했습니다:

1. **한국어 텍스트 인식**: EasyOCR 한국어 지원으로 70%+ 감지율 달성
2. **OCR 민감도 개선**: 임계값 조정으로 작은 텍스트까지 감지
3. **BLIP2 모델 전환**: Florence2 호환성 문제 해결로 캡션 생성 성공
4. **최종 성과**: 127개 UI 요소 감지로 완전한 한글 UI 파악 달성

이러한 개선을 통해 OmniParser는 한글 UI 환경에서도 효과적으로 작동할 수 있게 되었습니다. 