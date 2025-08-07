"""
웹 애플리케이션 분석 API

이 모듈은 웹앱 스크린샷 분석을 위한 간단한 API 인터페이스를 제공합니다.
다른 프로젝트에서 쉽게 import하여 사용할 수 있습니다.
"""

from qwen2vl_webapp_analyzer import WebAppAnalyzer

class WebAppAnalysisAPI:
    """
    웹 애플리케이션 분석 API 클래스
    """
    
    def __init__(self, device="auto"):
        """
        API 초기화
        
        Args:
            device: 사용할 디바이스 (auto, cpu, cuda, mps)
        """
        self.analyzer = WebAppAnalyzer(device=device)
    
    def quick_analysis(self, image_path, context=""):
        """
        빠른 분석 - 핵심 정보만 간단히
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 사용자 보충설명
            
        Returns:
            dict: 분석 결과 딕셔너리
        """
        try:
            result = self.analyzer.analyze_webapp_screenshot(
                image_path, context, "quick"
            )
            return {
                "success": True,
                "analysis_type": "quick",
                "result": result,
                "image_path": image_path,
                "user_context": context
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis_type": "quick",
                "image_path": image_path
            }
    
    def comprehensive_analysis(self, image_path, context=""):
        """
        종합 분석 - 전체적인 웹앱 분석
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 사용자 보충설명
            
        Returns:
            dict: 분석 결과 딕셔너리
        """
        try:
            result = self.analyzer.analyze_webapp_screenshot(
                image_path, context, "comprehensive"
            )
            return {
                "success": True,
                "analysis_type": "comprehensive",
                "result": result,
                "image_path": image_path,
                "user_context": context
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis_type": "comprehensive",
                "image_path": image_path
            }
    
    def detailed_analysis(self, image_path, context=""):
        """
        상세 분석 - 매우 자세한 UI/UX 분석
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 사용자 보충설명
            
        Returns:
            dict: 분석 결과 딕셔너리
        """
        try:
            result = self.analyzer.analyze_webapp_screenshot(
                image_path, context, "detailed"
            )
            return {
                "success": True,
                "analysis_type": "detailed",
                "result": result,
                "image_path": image_path,
                "user_context": context
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis_type": "detailed",
                "image_path": image_path
            }
    
    def workflow_analysis(self, image_path, context="", workflow_step=""):
        """
        워크플로우 분석 - 사용자 경험 관점
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 사용자 보충설명
            workflow_step: 현재 워크플로우 단계
            
        Returns:
            dict: 분석 결과 딕셔너리
        """
        try:
            result = self.analyzer.analyze_user_workflow(
                image_path, context, workflow_step
            )
            return {
                "success": True,
                "analysis_type": "workflow",
                "result": result,
                "image_path": image_path,
                "user_context": context,
                "workflow_step": workflow_step
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis_type": "workflow",
                "image_path": image_path
            }
    
    def accessibility_evaluation(self, image_path, context=""):
        """
        접근성 평가 - WCAG 기준 평가
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 사용자 보충설명
            
        Returns:
            dict: 분석 결과 딕셔너리
        """
        try:
            result = self.analyzer.evaluate_accessibility(image_path, context)
            return {
                "success": True,
                "analysis_type": "accessibility",
                "result": result,
                "image_path": image_path,
                "user_context": context
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis_type": "accessibility",
                "image_path": image_path
            }
    
    def design_system_analysis(self, image_path, context=""):
        """
        디자인 시스템 분석 - 색상, 타이포그래피, 레이아웃 등
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 사용자 보충설명
            
        Returns:
            dict: 분석 결과 딕셔너리
        """
        try:
            result = self.analyzer.analyze_design_system(image_path, context)
            return {
                "success": True,
                "analysis_type": "design_system",
                "result": result,
                "image_path": image_path,
                "user_context": context
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis_type": "design_system",
                "image_path": image_path
            }
    
    def contextual_comparison(self, image_path, context, comparison_target=""):
        """
        맥락 기반 비교 분석
        
        Args:
            image_path: 스크린샷 이미지 경로
            context: 사용자 보충설명
            comparison_target: 비교 대상 설명
            
        Returns:
            dict: 분석 결과 딕셔너리
        """
        try:
            result = self.analyzer.compare_with_context(
                image_path, context, comparison_target
            )
            return {
                "success": True,
                "analysis_type": "contextual_comparison",
                "result": result,
                "image_path": image_path,
                "user_context": context,
                "comparison_target": comparison_target
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis_type": "contextual_comparison",
                "image_path": image_path
            }
    
    def batch_analysis(self, image_paths, context="", analysis_type="quick"):
        """
        여러 이미지 일괄 분석
        
        Args:
            image_paths: 이미지 경로 리스트
            context: 공통 사용자 보충설명
            analysis_type: 분석 유형 (quick, comprehensive, detailed)
            
        Returns:
            list: 각 이미지별 분석 결과 리스트
        """
        results = []
        
        for i, image_path in enumerate(image_paths):
            print(f"🔄 배치 분석 진행 중: {i+1}/{len(image_paths)} - {image_path}")
            
            if analysis_type == "quick":
                result = self.quick_analysis(image_path, context)
            elif analysis_type == "comprehensive":
                result = self.comprehensive_analysis(image_path, context)
            elif analysis_type == "detailed":
                result = self.detailed_analysis(image_path, context)
            else:
                result = self.quick_analysis(image_path, context)
            
            results.append(result)
        
        return results

