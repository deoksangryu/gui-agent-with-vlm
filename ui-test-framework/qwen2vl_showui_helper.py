"""
Qwen2VL ShowUI 헬퍼

이 스크립트는 웹 애플리케이션 스크린샷을 분석하여 
ShowUI 모델이 사용할 수 있는 UI 요소 정보를 추출합니다.

주요 기능:
1. 클릭 가능한 요소 식별 (버튼, 링크, 아이콘 등)
2. 입력 가능한 요소 식별 (텍스트 필드, 드롭다운 등)
3. 각 요소의 위치 좌표 추정
4. 요소별 기능과 목적 설명
5. ShowUI 명령어 생성 지원
"""

import os
import torch
import time
import json
from PIL import Image
from io import BytesIO
import requests
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

# GPU 최적화 설정
torch.backends.cuda.enable_mem_efficient_sdp(False)
torch.backends.cuda.enable_flash_sdp(False)

class ShowUIHelper:
    """
    ShowUI를 위한 UI 요소 추출 전문 분석기
    """
    
    def __init__(self, model_name="Qwen/Qwen2-VL-2B-Instruct", device="auto"):
        """
        ShowUI 헬퍼 초기화
        
        Args:
            model_name: 사용할 모델 이름
            device: 사용할 디바이스 (auto, cpu, cuda, mps 등)
        """
        print("🎯 ShowUI 헬퍼 초기화 중...")
        
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
            
            print("✅ ShowUI 헬퍼 준비 완료!")
            
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
    
    def extract_ui_elements(self, image_input, user_context="", task_description=""):
        """
        ShowUI를 위한 UI 요소 추출
        
        Args:
            image_input: 스크린샷 이미지
            user_context: 사용자 제공 보충설명
            task_description: 수행하려는 작업 설명
            
        Returns:
            str: UI 요소 정보 (JSON 형태)
        """
        
        system_prompt = """
당신은 웹 자동화 전문가입니다. 
제공된 스크린샷에서 ShowUI 모델이 자동화 작업에 사용할 수 있는 
UI 요소를 간결하고 정확하게 분석해주세요.

각 요소에 대해 한 번씩만 설명하고, 중복되는 내용은 피해주세요.
"""
        
        task_prompt = f"""
이 웹 애플리케이션 스크린샷에서 상호작용 가능한 주요 UI 요소들을 분석해주세요.

【클릭 가능한 요소들】
각 버튼, 링크, 아이콘에 대해:
- 유형: (버튼/링크/아이콘)
- 위치: (화면의 구체적 위치)
- 텍스트: (표시된 텍스트)
- 기능: (예상되는 동작)

【입력 가능한 요소들】
각 입력 필드에 대해:
- 유형: (텍스트박스/드롭다운/체크박스 등)
- 위치: (화면 위치)
- 라벨: (필드 이름)
- 목적: (입력할 정보 유형)

【주요 텍스트】
- 제목/헤더
- 메뉴 항목
- 중요한 안내 메시지

【네비게이션】
- 메뉴바 위치와 항목들
- 페이지 이동 버튼들

각 요소는 한 번씩만 언급하고, 위치는 "상단 좌측", "중앙", "하단 우측" 등으로 간단명확하게 표현해주세요.
ShowUI 자동화에 필요한 핵심 정보만 제공해주세요.
"""
        
        # 사용자 컨텍스트 추가
        if user_context.strip():
            context_section = f"""

【웹 애플리케이션 정보】
{user_context.strip()}
"""
            task_prompt += context_section
        
        # 작업 설명 추가
        if task_description.strip():
            task_section = f"""

【수행할 작업】
{task_description.strip()}
위 작업을 수행하기 위해 필요한 UI 요소들에 특히 주목해서 분석해주세요.
"""
            task_prompt += task_section
        
        full_prompt = system_prompt + task_prompt
        
        return self._generate_response(image_input, full_prompt)
    
    def generate_showui_commands(self, image_input, user_context="", task_sequence=""):
        """
        ShowUI 명령어 시퀀스 생성
        
        Args:
            image_input: 스크린샷 이미지
            user_context: 사용자 제공 보충설명  
            task_sequence: 수행할 작업 시퀀스
            
        Returns:
            str: ShowUI 명령어들
        """
        
        prompt = f"""
당신은 ShowUI 자동화 전문가입니다.
제공된 스크린샷을 분석하여 구체적인 ShowUI 명령어 시퀀스를 생성해주세요.

【ShowUI 명령어 형식】
다음과 같은 형식으로 명령어를 작성해주세요:

1. click(<위치설명>) - 특정 요소 클릭
   예: click("화면 우상단의 로그인 버튼")
   
2. type(<위치설명>, "<입력할텍스트>") - 텍스트 입력
   예: type("사용자명 입력 필드", "testuser")
   
3. scroll(<방향>, <정도>) - 스크롤
   예: scroll("down", "medium")
   
4. wait(<시간>) - 대기
   예: wait(2)

【현재 화면 분석】
현재 화면에서 상호작용 가능한 모든 요소들을 먼저 나열하고,
각 요소의 정확한 위치와 기능을 설명해주세요.

【명령어 시퀀스 생성】
요청된 작업을 수행하기 위한 단계별 ShowUI 명령어를 생성해주세요.
각 명령어 앞에 주석으로 어떤 작업을 하는지 설명을 추가해주세요.
"""
        
        if user_context.strip():
            prompt += f"""

【웹 애플리케이션 정보】
{user_context.strip()}
"""
        
        if task_sequence.strip():
            prompt += f"""

【수행할 작업 시퀀스】
{task_sequence.strip()}

위 작업들을 순서대로 수행하기 위한 ShowUI 명령어를 생성해주세요.
"""
        else:
            prompt += """

【기본 작업】
현재 화면에서 수행 가능한 주요 작업들에 대한 ShowUI 명령어 예시를 제공해주세요.
"""
        
        prompt += "\n한국어로 상세하고 실행 가능한 명령어를 생성해주세요."
        
        return self._generate_response(image_input, prompt)
    
    def identify_form_structure(self, image_input, user_context=""):
        """
        폼 구조 식별 (입력 양식 분석)
        
        Args:
            image_input: 스크린샷 이미지
            user_context: 사용자 보충설명
            
        Returns:
            str: 폼 구조 정보
        """
        
        prompt = f"""
당신은 웹 폼 분석 전문가입니다.
이 스크린샷에서 입력 양식(Form)의 구조를 자세히 분석해주세요.

【폼 필드 분석】
각 입력 필드에 대해:
1. 필드 유형: (텍스트/이메일/비밀번호/숫자/선택 등)
2. 필드 라벨: (필드 이름이나 설명)
3. 위치: (화면에서의 정확한 위치)
4. 필수 여부: (필수 입력 필드인지)
5. 검증 규칙: (예상되는 입력 형식이나 제한사항)
6. 기본값/플레이스홀더: (미리 입력된 값이나 힌트 텍스트)

【액션 버튼 분석】
1. 제출 버튼: (위치와 텍스트)
2. 취소/리셋 버튼: (있다면 위치와 기능)
3. 기타 버튼들: (추가 기능 버튼들)

【폼 입력 순서】
사용자가 자연스럽게 입력할 수 있는 필드 순서를 제안해주세요.

【ShowUI 자동화를 위한 정보】
각 필드를 ShowUI로 자동 입력하기 위한 구체적인 위치 설명과 
예시 입력값을 제공해주세요.
"""
        
        if user_context.strip():
            prompt += f"""

【추가 정보】
{user_context.strip()}
"""
        
        prompt += "\n한국어로 폼 구조를 체계적으로 분석해주세요."
        
        return self._generate_response(image_input, prompt)
    
    def analyze_navigation_structure(self, image_input, user_context=""):
        """
        네비게이션 구조 분석
        
        Args:
            image_input: 스크린샷 이미지  
            user_context: 사용자 보충설명
            
        Returns:
            str: 네비게이션 구조 정보
        """
        
        prompt = f"""
당신은 웹 네비게이션 분석 전문가입니다.
이 스크린샷에서 네비게이션 구조를 분석해주세요.

【메인 네비게이션】
1. 상단 메뉴바: (메뉴 항목들과 위치)
2. 사이드 메뉴: (있다면 메뉴 구조)
3. 하단 네비게이션: (모바일 스타일 하단 메뉴)

【브레드크럼/경로 표시】
현재 페이지의 위치를 나타내는 요소들

【검색 기능】
1. 검색바 위치와 형태
2. 검색 옵션이나 필터들

【페이지 이동 요소들】
1. 페이지네이션: (이전/다음 버튼, 페이지 번호)
2. 무한 스크롤 여부
3. "더보기" 버튼 등

【ShowUI 네비게이션 명령어】
각 네비게이션 요소에 접근하기 위한 구체적인 ShowUI 명령어를 제공해주세요.
예시:
- click("상단 메뉴의 '제품' 링크")
- click("사이드바의 '설정' 메뉴")
- click("페이지 하단의 '다음' 버튼")
"""
        
        if user_context.strip():
            prompt += f"""

【웹사이트 정보】
{user_context.strip()}
"""
        
        prompt += "\n한국어로 네비게이션 구조를 체계적으로 분석해주세요."
        
        return self._generate_response(image_input, prompt)
    
    def extract_content_areas(self, image_input, user_context=""):
        """
        콘텐츠 영역 추출
        
        Args:
            image_input: 스크린샷 이미지
            user_context: 사용자 보충설명
            
        Returns:
            str: 콘텐츠 영역 정보
        """
        
        prompt = f"""
당신은 웹 페이지 레이아웃 분석 전문가입니다.
이 스크린샷에서 주요 콘텐츠 영역들을 식별하고 분석해주세요.

【주요 콘텐츠 영역】
1. 헤더 영역: (로고, 메뉴, 사용자 정보 등)
2. 메인 콘텐츠 영역: (핵심 내용이 표시되는 부분)
3. 사이드바 영역: (보조 정보나 메뉴)
4. 푸터 영역: (하단 정보들)

【각 영역별 상세 분석】
각 영역에서:
1. 위치와 크기: (화면에서의 정확한 위치)
2. 포함된 요소들: (텍스트, 이미지, 버튼 등)
3. 상호작용 요소들: (클릭/입력 가능한 요소들)
4. 중요도: (사용자 작업에서의 우선순위)

【텍스트 콘텐츠】
읽을 수 있는 모든 텍스트를 영역별로 정리:
1. 제목들 (H1, H2, H3 등)
2. 본문 텍스트
3. 버튼 텍스트
4. 링크 텍스트
5. 라벨과 설명 텍스트

【데이터 표시 영역】
1. 표(Table) 구조
2. 리스트 항목들
3. 카드형 레이아웃
4. 차트나 그래프

【ShowUI 데이터 추출】
각 콘텐츠 영역에서 데이터를 추출하거나 
특정 정보를 찾기 위한 ShowUI 접근 방법을 제안해주세요.
"""
        
        if user_context.strip():
            prompt += f"""

【페이지 정보】
{user_context.strip()}
"""
        
        prompt += "\n한국어로 콘텐츠 구조를 체계적으로 분석해주세요."
        
        return self._generate_response(image_input, prompt)
    
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
            print("🔄 UI 요소 분석 중...")
            generated_ids = self.model.generate(
                **inputs, 
                max_new_tokens=1500,  # 토큰 수 더 줄임
                do_sample=False,  # 더 결정적인 생성
                temperature=None,  # do_sample=False일 때 temperature 사용 안함
                repetition_penalty=1.2,  # 반복 방지 강화
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

def interactive_showui_helper():
    """
    대화형 ShowUI 헬퍼
    """
    print("🎯 ShowUI 헬퍼 - UI 요소 추출기")
    print("=" * 50)
    print("이 도구는 ShowUI 자동화를 위한 UI 요소 정보를 추출합니다.")
    print("'quit'를 입력하면 종료됩니다.")
    
    try:
        helper = ShowUIHelper()
    except Exception as e:
        print(f"❌ 헬퍼 초기화 실패: {e}")
        return
    
    while True:
        print("\n" + "-"*50)
        
        # 이미지 입력
        image_path = input("📁 웹앱 스크린샷 경로를 입력하세요: ").strip()
        if image_path.lower() == 'quit':
            break
        
        if not os.path.exists(image_path):
            print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
            continue
        
        # 사용자 컨텍스트 입력
        print("\n💬 이 웹앱에 대한 설명을 입력해주세요:")
        user_context = input("설명: ").strip()
        
        # 분석 유형 선택
        print("\n🔍 분석 유형을 선택하세요:")
        print("1. UI 요소 추출 (모든 상호작용 요소)")
        print("2. ShowUI 명령어 생성")
        print("3. 폼 구조 분석")
        print("4. 네비게이션 구조 분석") 
        print("5. 콘텐츠 영역 추출")
        
        choice = input("선택 (1-5): ").strip()
        
        print(f"\n🤖 '{image_path}' 분석 중...")
        
        try:
            if choice == "1":
                task_desc = input("수행할 작업이 있다면 설명해주세요 (선택사항): ").strip()
                result = helper.extract_ui_elements(image_path, user_context, task_desc)
            elif choice == "2":
                task_seq = input("수행할 작업 시퀀스를 입력해주세요: ").strip()
                result = helper.generate_showui_commands(image_path, user_context, task_seq)
            elif choice == "3":
                result = helper.identify_form_structure(image_path, user_context)
            elif choice == "4":
                result = helper.analyze_navigation_structure(image_path, user_context)
            elif choice == "5":
                result = helper.extract_content_areas(image_path, user_context)
            else:
                result = helper.extract_ui_elements(image_path, user_context)
            
            print(f"\n📝 분석 결과:")
            print("="*60)
            print(result)
            print("="*60)
            
        except Exception as e:
            print(f"❌ 분석 실패: {e}")
    
    print("👋 ShowUI 헬퍼 종료")

def quick_demo():
    """
    빠른 데모 실행
    """
    print("🚀 ShowUI 헬퍼 빠른 데모")
    print("=" * 40)
    
    try:
        helper = ShowUIHelper()
    except Exception as e:
        print(f"❌ 헬퍼 초기화 실패: {e}")
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
    user_context = "토스증권 메인 화면입니다."
    
    print(f"💬 사용자 컨텍스트: {user_context}")
    print("\n🔄 UI 요소 추출 실행 중...")
    
    try:
        result = helper.extract_ui_elements(image_path, user_context)
        print(f"\n📝 분석 결과:")
        print("="*50)
        print(result)
        print("="*50)
        print("✅ 데모 완료!")
        
    except Exception as e:
        print(f"❌ 데모 실패: {e}")

if __name__ == "__main__":
    print("🎯 ShowUI 헬퍼 - UI 요소 추출기")
    print("선택하세요:")
    print("1. 대화형 헬퍼 실행")
    print("2. 빠른 데모 실행")
    
    choice = input("선택 (1-2): ").strip()
    
    if choice == "2":
        quick_demo()
    else:
        interactive_showui_helper() 