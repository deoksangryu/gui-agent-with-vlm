"""
ShowUI 이미지 설명 테스트 스크립트

이 스크립트는 ShowUI 모델을 사용하여 이미지를 분석하고 설명하는 기능을 제공합니다.
기존의 클릭 좌표 감지 기능과 함께 이미지 전체에 대한 자세한 설명도 생성할 수 있습니다.

주요 기능:
1. 이미지 전체 설명 생성
2. UI 요소 식별 및 설명
3. 텍스트 인식 및 요약
4. 화면 레이아웃 분석
"""

import os
import torch
from PIL import Image
from io import BytesIO
import requests
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

class ShowUIDescriber:
    """
    ShowUI를 사용한 이미지 설명 클래스
    """
    
    def __init__(self, model_name="showlab/ShowUI-2B", device="cpu"):
        """
        ShowUI 모델 초기화
        
        Args:
            model_name: 사용할 모델 이름
            device: 사용할 디바이스 (cpu, cuda, mps 등)
        """
        print(f"ShowUI 모델 로딩 중: {model_name}")
        
        # 모델 로드
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map=device
        )
        
        # 이미지 처리 설정
        self.min_pixels = 256 * 28 * 28
        self.max_pixels = 1344 * 28 * 28
        self.size = {"shortest_edge": self.min_pixels, "longest_edge": self.max_pixels}
        
        # 프로세서 로드
        self.processor = AutoProcessor.from_pretrained(
            model_name, 
            min_pixels=self.min_pixels, 
            max_pixels=self.max_pixels, 
            size=self.size
        )
        
        self.device = device
        print(f"ShowUI 모델 로딩 완료 (디바이스: {device})")
    
    def load_image(self, image_input):
        """
        이미지 로드 (파일 경로, URL, PIL Image 지원)
        
        Args:
            image_input: 이미지 경로, URL, 또는 PIL Image 객체
            
        Returns:
            PIL.Image: 로드된 이미지
        """
        if isinstance(image_input, str):
            if image_input.startswith('http'):
                # URL에서 이미지 다운로드
                response = requests.get(image_input)
                image = Image.open(BytesIO(response.content))
            else:
                # 로컬 파일에서 이미지 로드
                image = Image.open(image_input)
        else:
            # 이미 PIL Image인 경우
            image = image_input
        
        return image
    
    def describe_image(self, image_input, custom_prompt=None):
        """
        이미지 전체에 대한 자세한 설명 생성
        
        Args:
            image_input: 이미지 경로, URL, 또는 PIL Image
            custom_prompt: 사용자 정의 프롬프트 (선택사항)
            
        Returns:
            str: 이미지 설명 텍스트
        """
        # 기본 설명 프롬프트
        if custom_prompt is None:
            prompt = """이 이미지를 자세히 설명해주세요. 다음 사항들을 포함해주세요:
1. 전반적인 화면 구성과 레이아웃
2. 주요 UI 요소들 (버튼, 텍스트, 입력창 등)
3. 텍스트 내용 (가능한 경우)
4. 색상과 디자인 특징
5. 사용자가 할 수 있는 주요 액션들"""
        else:
            prompt = custom_prompt
        
        return self._generate_response(image_input, prompt)
    
    def analyze_ui_elements(self, image_input):
        """
        UI 요소들을 분석하고 목록화
        
        Args:
            image_input: 이미지 경로, URL, 또는 PIL Image
            
        Returns:
            str: UI 요소 분석 결과
        """
        prompt = """이 화면의 모든 UI 요소들을 분석하고 다음 형식으로 나열해주세요:

[UI 요소 분석]
1. 버튼: (버튼 이름과 위치)
2. 텍스트 입력창: (입력창 이름과 위치)
3. 텍스트/라벨: (표시된 텍스트 내용)
4. 메뉴/네비게이션: (메뉴 항목들)
5. 이미지/아이콘: (아이콘 설명)
6. 기타 요소: (기타 중요한 UI 요소들)

각 요소의 대략적인 위치(상단/중앙/하단, 좌측/중앙/우측)도 함께 설명해주세요."""
        
        return self._generate_response(image_input, prompt)
    
    def extract_text_content(self, image_input):
        """
        이미지에서 텍스트 내용을 추출하고 정리
        
        Args:
            image_input: 이미지 경로, URL, 또는 PIL Image
            
        Returns:
            str: 추출된 텍스트 내용
        """
        prompt = """이 이미지에 표시된 모든 텍스트를 추출하고 정리해주세요:

[텍스트 추출 결과]
1. 제목/헤더: 
2. 본문 텍스트:
3. 버튼 텍스트:
4. 메뉴 항목:
5. 입력 힌트/플레이스홀더:
6. 기타 텍스트:

텍스트의 위치와 중요도도 함께 설명해주세요."""
        
        return self._generate_response(image_input, prompt)
    
    def suggest_actions(self, image_input):
        """
        화면에서 사용자가 수행할 수 있는 액션들을 제안
        
        Args:
            image_input: 이미지 경로, URL, 또는 PIL Image
            
        Returns:
            str: 가능한 액션들 목록
        """
        prompt = """이 화면을 보고 사용자가 수행할 수 있는 주요 액션들을 제안해주세요:

[가능한 액션들]
1. 클릭 가능한 요소들:
2. 입력 가능한 필드들:
3. 스크롤/네비게이션:
4. 메뉴/설정 접근:
5. 주요 기능 사용법:

각 액션에 대해 어떤 결과가 예상되는지도 설명해주세요."""
        
        return self._generate_response(image_input, prompt)
    
    def _generate_response(self, image_input, prompt):
        """
        ShowUI 모델을 사용하여 응답 생성 (내부 메서드)
        
        Args:
            image_input: 이미지 입력
            prompt: 질문/프롬프트
            
        Returns:
            str: 모델의 응답
        """
        try:
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
                            "max_pixels": self.max_pixels
                        }
                    ],
                }
            ]
            
            # 템플릿 적용
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            # 이미지 처리
            image_inputs, video_inputs = process_vision_info(messages)
            
            # 입력 토큰화
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to(self.device)
            
            # 응답 생성
            generated_ids = self.model.generate(**inputs, max_new_tokens=512)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            # 텍스트 디코딩
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )[0]
            
            return output_text.strip()
            
        except Exception as e:
            return f"이미지 처리 중 오류 발생: {str(e)}"

