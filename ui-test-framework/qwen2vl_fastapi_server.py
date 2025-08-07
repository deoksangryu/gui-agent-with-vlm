"""
Qwen2VL FastAPI 서버

클라이언트로부터 base64 이미지를 받아서 클릭 가능한 요소들을 
쉼표로 구분된 문자열로 반환하는 FastAPI 서버입니다.

사용법:
    uvicorn qwen2vl_fastapi_server:app --host 0.0.0.0 --port 8000
"""

import base64
import io
import torch
import time
from typing import Optional
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

# GPU 최적화 설정
torch.backends.cuda.enable_mem_efficient_sdp(False)
torch.backends.cuda.enable_flash_sdp(False)

# FastAPI 앱 초기화
app = FastAPI(
    title="Qwen2VL 클릭 요소 분석 API",
    description="클릭할 요소들을 ,로 구분된 문자열로 정리",
    version="1.0.0"
)

# CORS 설정 (필요에 따라 조정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영환경에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청/응답 모델
class ImageAnalysisRequest(BaseModel):
    """이미지 분석 요청 모델"""
    image_base64: str
    context: Optional[str] = ""  # 선택적 컨텍스트 정보

class ImageAnalysisResponse(BaseModel):
    """이미지 분석 응답 모델"""
    clickable_elements: str
    processing_time: float
    success: bool
    error_message: Optional[str] = None

# 전역 모델 변수
model = None
processor = None
device = None

class Qwen2VLAnalyzer:
    """Qwen2VL 분석기 클래스"""
    
    def __init__(self, model_name="Qwen/Qwen2-VL-2B-Instruct", device="auto"):
        """분석기 초기화"""
        print("🎯 Qwen2VL 분석기 초기화 중...")
        
        # 이미지 처리 설정
        self.min_pixels = 256 * 28 * 28
        self.max_pixels = 1344 * 28 * 28
        
        # 디바이스 설정
        if device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device
        
        print(f"📱 사용 디바이스: {self.device}")
        
        # 프로세서 및 모델 로드
        self.processor = AutoProcessor.from_pretrained(
            model_name,
            min_pixels=self.min_pixels,
            max_pixels=self.max_pixels
        )
        
        if self.device == "cpu":
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                device_map="cpu"
            )
        else:
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.bfloat16,
                device_map=self.device
            )
        
        print("✅ Qwen2VL 분석기 준비 완료!")
    
    def analyze_clickable_elements(self, image: Image.Image, context: str = "") -> str:
        """
        이미지에서 클릭 가능한 요소들을 분석하여 쉼표로 구분된 문자열로 반환
        
        Args:
            image: PIL Image 객체
            context: 선택적 컨텍스트 정보
            
        Returns:
            str: 클릭 가능한 요소들을 쉼표로 구분한 문자열
        """
        
        # 더 명확하고 구체적인 프롬프트
        prompt = f"""이 스크린샷에서 실제로 클릭할 수 있는 UI 요소들만 찾아서 쉼표로 구분된 하나의 문자열로 답해주세요.

클릭 가능한 요소란:
- 버튼 (로그인, 검색, 메뉴 등)
- 링크 (텍스트 링크, 종목명 링크 등)
- 아이콘 (네비게이션, 설정 등)
- 탭 메뉴
- 드롭다운 메뉴

클릭할 수 없는 단순 텍스트나 숫자는 제외하고, 오직 상호작용 가능한 요소들만 나열해주세요.

출력 형식: 요소1, 요소2, 요소3, ...

{f"화면 정보: {context}" if context.strip() else ""}"""
        
        try:
            # 메시지 구성
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "image": image,
                            "min_pixels": self.min_pixels,
                            "max_pixels": self.max_pixels,
                        },
                    ],
                }
            ]
            
            # 템플릿 적용 및 처리
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            image_inputs, video_inputs = process_vision_info(messages)
            
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            
            inputs = inputs.to(self.device)
            
            # 응답 생성 (더 자세한 응답을 위한 설정)
            generated_ids = self.model.generate(
                **inputs, 
                max_new_tokens=2000,  # 더 긴 응답을 위해 증가
                do_sample=True,  # 샘플링 활성화
                temperature=0.3,  # 적당한 창의성
                top_p=0.9,
                repetition_penalty=1.1,  # 반복 방지 (너무 높지 않게)
                pad_token_id=self.processor.tokenizer.eos_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id
            )
            
            # 결과 디코딩
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )[0]
            
            # 결과 정리 (더 관대한 길이 제한)
            result = output_text.strip()
            # 여러 줄인 경우 첫 번째 문단까지만 사용
            if '\n\n' in result:
                result = result.split('\n\n')[0]
            if len(result) > 1500:  # 더 긴 응답 허용
                result = result[:1500] + "..."
            
            return result
            
        except Exception as e:
            raise Exception(f"분석 중 오류 발생: {str(e)}")

# 전역 분석기 초기화
analyzer = None

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 로드"""
    global analyzer
    try:
        print("🚀 FastAPI 서버 시작 - 모델 로딩 중...")
        analyzer = Qwen2VLAnalyzer()
        print("✅ 모델 로딩 완료!")
    except Exception as e:
        print(f"❌ 모델 로딩 실패: {e}")
        raise

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Qwen2VL 클릭 요소 분석 API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "이미지 분석",
            "GET /health": "서버 상태 확인"
        }
    }

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    global analyzer
    return {
        "status": "healthy" if analyzer is not None else "not_ready",
        "model_loaded": analyzer is not None,
        "device": analyzer.device if analyzer else "unknown"
    }

@app.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """
    이미지 분석 엔드포인트
    
    Args:
        request: base64 인코딩된 이미지와 선택적 컨텍스트
        
    Returns:
        ImageAnalysisResponse: 클릭 가능한 요소들의 쉼표 구분 문자열
    """
    global analyzer
    
    if analyzer is None:
        raise HTTPException(status_code=503, detail="모델이 아직 로딩되지 않았습니다")
    
    start_time = time.time()
    
    try:
        # Base64 이미지 디코딩
        try:
            # base64 헤더 제거 (data:image/png;base64, 등)
            if ',' in request.image_base64:
                base64_data = request.image_base64.split(',')[1]
            else:
                base64_data = request.image_base64
            
            # Base64 디코딩
            image_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(image_data))
            
            # RGBA를 RGB로 변환 (필요한 경우)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"이미지 디코딩 실패: {str(e)}")
        
        # 이미지 분석 실행
        try:
            clickable_elements = analyzer.analyze_clickable_elements(image, request.context)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"이미지 분석 실패: {str(e)}")
        
        processing_time = time.time() - start_time
        
        return ImageAnalysisResponse(
            clickable_elements=clickable_elements,
            processing_time=processing_time,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        return ImageAnalysisResponse(
            clickable_elements="",
            processing_time=processing_time,
            success=False,
            error_message=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    
    print("🌐 Qwen2VL FastAPI 서버 시작")
    print("📍 서버 주소: http://localhost:8000")
    print("📖 API 문서: http://localhost:8000/docs")
    
    uvicorn.run(
        "qwen2vl_fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 프로덕션에서는 False
        log_level="info"
    ) 