"""
Qwen2VL FastAPI v1 서버

qwen2vl_webapp_analyzer.py의 기능을 그대로 유지하면서
클라이언트로부터 base64 이미지를 받아 처리하는 FastAPI 서버입니다.
"""

import base64
import io
import os
import torch
import time
import subprocess
import tempfile
from typing import Optional
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
import requests
from io import BytesIO

# 화면 스크린샷을 위한 라이브러리
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    print("✅ pyautogui 사용 가능")
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️ pyautogui가 설치되지 않음. 스크린샷 기능을 사용하려면 'pip install pyautogui' 실행")

# GPU 최적화 설정
torch.backends.cuda.enable_mem_efficient_sdp(False)
torch.backends.cuda.enable_flash_sdp(False)

# FastAPI 앱 초기화
app = FastAPI(
    title="Qwen2VL WebApp Analyzer API v1",
    description="웹 애플리케이션 분석기의 정확한 복제본 - Base64 이미지 지원",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청/응답 모델
class ImageAnalysisRequest(BaseModel):
    """이미지 분석 요청 모델"""
    image_base64: str
    user_context: Optional[str] = ""

class ImageAnalysisResponse(BaseModel):
    """이미지 분석 응답 모델"""
    result: str
    processing_time: float
    success: bool
    error_message: Optional[str] = None

# 서버 스크린샷 분석 모델
class ScreenshotAnalysisRequest(BaseModel):
    """서버 스크린샷 분석 요청"""
    context: Optional[str] = ""

class ScreenshotAnalysisResponse(BaseModel):
    """서버 스크린샷 분석 응답"""
    success: bool
    result: str = ""
    error_message: str = ""
    processing_time: float = 0.0

def capture_server_screenshot() -> Image.Image:
    """
    서버에서 전체 화면 스크린샷 캡처
    
    Returns:
        PIL Image: 캡처된 스크린샷
    """
    try:
        if PYAUTOGUI_AVAILABLE:
            # pyautogui로 스크린샷 캡처
            screenshot = pyautogui.screenshot()
            print(f"📸 스크린샷 캡처 완료: {screenshot.size}")
            return screenshot
        else:
            # macOS의 경우 screencapture 명령어 사용
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_file.close()
            
            subprocess.run(['screencapture', '-x', temp_file.name], check=True)
            screenshot = Image.open(temp_file.name)
            
            # 임시 파일 정리
            os.unlink(temp_file.name)
            
            print(f"📸 스크린샷 캡처 완료: {screenshot.size}")
            return screenshot
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스크린샷 캡처 실패: {str(e)}")

class WebAppAnalyzer:
    """
    웹 애플리케이션 분석기 - webapp analyzer와 동일한 기능
    """
    
    def __init__(self, model_name="Qwen/Qwen2-VL-2B-Instruct", device="auto"):
        """
        웹앱 분석기 초기화
        
        Args:
            model_name: 사용할 모델 이름
            device: 사용할 디바이스 (auto, cpu, cuda, mps 등)
        """
        print("🌐 웹 애플리케이션 분석기 초기화 중...")
        
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
        
        try:
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
            
            print("✅ 웹앱 분석기 준비 완료!")
            
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {e}")
            raise
    
    def load_image(self, image_input):
        """이미지 로드 함수 - webapp analyzer와 동일"""
        if isinstance(image_input, str):
            if image_input.startswith('http'):
                response = requests.get(image_input)
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(image_input)
        else:
            image = image_input
        return image
    
    def analyze_webapp_screenshot(self, image_input, user_context=""):
        """
        웹 애플리케이션 스크린샷 분석 - webapp analyzer와 동일한 로직
        
        Args:
            image_input: 이미지 (PIL Image 객체 또는 경로)
            user_context: 사용자 제공 보충설명
            
        Returns:
            str: 분석 결과
        """
        
        # 기본 시스템 프롬프트 - webapp analyzer와 동일
        system_prompt = """
당신은 웹 애플리케이션 UI/UX 전문 분석가입니다. 
제공된 스크린샷은 웹 애플리케이션의 화면입니다.
현재 화면에 있는 내용을 정리하여 보고서를 작성해주세요.
"""
        
        return self._generate_response(image_input, system_prompt)
    
    def _generate_response(self, image_input, prompt):
        """Qwen2VL 응답 생성 (내부 메서드) - webapp analyzer와 동일"""
        try:
            start_time = time.time()
            
            # 이미지 로드
            image = self.load_image(image_input)
            
            # 메시지 구성
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "image": image_input if isinstance(image_input, str) else image,
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
            
            # 응답 생성 - 타임아웃 방지를 위한 최적화된 파라미터
            print("🔄 웹앱 분석 중...")
            generated_ids = self.model.generate(
                **inputs, 
                max_new_tokens=2000,  # 타임아웃 방지를 위해 감소
                repetition_penalty=1.1,  # 반복 방지
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
            
            end_time = time.time()
            print(f"⏱️ 분석 완료 시간: {end_time - start_time:.2f}초")
            
            return output_text.strip()
            
        except Exception as e:
            return f"❌ 분석 중 오류 발생: {str(e)}"

# 전역 분석기 초기화
analyzer = None

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 로드"""
    global analyzer
    try:
        print("🚀 FastAPI v1 서버 시작 - 모델 로딩 중...")
        analyzer = WebAppAnalyzer()
        print("✅ 모델 로딩 완료!")
    except Exception as e:
        print(f"❌ 모델 로딩 실패: {e}")
        raise

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Qwen2VL WebApp Analyzer API v1",
        "description": "webapp analyzer와 동일한 기능의 FastAPI 서버",
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
    이미지 분석 엔드포인트 - webapp analyzer와 동일한 기능
    
    Args:
        request: base64 인코딩된 이미지와 사용자 컨텍스트
        
    Returns:
        ImageAnalysisResponse: webapp analyzer와 동일한 분석 결과
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
        
        # webapp analyzer와 동일한 분석 실행
        try:
            result = analyzer.analyze_webapp_screenshot(image, request.user_context)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"이미지 분석 실패: {str(e)}")
        
        processing_time = time.time() - start_time
        
        return ImageAnalysisResponse(
            result=result,
            processing_time=processing_time,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        return ImageAnalysisResponse(
            result="",
            processing_time=processing_time,
            success=False,
            error_message=str(e)
        )

@app.post("/analyze-screenshot", response_model=ScreenshotAnalysisResponse)
async def analyze_screenshot(request: ScreenshotAnalysisRequest):
    """
    서버에서 스크린샷 캡처 후 분석
    
    Args:
        request: 분석 컨텍스트 정보
        
    Returns:
        ScreenshotAnalysisResponse: 스크린샷 분석 결과
    """
    global analyzer
    
    if analyzer is None:
        raise HTTPException(status_code=503, detail="모델이 아직 로딩되지 않았습니다")
    
    start_time = time.time()
    
    try:
        print(f"📸 서버 스크린샷 분석 시작: '{request.context}'")
        
        # 1. 서버에서 전체 화면 스크린샷 캡처
        screenshot = capture_server_screenshot()
        
        # 2. Qwen2VL로 스크린샷 분석
        try:
            result = analyzer.analyze_webapp_screenshot(screenshot, request.context)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"이미지 분석 실패: {str(e)}")
        
        processing_time = time.time() - start_time
        print(f"✅ 서버 스크린샷 분석 완료 ({processing_time:.2f}초)")
        
        return ScreenshotAnalysisResponse(
            success=True,
            result=result,
            processing_time=processing_time
        )
        
    except Exception as e:
        error_msg = f"서버 스크린샷 분석 실패: {str(e)}"
        print(f"❌ {error_msg}")
        
        return ScreenshotAnalysisResponse(
            success=False,
            error_message=error_msg,
            processing_time=time.time() - start_time
        )

if __name__ == "__main__":
    import uvicorn
    
    print("🌐 Qwen2VL FastAPI v1 서버 시작")
    print("📍 서버 주소: http://localhost:8000")
    print("📖 API 문서: http://localhost:8000/docs")
    print("🔄 webapp analyzer와 동일한 기능 제공")
    
    uvicorn.run(
        "qwen2vl_fastapi_v1_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    ) 