# 편의 함수들
def analyze_webapp_screenshot(image_path, context="", analysis_type="comprehensive", device="auto"):
    """
    웹앱 스크린샷 분석 편의 함수
    
    Args:
        image_path: 스크린샷 이미지 경로
        context: 사용자 보충설명
        analysis_type: 분석 유형 (quick, comprehensive, detailed)
        device: 사용할 디바이스
        
    Returns:
        dict: 분석 결과
    """
    api = WebAppAnalysisAPI(device=device)
    
    if analysis_type == "quick":
        return api.quick_analysis(image_path, context)
    elif analysis_type == "comprehensive":
        return api.comprehensive_analysis(image_path, context)
    elif analysis_type == "detailed":
        return api.detailed_analysis(image_path, context)
    else:
        return api.quick_analysis(image_path, context)

def evaluate_webapp_accessibility(image_path, context="", device="auto"):
    """
    웹앱 접근성 평가 편의 함수
    
    Args:
        image_path: 스크린샷 이미지 경로
        context: 사용자 보충설명
        device: 사용할 디바이스
        
    Returns:
        dict: 접근성 평가 결과
    """
    api = WebAppAnalysisAPI(device=device)
    return api.accessibility_evaluation(image_path, context)

def analyze_user_workflow(image_path, context="", workflow_step="", device="auto"):
    """
    사용자 워크플로우 분석 편의 함수
    
    Args:
        image_path: 스크린샷 이미지 경로
        context: 사용자 보충설명
        workflow_step: 현재 워크플로우 단계
        device: 사용할 디바이스
        
    Returns:
        dict: 워크플로우 분석 결과
    """
    api = WebAppAnalysisAPI(device=device)
    return api.workflow_analysis(image_path, context, workflow_step)

# 사용 예제
if __name__ == "__main__":
    print("🔧 웹앱 분석 API 테스트")
    print("=" * 40)
    
    # API 인스턴스 생성
    api = WebAppAnalysisAPI()
    
    # 테스트 이미지
    test_image = "test_screenshot.png"
    test_context = "이것은 AI 챗봇 웹 애플리케이션입니다. 사용자가 텍스트로 AI와 대화할 수 있습니다."
    
    print(f"📸 테스트 이미지: {test_image}")
    print(f"💬 테스트 컨텍스트: {test_context}")
    
    # 빠른 분석 테스트
    print("\n🚀 빠른 분석 테스트...")
    try:
        result = api.quick_analysis(test_image, test_context)
        if result["success"]:
            print("✅ 빠른 분석 성공!")
            print(f"📝 결과 미리보기: {result['result'][:200]}...")
        else:
            print(f"❌ 빠른 분석 실패: {result['error']}")
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
    
    # 편의 함수 테스트
    print("\n🔧 편의 함수 테스트...")
    try:
        result = analyze_webapp_screenshot(
            test_image, 
            test_context, 
            "quick"
        )
        if result["success"]:
            print("✅ 편의 함수 성공!")
        else:
            print(f"❌ 편의 함수 실패: {result['error']}")
    except Exception as e:
        print(f"❌ 편의 함수 오류: {e}")
    
    print("\n🎉 API 테스트 완료!") 