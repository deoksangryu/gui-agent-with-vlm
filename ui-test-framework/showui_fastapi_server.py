import ast
import base64
import io
import os
import time
import traceback
from io import BytesIO
from pathlib import Path
from typing import Optional, Dict, Any

import requests
import torch
from PIL import Image, ImageDraw
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

# 화면 클릭을 위한 라이브러리
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    # 화면 클릭 시 안전장치 (갑작스런 마우스 이동 방지)
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1  # 각 동작 간 0.1초 대기
    print("✅ pyautogui 사용 가능")
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️ pyautogui가 설치되지 않음. 클릭 기능을 사용하려면 'pip install pyautogui' 실행")

# =============================================================================
# FastAPI 애플리케이션 설정
# =============================================================================

app = FastAPI(
    title="ShowUI FastAPI 서버",
    description="이미지에서 UI 요소의 위치를 찾는 ShowUI 모델 기반 API 서버",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정 (프론트엔드에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Pydantic 모델 정의
# =============================================================================

class ClickRequest(BaseModel):
    """클릭 위치 찾기 요청 모델"""
    image_base64: str
    query: str  # 찾고자 하는 UI 요소 설명
    
class ClickResponse(BaseModel):
    """클릭 위치 찾기 응답 모델"""
    success: bool
    coordinates: Optional[list] = None  # [x, y] 상대 좌표 (0~1)
    absolute_coordinates: Optional[list] = None  # [x, y] 절대 좌표 (픽셀)
    query: str
    image_size: Optional[list] = None  # [width, height]
    result_image_filename: Optional[str] = None  # 결과 이미지 파일명
    processing_time: Optional[float] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """서버 상태 응답 모델"""
    status: str
    model_loaded: bool
    gpu_available: bool
    timestamp: str

class BrowserInfo(BaseModel):
    """브라우저 정보 모델"""
    window: Dict[str, Any]
    screen: Dict[str, Any] 
    chatbot: Dict[str, Any]
    userAgent: str
    timestamp: str

class ServerClickRequest(BaseModel):
    """서버 클릭 요청 모델"""
    x: float  # 화면 절대 x 좌표
    y: float  # 화면 절대 y 좌표
    browserInfo: BrowserInfo
    action: str
    timestamp: str

class ServerClickResponse(BaseModel):
    """서버 클릭 응답 모델"""
    success: bool
    message: str
    clicked_coordinates: list  # [x, y] 실제 클릭된 좌표
    timestamp: str
    error: Optional[str] = None

class ServerScreenshotRequest(BaseModel):
    """서버 스크린샷 및 UI 찾기 요청 모델"""
    query: str
    auto_click: bool = True

class ServerScreenshotResponse(BaseModel):
    """서버 스크린샷 응답 모델"""
    success: bool
    query: str
    coordinates: Optional[list] = None  # [x, y] 상대 좌표 (0~1)
    absolute_coordinates: Optional[list] = None  # [x, y] 절대 좌표 (픽셀)
    image_size: Optional[list] = None  # [width, height]
    result_image_filename: Optional[str] = None
    processing_time: Optional[float] = None
    click_executed: Optional[bool] = None
    error: Optional[str] = None

# =============================================================================
# 글로벌 변수 및 모델 초기화
# =============================================================================

model = None
processor = None
is_model_loaded = False

# ShowUI 시스템 프롬프트
_SYSTEM = "Based on the screenshot of the page, I give a text description and you give its corresponding location. The coordinate represents a clickable location [x, y] for an element, which is a relative coordinate on the screenshot, scaled from 0 to 1."

# 이미지 처리 파라미터
min_pixels = 256*28*28
max_pixels = 1344*28*28
size = {"shortest_edge": min_pixels, "longest_edge": max_pixels}

# 결과 이미지 저장 디렉토리
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# =============================================================================
# 유틸리티 함수들
# =============================================================================

def draw_point(image_input, point=None, radius=10):
    """
    이미지에 포인트를 그리는 함수
    
    Args:
        image_input: PIL Image 객체
        point: [x, y] 좌표 (0~1 사이의 상대 좌표)
        radius: 포인트의 반지름 (픽셀 단위)
    
    Returns:
        PIL Image: 포인트가 그려진 이미지
    """
    if point is None:
        return image_input
        
    # 원본 이미지 보호를 위해 복사본 사용
    image = image_input.copy()
    
    # 상대 좌표를 절대 좌표로 변환
    x = point[0] * image.width
    y = point[1] * image.height
    
    # 이미지에 포인트 그리기
    draw = ImageDraw.Draw(image)
    
    # 빨간색 원 그리기
    draw.ellipse(
        (x - radius, y - radius, x + radius, y + radius), 
        fill='red', 
        outline='darkred',
        width=3
    )
    
    # 중심점에 작은 점 추가 (더 정확한 위치 표시)
    draw.ellipse(
        (x - 2, y - 2, x + 2, y + 2), 
        fill='white'
    )
    
    return image

def base64_to_pil(base64_string: str) -> Image.Image:
    """Base64 문자열을 PIL Image로 변환"""
    try:
        # Base64 데이터에서 헤더 제거 (data:image/png;base64, 등)
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        
        # RGB 모드로 변환 (투명도 채널 제거)
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                background.paste(image, mask=image.split()[-1])
            else:
                background.paste(image)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
            
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"이미지 디코딩 실패: {str(e)}")

def capture_server_screenshot() -> Image.Image:
    """
    서버에서 전체 화면 스크린샷 캡처
    
    Returns:
        PIL.Image: 캡처된 전체 화면 이미지
    """
    if not PYAUTOGUI_AVAILABLE:
        raise HTTPException(status_code=503, detail="pyautogui가 설치되지 않아 스크린샷을 캡처할 수 없습니다")
    
    try:
        # 전체 화면 스크린샷 캡처
        screenshot = pyautogui.screenshot()
        
        # PIL Image로 변환 (이미 PIL Image이지만 확실히 하기 위해)
        if not isinstance(screenshot, Image.Image):
            screenshot = Image.fromarray(screenshot)
        
        # RGB 모드로 변환
        if screenshot.mode != 'RGB':
            screenshot = screenshot.convert('RGB')
        
        print(f"📸 서버 스크린샷 캡처 완료: {screenshot.size}")
        return screenshot
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스크린샷 캡처 실패: {str(e)}")

def init_model():
    """모델 초기화"""
    global model, processor, is_model_loaded
    
    try:
        print("ShowUI 모델 로딩 중...")
        
        # GPU 사용 가능 여부 확인
        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.bfloat16 if device == "cuda" else torch.float32
        
        print(f"사용 디바이스: {device}")
        print(f"데이터 타입: {torch_dtype}")
        
        # 모델 로드
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            "showlab/ShowUI-2B",
            torch_dtype=torch_dtype,
            device_map=device
        )
        
        # 프로세서 로드
        processor = AutoProcessor.from_pretrained(
            "showlab/ShowUI-2B", 
            min_pixels=min_pixels, 
            max_pixels=max_pixels, 
            size=size
        )
        
        is_model_loaded = True
        print("✅ ShowUI 모델 로딩 완료!")
        
    except Exception as e:
        print(f"❌ 모델 로딩 실패: {str(e)}")
        traceback.print_exc()
        is_model_loaded = False

