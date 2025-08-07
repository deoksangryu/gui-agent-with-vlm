import ast
from io import BytesIO
import requests
import torch
from PIL import Image, ImageDraw
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor

def draw_point(image_input, point=None, radius=5):
    """
    이미지에 포인트를 그리는 함수
    
    Args:
        image_input: 이미지 경로(str) 또는 PIL Image 객체
        point: [x, y] 좌표 (0~1 사이의 상대 좌표)
        radius: 포인트의 반지름 (픽셀 단위)
    
    Returns:
        PIL Image: 포인트가 그려진 이미지
    """
    # 이미지 로드
    if isinstance(image_input, str):
        if image_input.startswith('http'):
            response = requests.get(image_input)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_input)
    else:
        image = image_input.copy()  # 원본 이미지 보호를 위해 복사본 사용

    # 포인트가 제공된 경우 그리기
    if point:
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
            width=2
        )
        
        # 중심점에 작은 점 추가 (더 정확한 위치 표시)
        draw.ellipse(
            (x - 1, y - 1, x + 1, y + 1), 
            fill='white'
        )
        
        print(f"포인트 그리기 완료: 절대 좌표 ({x:.1f}, {y:.1f}), 상대 좌표 ({point[0]:.3f}, {point[1]:.3f})")
    
    return image

def save_result_image(original_image_path, point, output_path="result_with_point.png"):
    """
    원본 이미지에 포인트를 그리고 결과를 저장하는 함수
    
    Args:
        original_image_path: 원본 이미지 경로
        point: 그릴 포인트의 좌표 [x, y]
        output_path: 저장할 파일 경로
    """
    # 포인트가 그려진 이미지 생성
    result_image = draw_point(original_image_path, point, radius=10)
    
    # 결과 이미지 저장
    result_image.save(output_path)
    print(f"포인트가 표시된 이미지가 저장되었습니다: {output_path}")
    
    return result_image

model = Qwen2VLForConditionalGeneration.from_pretrained(
    "showlab/ShowUI-2B",
    torch_dtype=torch.bfloat16,
    device_map="cpu"
)

min_pixels = 256*28*28
max_pixels = 1344*28*28
size={"shortest_edge": min_pixels, "longest_edge": max_pixels}

processor = AutoProcessor.from_pretrained("showlab/ShowUI-2B", min_pixels=min_pixels, max_pixels=max_pixels, size=size)
img_url = 'test_screenshot.png'
query = "1일"

_SYSTEM = "Based on the screenshot of the page, I give a text description and you give its corresponding location. The coordinate represents a clickable location [x, y] for an element, which is a relative coordinate on the screenshot, scaled from 0 to 1."
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": _SYSTEM},
            {"type": "image", "image": img_url, "min_pixels": min_pixels, "max_pixels": max_pixels},
            {"type": "text", "text": query}
        ],
    }
]

text = processor.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True,
)
image_inputs, video_inputs = process_vision_info(messages)
inputs = processor(
    text=[text],
    images=image_inputs,
    videos=video_inputs,
    padding=True,
    return_tensors="pt",
)
inputs = inputs.to("cpu")

generated_ids = model.generate(**inputs, max_new_tokens=128)
generated_ids_trimmed = [
    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text = processor.batch_decode(
    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
)[0]

click_xy = ast.literal_eval(output_text)
# [0.73, 0.21]
print(f"감지된 클릭 좌표: {click_xy}")

# 원본 이미지를 기반으로 새 이미지에 포인트 그리기
try:
    result_image = save_result_image(img_url, click_xy, "result_with_detected_point.png")
    
    # 추가적으로 이미지 정보 출력
    original_image = Image.open(img_url)
    print(f"원본 이미지 크기: {original_image.size}")
    print(f"감지된 요소 '{query}'의 위치가 빨간색 점으로 표시되었습니다.")
    
    # 선택적으로 이미지 미리보기 (Jupyter 환경이나 GUI 환경에서 사용)
    try:
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # 원본 이미지
        ax1.imshow(original_image)
        ax1.set_title(f"원본 이미지: {img_url}")
        ax1.axis('off')
        
        # 포인트가 표시된 이미지
        ax2.imshow(result_image)
        ax2.set_title(f"감지된 위치: '{query}' at {click_xy}")
        ax2.axis('off')
        
        plt.tight_layout()
        plt.savefig("comparison_result.png", dpi=150, bbox_inches='tight')
        plt.show()
        print("비교 이미지가 저장되었습니다: comparison_result.png")
        
    except ImportError:
        print("matplotlib이 설치되지 않아 이미지 미리보기를 건너뜁니다.")
        print("결과 확인을 위해 'result_with_detected_point.png' 파일을 확인하세요.")
        
except Exception as e:
    print(f"이미지 처리 중 오류 발생: {e}")
    # 오류 발생 시에도 기본 draw_point 함수 실행
    draw_point(img_url, click_xy, 10)