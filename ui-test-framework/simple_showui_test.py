"""
간단한 ShowUI 헬퍼 테스트 버전

반복 생성 문제를 해결하기 위한 최소화된 버전입니다.
"""

import os
import torch
import time
from PIL import Image
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

# GPU 최적화 설정
torch.backends.cuda.enable_mem_efficient_sdp(False)
torch.backends.cuda.enable_flash_sdp(False)

class SimpleShowUIHelper:
    """
    간단한 ShowUI 헬퍼
    """
    
    def __init__(self, model_name="Qwen/Qwen2-VL-2B-Instruct", device="auto"):
        print("🎯 간단한 ShowUI 헬퍼 초기화 중...")
        
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
            
            print("✅ 간단한 ShowUI 헬퍼 준비 완료!")
            
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {e}")
            raise
    
    def analyze_ui_simple(self, image_path, context=""):
        """
        간단한 UI 분석
        """
        
        # 매우 간단한 프롬프트
        prompt = f"""
이 스크린샷에서 클릭할 수 있는 버튼과 입력할 수 있는 필드를 찾아주세요.

각 요소에 대해 간단히:
1. 유형 (버튼/입력필드/링크)
2. 위치 (상단/중앙/하단, 좌측/중앙/우측)
3. 텍스트 내용

웹앱 정보: {context}

간결하게 5개 이하의 주요 요소만 나열해주세요.
"""
        
        try:
            start_time = time.time()
            
            # 이미지 로드
            if isinstance(image_path, str):
                image = Image.open(image_path)
            else:
                image = image_path
            
            # 메시지 구성
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "image": image_path if isinstance(image_path, str) else image,
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
            
            # 응답 생성 (매우 보수적인 설정)
            print("🔄 간단 분석 중...")
            generated_ids = self.model.generate(
                **inputs, 
                max_new_tokens=500,  # 매우 짧게
                do_sample=False,  # 결정적 생성
                repetition_penalty=1.3,  # 반복 방지 강화
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
            
            # 응답 길이 제한 (안전장치)
            if len(output_text) > 1000:
                output_text = output_text[:1000] + "..."
            
            return output_text.strip()
            
        except Exception as e:
            return f"❌ 분석 중 오류 발생: {str(e)}"

def test_simple_helper():
    """
    간단한 테스트 실행
    """
    print("🚀 간단한 ShowUI 헬퍼 테스트")
    print("=" * 40)
    
    try:
        helper = SimpleShowUIHelper()
    except Exception as e:
        print(f"❌ 헬퍼 초기화 실패: {e}")
        return
    
    # 테스트 이미지 확인
    test_images = ["test_screenshot.png", "screenshot.png", "toss_screenshot.png"]
    test_image = None
    
    for img in test_images:
        if os.path.exists(img):
            test_image = img
            break
    
    if not test_image:
        print("⚠️ 테스트 이미지를 찾을 수 없습니다.")
        print("💡 다음 중 하나의 파일을 준비해주세요:")
        for img in test_images:
            print(f"   - {img}")
        return
    
    print(f"📸 테스트 이미지: {test_image}")
    
    # 간단한 분석 실행
    context = "토스증권 메인 화면입니다."
    print(f"💬 컨텍스트: {context}")
    print("\n🔄 간단 UI 분석 실행 중...")
    
    try:
        result = helper.analyze_ui_simple(test_image, context)
        print(f"\n📝 분석 결과:")
        print("="*50)
        print(result)
        print("="*50)
        print("✅ 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    test_simple_helper() 