def main():
    """
    메인 실행 함수 - 다양한 이미지 설명 기능을 테스트
    """
    print("🤖 ShowUI 이미지 설명 테스트 시작")
    print("=" * 60)
    
    # ShowUI 설명기 초기화
    describer = ShowUIDescriber()
    
    # 테스트할 이미지 파일 (예제)
    test_images = [
        "test_screenshot.png",  # 기본 테스트 이미지
        # 추가 테스트 이미지들을 여기에 추가할 수 있습니다
    ]
    
    for image_path in test_images:
        if not os.path.exists(image_path):
            print(f"⚠️  이미지 파일을 찾을 수 없습니다: {image_path}")
            continue
            
        print(f"\n📸 이미지 분석 중: {image_path}")
        print("-" * 40)
        
        # 1. 전체 이미지 설명
        print("\n1️⃣ 전체 이미지 설명:")
        description = describer.describe_image(image_path)
        print(description)
        
        # 2. UI 요소 분석
        print("\n2️⃣ UI 요소 분석:")
        ui_analysis = describer.analyze_ui_elements(image_path)
        print(ui_analysis)
        
        # 3. 텍스트 추출
        print("\n3️⃣ 텍스트 추출:")
        text_content = describer.extract_text_content(image_path)
        print(text_content)
        
        # 4. 액션 제안
        print("\n4️⃣ 가능한 액션들:")
        actions = describer.suggest_actions(image_path)
        print(actions)
        
        print("\n" + "="*60)
    
    print("✅ 이미지 설명 테스트 완료!")

def interactive_mode():
    """
    대화형 모드 - 사용자가 직접 이미지와 질문을 입력
    """
    print("🔄 대화형 모드 시작")
    print("이미지 경로와 질문을 입력하세요. 'quit'를 입력하면 종료됩니다.")
    
    describer = ShowUIDescriber()
    
    while True:
        print("\n" + "-"*40)
        image_path = input("이미지 경로를 입력하세요: ").strip()
        
        if image_path.lower() == 'quit':
            break
            
        if not os.path.exists(image_path):
            print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
            continue
        
        question = input("질문을 입력하세요 (엔터만 누르면 기본 설명): ").strip()
        
        print("\n🤖 분석 중...")
        if question:
            result = describer.describe_image(image_path, question)
        else:
            result = describer.describe_image(image_path)
        
        print(f"\n📝 결과:\n{result}")
    
    print("👋 대화형 모드 종료")

if __name__ == "__main__":
    # 기본 테스트 실행
    main()
    
    # 대화형 모드 실행 여부 선택
    choice = input("\n대화형 모드를 실행하시겠습니까? (y/n): ").strip().lower()
    if choice == 'y':
        interactive_mode() 