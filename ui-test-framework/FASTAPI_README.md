# Qwen2VL FastAPI 서버

Qwen2VL 모델을 사용하여 이미지에서 클릭 가능한 요소들을 찾아 쉼표로 구분된 문자열로 반환하는 FastAPI 서버입니다.

## 🚀 주요 기능

- **Base64 이미지 처리**: 클라이언트에서 base64로 인코딩된 이미지를 받아 처리
- **클릭 요소 추출**: Qwen2VL을 사용하여 클릭 가능한 UI 요소들을 식별
- **간단한 응답**: 쉼표로 구분된 문자열 형태로 결과 반환
- **RESTful API**: 표준 HTTP 프로토콜 사용
- **CORS 지원**: 웹 브라우저에서 직접 호출 가능
- **자동 문서화**: FastAPI 자동 생성 API 문서

## 📦 설치 및 설정

### 1. 필요 패키지 설치

```bash
# ui-test 가상환경 활성화
cd ui-test
source bin/activate  # Linux/Mac
# 또는
# Scripts\activate  # Windows

# FastAPI 관련 패키지 설치
pip install -r requirements_fastapi.txt
```

### 2. 서버 실행

```bash
# 직접 실행
python qwen2vl_fastapi_server.py

# 또는 uvicorn으로 실행
uvicorn qwen2vl_fastapi_server:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 서버 확인

서버가 실행되면 다음 주소들에서 확인할 수 있습니다:

- **메인 페이지**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **상태 확인**: http://localhost:8000/health

## 🔧 API 사용법

### 엔드포인트

#### 1. `GET /` - 서버 정보
```json
{
  "message": "Qwen2VL 클릭 요소 분석 API",
  "version": "1.0.0",
  "endpoints": {
    "POST /analyze": "이미지 분석",
    "GET /health": "서버 상태 확인"
  }
}
```

#### 2. `GET /health` - 서버 상태 확인
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda"
}
```

#### 3. `POST /analyze` - 이미지 분석 (메인 기능)

**요청 형식:**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "context": "토스 증권 앱 화면"
}
```

**응답 형식:**
```json
{
  "clickable_elements": "로그인 버튼, 회원가입 링크, 메뉴 아이콘, 검색 버튼, 설정",
  "processing_time": 2.34,
  "success": true,
  "error_message": null
}
```

### Python 클라이언트 예제

```python
import base64
import requests

# 이미지를 base64로 인코딩
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# API 호출
def analyze_image(image_path, context=""):
    base64_image = image_to_base64(image_path)
    
    response = requests.post(
        "http://localhost:8000/analyze",
        json={
            "image_base64": base64_image,
            "context": context
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"클릭 요소들: {result['clickable_elements']}")
        return result
    else:
        print(f"오류: {response.status_code}")
        return None

# 사용 예제
result = analyze_image("screenshot.png", "토스 증권 메인 화면")
```

### JavaScript/웹 브라우저 예제

```javascript
// 파일을 base64로 변환
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = error => reject(error);
    });
}

// API 호출
async function analyzeImage(file, context = "") {
    try {
        const base64Image = await fileToBase64(file);
        
        const response = await fetch('http://localhost:8000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image_base64: base64Image,
                context: context
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('클릭 요소들:', result.clickable_elements);
            return result.clickable_elements;
        } else {
            console.error('분석 실패:', result.error_message);
            return null;
        }
    } catch (error) {
        console.error('요청 실패:', error);
        return null;
    }
}

// 사용 예제 (파일 입력에서)
const fileInput = document.getElementById('imageInput');
fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        const elements = await analyzeImage(file, "웹 애플리케이션 화면");
        // 결과 처리...
    }
});
```

## 🧪 테스트

### 1. 테스트 클라이언트 실행

```bash
python test_fastapi_client.py
```

이 스크립트는 다음 기능을 제공합니다:
- 서버 상태 자동 확인
- 샘플 이미지들로 자동 테스트
- 대화형 이미지 분석 테스트

### 2. 수동 테스트

```bash
# 서버 상태 확인
curl http://localhost:8000/health

