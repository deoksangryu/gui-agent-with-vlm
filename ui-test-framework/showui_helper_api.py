"""
ShowUI 헬퍼 API

ShowUI 자동화를 위한 UI 요소 추출 API입니다.
다른 프로젝트에서 쉽게 import하여 사용할 수 있습니다.
"""

from qwen2vl_showui_helper import ShowUIHelper

class ShowUIHelperAPI:
    """
    ShowUI 헬퍼 API 클래스
    """
    
    def __init__(self, device="auto"):
        """
        API 초기화
        
        Args:
            device: 사용할 디바이스 (auto, cpu, cuda, mps)
        """
        self.helper = ShowUIHelper(device=device)
    
    def extract_ui_elements(self, image_path, context="", task=""):
        """
        UI 요소 추출
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 웹앱에 대한 설명
            task: 수행할 작업 설명 (선택사항)
            
        Returns:
            dict: 분석 결과
        """
        try:
            result = self.helper.extract_ui_elements(image_path, context, task)
            return {
                "success": True,
                "type": "ui_elements",
                "result": result,
                "image_path": image_path,
                "context": context,
                "task": task
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "ui_elements",
                "image_path": image_path
            }
    
    def generate_commands(self, image_path, context="", task_sequence=""):
        """
        ShowUI 명령어 생성
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 웹앱에 대한 설명
            task_sequence: 수행할 작업 시퀀스
            
        Returns:
            dict: 명령어 생성 결과
        """
        try:
            result = self.helper.generate_showui_commands(image_path, context, task_sequence)
            return {
                "success": True,
                "type": "commands",
                "result": result,
                "image_path": image_path,
                "context": context,
                "task_sequence": task_sequence
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "commands",
                "image_path": image_path
            }
    
    def analyze_form(self, image_path, context=""):
        """
        폼 구조 분석
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 웹앱에 대한 설명
            
        Returns:
            dict: 폼 분석 결과
        """
        try:
            result = self.helper.identify_form_structure(image_path, context)
            return {
                "success": True,
                "type": "form_analysis",
                "result": result,
                "image_path": image_path,
                "context": context
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "form_analysis",
                "image_path": image_path
            }
    
    def analyze_navigation(self, image_path, context=""):
        """
        네비게이션 구조 분석
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 웹앱에 대한 설명
            
        Returns:
            dict: 네비게이션 분석 결과
        """
        try:
            result = self.helper.analyze_navigation_structure(image_path, context)
            return {
                "success": True,
                "type": "navigation_analysis",
                "result": result,
                "image_path": image_path,
                "context": context
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "navigation_analysis",
                "image_path": image_path
            }
    
    def extract_content(self, image_path, context=""):
        """
        콘텐츠 영역 추출
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 웹앱에 대한 설명
            
        Returns:
            dict: 콘텐츠 추출 결과
        """
        try:
            result = self.helper.extract_content_areas(image_path, context)
            return {
                "success": True,
                "type": "content_extraction",
                "result": result,
                "image_path": image_path,
                "context": context
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "content_extraction",
                "image_path": image_path
            }
    
    def full_analysis(self, image_path, context="", target_task=""):
        """
        전체 분석 (모든 분석 유형을 한 번에)
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 웹앱에 대한 설명
            target_task: 목표 작업 (선택사항)
            
        Returns:
            dict: 전체 분석 결과
        """
        results = {}
        
        # UI 요소 추출
        print("🔄 UI 요소 추출 중...")
        ui_result = self.extract_ui_elements(image_path, context, target_task)
        results["ui_elements"] = ui_result
        
        # 폼 분석
        print("🔄 폼 구조 분석 중...")
        form_result = self.analyze_form(image_path, context)
        results["form_analysis"] = form_result
        
        # 네비게이션 분석
        print("🔄 네비게이션 분석 중...")
        nav_result = self.analyze_navigation(image_path, context)
        results["navigation_analysis"] = nav_result
        
        # 콘텐츠 추출
        print("🔄 콘텐츠 추출 중...")
        content_result = self.extract_content(image_path, context)
        results["content_extraction"] = content_result
        
        # ShowUI 명령어 생성 (목표 작업이 있는 경우)
        if target_task.strip():
            print("🔄 ShowUI 명령어 생성 중...")
            cmd_result = self.generate_commands(image_path, context, target_task)
            results["showui_commands"] = cmd_result
        
        return {
            "success": True,
            "type": "full_analysis",
            "results": results,
            "image_path": image_path,
            "context": context,
            "target_task": target_task
        }

# 편의 함수들
def extract_ui_elements_for_showui(image_path, context="", task="", device="auto"):
    """
    ShowUI를 위한 UI 요소 추출 편의 함수
    
    Args:
        image_path: 스크린샷 이미지 경로
        context: 웹앱 설명
        task: 수행할 작업
        device: 사용할 디바이스
        
    Returns:
        dict: UI 요소 추출 결과
    """
    api = ShowUIHelperAPI(device=device)
    return api.extract_ui_elements(image_path, context, task)

def generate_showui_commands(image_path, context="", task_sequence="", device="auto"):
    """
    ShowUI 명령어 생성 편의 함수
    
    Args:
        image_path: 스크린샷 이미지 경로
        context: 웹앱 설명
        task_sequence: 작업 시퀀스
        device: 사용할 디바이스
        
    Returns:
        dict: 명령어 생성 결과
    """
    api = ShowUIHelperAPI(device=device)
    return api.generate_commands(image_path, context, task_sequence)

def analyze_webpage_for_automation(image_path, context="", target_task="", device="auto"):
    """
    웹페이지 자동화를 위한 전체 분석 편의 함수
    
    Args:
        image_path: 스크린샷 이미지 경로
        context: 웹앱 설명
        target_task: 목표 작업
        device: 사용할 디바이스
        
    Returns:
        dict: 전체 분석 결과
    """
    api = ShowUIHelperAPI(device=device)
    return api.full_analysis(image_path, context, target_task)

# 사용 예제
if __name__ == "__main__":
    print("🎯 ShowUI 헬퍼 API 테스트")
    print("=" * 40)
    
    # API 인스턴스 생성
    api = ShowUIHelperAPI()
    
    # 테스트 이미지
    test_image = "test_screenshot.png"
    test_context = "토스증권 메인 화면입니다."
    test_task = "주식 검색하고 매수 주문 넣기"
    
    print(f"📸 테스트 이미지: {test_image}")
    print(f"💬 테스트 컨텍스트: {test_context}")
    print(f"🎯 테스트 작업: {test_task}")
    
    # UI 요소 추출 테스트
    print("\n🚀 UI 요소 추출 테스트...")
    try:
        result = api.extract_ui_elements(test_image, test_context, test_task)
        if result["success"]:
            print("✅ UI 요소 추출 성공!")
            print(f"📝 결과 미리보기: {result['result'][:200]}...")
        else:
            print(f"❌ UI 요소 추출 실패: {result['error']}")
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
    
    # 편의 함수 테스트
    print("\n🔧 편의 함수 테스트...")
    try:
        result = extract_ui_elements_for_showui(
            test_image, 
            test_context, 
            test_task
        )
        if result["success"]:
            print("✅ 편의 함수 성공!")
        else:
            print(f"❌ 편의 함수 실패: {result['error']}")
    except Exception as e:
        print(f"❌ 편의 함수 오류: {e}")
    
    print("\n🎉 API 테스트 완료!") 