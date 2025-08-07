"""
Qwen2VL 웹 애플리케이션 분석기

이 스크립트는 웹 애플리케이션 스크린샷 분석에 특화된 Qwen2VL 기반 도구입니다.
사용자의 보충설명을 받아 더 정확하고 맥락적인 분석을 제공합니다.

주요 기능:
1. 웹 애플리케이션 스크린샷 전문 분석
2. 사용자 보충설명 통합 분석
3. 웹 UI/UX 전문 관점 제공
4. 사용자 워크플로우 분석
5. 웹 접근성 및 사용성 평가
"""

import os
import torch
import time
from PIL import Image
from io import BytesIO
import requests
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

# GPU 최적화 설정
torch.backends.cuda.enable_mem_efficient_sdp(False)
torch.backends.cuda.enable_flash_sdp(False)

class WebAppAnalyzer:
    """
    웹 애플리케이션 스크린샷 전문 분석기
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
        """이미지 로드 함수"""
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
        # 기본 시스템 프롬프트
        system_prompt = """
당신은 웹 애플리케이션 UI/UX 전문 분석가입니다. 
제공된 스크린샷은 웹 애플리케이션의 화면입니다.
사용자가 제공한 보충설명과 함께 전문적이고 실용적인 분석을 제공해주세요.
"""
        task_prompt = """
클릭할 요소들을 ,로 구분된 문자열로 정리
"""
        # 사용자 컨텍스트 통합
        if user_context.strip():
            context_section = f"""

【사용자 제공 정보】
{user_context.strip()}

위 정보를 고려하여 더욱 정확하고 맞춤형 분석을 제공해주세요.
"""
            full_prompt = system_prompt + task_prompt + context_section
        else:
            full_prompt = system_prompt + task_prompt
        
        return self._generate_response(image_input, full_prompt)
    
    def _generate_response(self, image_input, prompt):
        """Qwen2VL 응답 생성 (내부 메서드)"""
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
            
            # 응답 생성
            print("🔄 웹앱 분석 중...")
            generated_ids = self.model.generate(
                **inputs, 
                max_new_tokens=4000,  # 더 긴 응답을 위해 증가
                do_sample=True,
                temperature=0.7,
                top_p=0.9
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

def quick_demo():
    """
    빠른 데모 실행
    """
    print("🚀 웹앱 분석기 빠른 데모")
    print("=" * 40)
    
    try:
        analyzer = WebAppAnalyzer()
    except Exception as e:
        print(f"❌ 분석기 초기화 실패: {e}")
        return
    
    # 테스트 이미지
    image_path = "test_screenshot.png"
    
    if not os.path.exists(image_path):
        print(f"⚠️ 테스트 이미지를 찾을 수 없습니다: {image_path}")
        print("💡 'test_screenshot.png' 파일을 준비해주세요.")
        return
    
    # 예제 분석
    print(f"📸 이미지 분석: {image_path}")
    
    # 사용자 컨텍스트 예제
    user_context = "이것은 토스증권 메인 화면입니다."
    
    print(f"💬 사용자 컨텍스트: {user_context}")
    print("\n🔄 빠른 분석 실행 중...")
    
    try:
        result = analyzer.analyze_webapp_screenshot(image_path, user_context)
        print(f"\n📝 분석 결과:")
        print("="*50)
        print(result)
        print("="*50)
        print("✅ 데모 완료!")
        
    except Exception as e:
        print(f"❌ 데모 실패: {e}")

if __name__ == "__main__":
    print("🌐 웹 애플리케이션 전문 분석기")
    quick_demo()