# 이미지 분석 (base64 인코딩된 이미지 필요)
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"image_base64":"iVBORw0KGgoAAAANSUhEUgAA...","context":"테스트 화면"}'
```

### 3. 웹 브라우저 테스트

http://localhost:8000/docs 에서 Swagger UI를 통해 직접 테스트할 수 있습니다.

## ⚙️ 설정 및 최적화

### 디바이스 설정

서버는 자동으로 최적의 디바이스를 선택합니다:
- CUDA GPU (사용 가능한 경우)
- Apple Silicon MPS (Mac에서)
- CPU (기본값)

### 성능 최적화

```python
# 서버 시작 시 다음 설정들이 자동 적용됩니다:
torch.backends.cuda.enable_mem_efficient_sdp(False)
torch.backends.cuda.enable_flash_sdp(False)

# 모델 생성 파라미터 조정 (qwen2vl_fastapi_server.py에서):
max_new_tokens=300  # 응답 길이 제한
do_sample=False     # 결정적 생성
repetition_penalty=1.2  # 반복 방지
```

### 프로덕션 설정

```bash
# 프로덕션 환경에서는 다음과 같이 실행:
uvicorn qwen2vl_fastapi_server:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --reload False \
    --log-level info
```

**주의사항:**
- GPU 메모리가 부족한 경우 workers 수를 1로 유지
- Qwen2VL 모델은 메모리를 많이 사용하므로 단일 워커 권장

## 🔒 보안 고려사항

### CORS 설정

현재 모든 도메인에서의 접근을 허용하고 있습니다. 프로덕션에서는 특정 도메인만 허용하도록 수정하세요:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

### 입력 검증

- 이미지 크기 제한 (현재 자동 처리됨)
- Base64 형식 검증 (구현됨)
- 요청 빈도 제한 (필요시 추가)

## 🐛 트러블슈팅

### 1. 모델 로딩 실패

```
❌ 모델 로딩 실패: OutOfMemoryError
```

**해결방법:**
- GPU 메모리 확인: `nvidia-smi`
- 다른 프로세스 종료
- CPU 모드로 실행: `device="cpu"`

### 2. 서버 연결 실패

```
❌ 서버 연결 실패: Connection refused
```

**해결방법:**
- 서버가 실행 중인지 확인
- 포트 8000이 사용 중인지 확인: `lsof -i :8000`
- 방화벽 설정 확인

### 3. 이미지 디코딩 실패

```
❌ 이미지 디코딩 실패: Invalid base64
```

**해결방법:**
- Base64 인코딩 확인
- 이미지 헤더 제거 확인 (`data:image/png;base64,` 부분)
- 지원되는 이미지 형식: PNG, JPEG, GIF, BMP

### 4. 반복 응답 문제

모델이 같은 내용을 반복하는 경우:
- `repetition_penalty` 값 증가 (현재 1.2)
- `max_new_tokens` 값 감소 (현재 300)
- `do_sample=False` 유지

## 📈 모니터링

### 로그 확인

```bash
# 서버 로그 실시간 확인
tail -f server.log

# 특정 오류 검색
grep "ERROR" server.log
```

### 성능 모니터링

```bash
# GPU 사용량 모니터링
watch -n 1 nvidia-smi

# 메모리 사용량 확인
htop
```

## 🔄 업데이트 및 유지보수

### 모델 업데이트

```bash
# 최신 모델로 업데이트
pip install --upgrade transformers
pip install --upgrade qwen-vl-utils
```

### 서버 재시작

```bash
# 서버 안전 종료
pkill -f qwen2vl_fastapi_server

# 서버 재시작
python qwen2vl_fastapi_server.py
```

## 📞 지원

문제가 발생하거나 개선 사항이 있으면:

1. 로그 파일 확인
2. 테스트 클라이언트로 재현 테스트
3. GPU/메모리 상태 확인
4. 이슈 리포트 작성

---

**참고**: 이 서버는 Qwen2VL-2B-Instruct 모델을 기반으로 하며, 클릭 가능한 UI 요소 식별에 특화되어 있습니다. 