# =============================================================================
# API 엔드포인트들
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 초기화"""
    init_model()

@app.get("/", response_model=Dict[str, str])
async def root():
    """루트 엔드포인트"""
    return {
        "message": "ShowUI FastAPI 서버가 실행 중입니다",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """서버 상태 확인"""
    return HealthResponse(
        status="healthy" if is_model_loaded else "model_not_loaded",
        model_loaded=is_model_loaded,
        gpu_available=torch.cuda.is_available(),
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    )

@app.post("/find_click_position", response_model=ClickResponse)
async def find_click_position(request: ClickRequest):
    """
    이미지에서 UI 요소의 클릭 위치를 찾는 엔드포인트
    """
    if not is_model_loaded:
        raise HTTPException(status_code=503, detail="모델이 로드되지 않았습니다. /health 엔드포인트로 상태를 확인하세요.")
    
    start_time = time.time()
    
    try:
        # Base64 이미지를 PIL Image로 변환
        image = base64_to_pil(request.image_base64)
        image_size = [image.width, image.height]
        
        # 디버깅용: 입력 이미지 저장
        debug_image_path = RESULTS_DIR / f"debug_input_{int(time.time())}.png"
        image.save(debug_image_path)
        print(f"🖼️ 디버깅용 입력 이미지 저장: {debug_image_path}")
        print(f"📏 이미지 크기: {image.width} × {image.height}")
        print(f"🎯 분석 대상: {request.query}")
        
        # 메시지 구성
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _SYSTEM},
                    {"type": "image", "image": image, "min_pixels": min_pixels, "max_pixels": max_pixels},
                    {"type": "text", "text": request.query}
                ],
            }
        ]
        
        # 텍스트 템플릿 적용
        text = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
        )
        
        # 이미지 및 비디오 입력 처리
        image_inputs, video_inputs = process_vision_info(messages)
        
        # 모델 입력 준비
        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        
        # GPU 사용 시 입력을 GPU로 이동
        device = next(model.parameters()).device
        inputs = inputs.to(device)
        
        # 모델 추론
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs, 
                max_new_tokens=128,
                do_sample=True,
                temperature=0.1,
                top_p=0.9,
                repetition_penalty=1.05
            )
        
        # 생성된 토큰만 추출
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        # 텍스트 디코딩
        output_text = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        
        print(f"모델 출력: {output_text}")
        
        # 좌표 파싱
        try:
            coordinates = ast.literal_eval(output_text.strip())
            if not isinstance(coordinates, list) or len(coordinates) != 2:
                raise ValueError("좌표 형식이 올바르지 않습니다")
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"좌표 파싱 실패: {output_text}")
        
        # 절대 좌표 계산
        absolute_coordinates = [
            coordinates[0] * image.width,
            coordinates[1] * image.height
        ]
        
        # 디버깅: 좌표 변환 과정 출력
        print(f"🔍 좌표 변환 디버깅:")
        print(f"   • ShowUI 정규화 좌표: [{coordinates[0]:.3f}, {coordinates[1]:.3f}]")
        print(f"   • 분석된 이미지 크기: {image.width} × {image.height}")
        print(f"   • 계산된 이미지 픽셀 좌표: [{absolute_coordinates[0]:.1f}, {absolute_coordinates[1]:.1f}]")
        
        # Retina/HiDPI 스케일링 감지 및 보정
        # 이미지 크기가 일반적인 화면 해상도의 2배라면 Retina 디스플레이
        expected_max_width = 3000  # 일반적인 최대 해상도
        expected_max_height = 2000
        
        if image.width > expected_max_width or image.height > expected_max_height:
            # Retina 디스플레이로 추정 - 좌표를 절반으로 축소
            scale_factor = 0.5
            absolute_coordinates[0] *= scale_factor
            absolute_coordinates[1] *= scale_factor
            print(f"   🖥️ Retina/HiDPI 감지: 좌표를 {scale_factor}배 축소")
            print(f"   • 보정된 화면 좌표: [{absolute_coordinates[0]:.1f}, {absolute_coordinates[1]:.1f}]")
        
        # 결과 이미지 생성 및 저장
        result_image = draw_point(image, coordinates, radius=15)
        result_filename = f"showui_result_{int(time.time())}.png"
        result_path = RESULTS_DIR / result_filename
        result_image.save(result_path)
        
        processing_time = time.time() - start_time
        
        return ClickResponse(
            success=True,
            coordinates=coordinates,
            absolute_coordinates=absolute_coordinates,
            query=request.query,
            image_size=image_size,
            result_image_filename=result_filename,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"처리 중 오류 발생: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        
        return ClickResponse(
            success=False,
            query=request.query,
            error=error_msg,
            processing_time=processing_time
        )

@app.get("/download_result/{filename}")
async def download_result(filename: str):
    """결과 이미지 다운로드"""
    file_path = RESULTS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="image/png"
    )

@app.post("/upload_and_find")
async def upload_and_find(
    file: UploadFile = File(...),
    query: str = "button"
):
    """
    파일 업로드 방식으로 클릭 위치 찾기
    """
    if not is_model_loaded:
        raise HTTPException(status_code=503, detail="모델이 로드되지 않았습니다")
    
    try:
        # 업로드된 파일 읽기
        contents = await file.read()
        
        # Base64로 인코딩
        image_base64 = base64.b64encode(contents).decode('utf-8')
        
        # 기존 엔드포인트 재사용
        request = ClickRequest(
            image_base64=image_base64,
            query=query
        )
        
        return await find_click_position(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 처리 실패: {str(e)}")

@app.get("/results")
async def list_results():
    """저장된 결과 이미지 목록 조회"""
    results = []
    for file_path in RESULTS_DIR.glob("*.png"):
        stat = file_path.stat()
        results.append({
            "filename": file_path.name,
            "size": stat.st_size,
            "created": time.ctime(stat.st_ctime),
            "download_url": f"/download_result/{file_path.name}"
        })
    
    return {"results": sorted(results, key=lambda x: x["created"], reverse=True)}

@app.post("/api/click-coordinate", response_model=ServerClickResponse)
async def click_coordinate(request: ServerClickRequest):
    """
    화면의 절대 좌표에 클릭 이벤트 발생
    브라우저 내부 좌표를 화면 절대 좌표로 변환하여 정확한 클릭 실행
    """
    if not PYAUTOGUI_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="pyautogui가 설치되지 않아 클릭 기능을 사용할 수 없습니다. 'pip install pyautogui'를 실행하세요."
        )
    
    try:
        start_time = time.time()
        
        # 브라우저 정보 추출
        browser_info = request.browserInfo
        
        # 좌표 변환: ShowUI 절대좌표 (전체 화면 기준) → 화면 절대 좌표
        # ShowUI가 전체 화면 캡처 이미지에서 찾은 좌표는 이미 화면 절대 좌표임
        
        # 전체 화면 캡처 모드: 간단한 좌표 변환
        # ShowUI 정규화 좌표 → 화면 절대 좌표
        
        # macOS/Retina 디스플레이 정보 확인
        screen_width, screen_height = pyautogui.size()
        
        # 브라우저 정보는 디버깅용으로만 사용
        browser_x = browser_info.window["screenX"]
        browser_y = browser_info.window["screenY"]
        chrome_height = browser_info.window["outerHeight"] - browser_info.window["innerHeight"]
        
        # ShowUI가 전체 화면에서 찾은 좌표를 그대로 사용
        # (이미 find_click_position에서 정규화 좌표 × 이미지 크기로 변환됨)
        
        # 하지만 Retina 디스플레이의 경우 이미지 크기가 실제 화면보다 클 수 있음
        # 브라우저에서 보고하는 화면 크기와 실제 pyautogui 화면 크기 비교
        browser_screen_width = browser_info.screen['width']
        browser_screen_height = browser_info.screen['height']
        
        # 추가 Retina 보정이 필요한지 확인
        if (browser_screen_width != screen_width or browser_screen_height != screen_height):
            print(f"   ⚠️ 화면 크기 불일치 감지:")
            print(f"      브라우저 보고: {browser_screen_width} × {browser_screen_height}")
            print(f"      pyautogui 감지: {screen_width} × {screen_height}")
            
            # 브라우저 보고 크기 기준으로 좌표 재조정
            scale_x = screen_width / browser_screen_width
            scale_y = screen_height / browser_screen_height
            
            print(f"      추가 스케일링: X={scale_x:.3f}, Y={scale_y:.3f}")
            
            absolute_x = request.x * scale_x
            absolute_y = request.y * scale_y
            
            print(f"      보정된 좌표: [{absolute_x:.1f}, {absolute_y:.1f}]")
        else:
            absolute_x = request.x
            absolute_y = request.y
            print(f"   ✅ 화면 크기 일치: 좌표 그대로 사용 [{absolute_x:.1f}, {absolute_y:.1f}]")
        
        print(f"📍 좌표 분석 (전체 화면 캡처 모드):")
        print(f"   • ShowUI 화면 절대 좌표: [{request.x:.1f}, {request.y:.1f}]")
        print(f"   • 화면 크기: {screen_width} × {screen_height}")
        print(f"   • 브라우저 위치 (참고): [{browser_x}, {browser_y}] {browser_info.window['outerWidth']}×{browser_info.window['outerHeight']}")
        print(f"   • 최종 사용 좌표: [{absolute_x:.1f}, {absolute_y:.1f}]")
        
        # Retina 스케일링은 위에서 이미 처리됨
        
        # 화면 크기 확인 (이미 위에서 screen_width, screen_height 계산됨)
        if absolute_x < 0 or absolute_y < 0 or absolute_x > screen_width or absolute_y > screen_height:
            raise HTTPException(
                status_code=400, 
                detail=f"변환된 좌표가 화면 범위를 벗어났습니다. "
                       f"계산된 좌표: [{absolute_x:.1f}, {absolute_y:.1f}], "
                       f"화면 크기: {screen_width}x{screen_height}"
            )
        
        print(f"🖱️ 화면 절대 좌표 [{absolute_x:.1f}, {absolute_y:.1f}]에 클릭 실행")
        
        # macOS Y축 좌표계 확인 및 조정
        import platform
        if platform.system() == "Darwin":  # macOS
            # macOS에서는 Y축이 뒤바뀔 수 있음 - 테스트 후 필요시 적용
            # absolute_y = screen_height - absolute_y
            print(f"   🍎 macOS 감지됨 - 현재 Y좌표 사용: {absolute_y:.1f}")
        
        # 실제 클릭 수행
        print(f"🖱️ 최종 클릭 실행: [{absolute_x:.1f}, {absolute_y:.1f}]")
        
        # 클릭 전 마우스 위치 확인
        before_pos = pyautogui.position()
        print(f"   • 클릭 전 마우스 위치: {before_pos}")
        
        pyautogui.click(absolute_x, absolute_y)
        
        # 클릭 후 마우스 위치 확인
        after_pos = pyautogui.position()
        print(f"   • 클릭 후 마우스 위치: {after_pos}")
        
        # 처리 시간 계산
        processing_time = time.time() - start_time
        
        # 스케일링 정보 포함한 메시지 생성
        if browser_info.screen['width'] != screen_width or browser_info.screen['height'] != screen_height:
            scale_info = f", 스케일링 {screen_width/browser_info.screen['width']:.1f}x 적용"
        else:
            scale_info = ""
            
        return ServerClickResponse(
            success=True,
            message=f"ShowUI 좌표 [{request.x:.1f}, {request.y:.1f}] → "
                   f"화면 절대 좌표 [{absolute_x:.1f}, {absolute_y:.1f}] 클릭 완료 "
                   f"(오프셋: +{browser_x}+{chrome_height}{scale_info})",
            clicked_coordinates=[absolute_x, absolute_y],
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"클릭 실행 중 오류 발생: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        
        return ServerClickResponse(
            success=False,
            message="클릭 실패",
            clicked_coordinates=[0, 0],
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            error=error_msg
        )

@app.post("/api/server-screenshot-and-find", response_model=ServerScreenshotResponse)
async def server_screenshot_and_find(request: ServerScreenshotRequest):
    """
    서버에서 전체 화면 스크린샷을 캡처하고 UI 요소를 찾아서 자동 클릭
    """
    if not is_model_loaded:
        raise HTTPException(status_code=503, detail="ShowUI 모델이 로드되지 않았습니다")
    
    start_time = time.time()
    
    try:
        print(f"🎯 서버 스크린샷 + UI 찾기 시작: '{request.query}'")
        
        # 1. 서버에서 전체 화면 스크린샷 캡처
        screenshot = capture_server_screenshot()
        image_size = [screenshot.width, screenshot.height]
        
        # 2. ShowUI로 UI 요소 분석
        # Base64 인코딩 (기존 find_click_position 재사용을 위해)
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # 기존 분석 로직 재사용
        click_request = ClickRequest(
            image_base64=img_base64,
            query=request.query
        )
        
        analysis_result = await find_click_position(click_request)
        
        if not analysis_result.success:
            return ServerScreenshotResponse(
                success=False,
                query=request.query,
                error=analysis_result.error,
                processing_time=time.time() - start_time
            )
        
        # 3. 자동 클릭 실행 (요청된 경우)
        click_executed = False
        if request.auto_click and analysis_result.absolute_coordinates:
            try:
                if not PYAUTOGUI_AVAILABLE:
                    print("⚠️ pyautogui 없음 - 클릭 건너뜀")
                else:
                    x, y = analysis_result.absolute_coordinates
                    print(f"🖱️ 자동 클릭 실행: [{x:.1f}, {y:.1f}]")
                    pyautogui.click(x, y)
                    click_executed = True
                    print("✅ 자동 클릭 완료")
            except Exception as click_error:
                print(f"❌ 자동 클릭 실패: {click_error}")
        
        processing_time = time.time() - start_time
        
        return ServerScreenshotResponse(
            success=True,
            query=request.query,
            coordinates=analysis_result.coordinates,
            absolute_coordinates=analysis_result.absolute_coordinates,
            image_size=analysis_result.image_size,
            result_image_filename=analysis_result.result_image_filename,
            processing_time=processing_time,
            click_executed=click_executed
        )
        
    except Exception as e:
        error_msg = f"서버 스크린샷 분석 실패: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        
        return ServerScreenshotResponse(
            success=False,
            query=request.query,
            error=error_msg,
            processing_time=time.time() - start_time
        )

# =============================================================================
# 서버 실행
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 ShowUI FastAPI 서버 시작 중...")
    print("📚 API 문서: http://localhost:8001/docs")
    print("🔍 Redoc 문서: http://localhost:8001/redoc")
    print("❤️ 서버 상태: http://localhost:8001/health")
    
    uvicorn.run(
        "showui_fastapi_server:app",
        host="0.0.0.0",
        port=8001,
        reload=False,  # 모델 로딩 시간 때문에 False로 설정
        log_level="info"
    ) 