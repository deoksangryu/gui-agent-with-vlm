"""
ShowUI 이미지 설명 기능 간단 사용 예제

이 스크립트는 ShowUI 이미지 설명 기능의 간단한 사용법을 보여줍니다.
"""

from showui_describe_test import ShowUIDescriber

def simple_example():
    """
    간단한 이미지 설명 예제
    """
    print("🚀 ShowUI 이미지 설명 간단 예제")
    print("=" * 50)
    
    # ShowUI 설명기 초기화
    describer = ShowUIDescriber()
    
    # 예제 이미지 파일
    image_path = "test_screenshot.png"
    
    try:
        # 1. 기본 이미지 설명
        print("\n📝 기본 이미지 설명:")
        description = describer.describe_image(image_path)
        print(description)
        
        # 2. 사용자 정의 질문
        print("\n❓ 사용자 정의 질문:")
        custom_question = "이 화면에서 가장 중요한 버튼은 무엇인가요?"
        custom_answer = describer.describe_image(image_path, custom_question)
        print(f"질문: {custom_question}")
        print(f"답변: {custom_answer}")
        
        # 3. UI 요소 분석
        print("\n🔍 UI 요소 분석:")
        ui_elements = describer.analyze_ui_elements(image_path)
        print(ui_elements)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def custom_questions_example():
    """
    다양한 사용자 정의 질문 예제
    """
    print("\n🎯 다양한 질문 예제")
    print("=" * 50)
    
    describer = ShowUIDescriber()
    image_path = "test_screenshot.png"
    
    # 다양한 질문들
    questions = [
        "이 앱의 주요 기능은 무엇인가요?",
        "사용자가 다음에 할 수 있는 행동은 무엇인가요?",
        "이 화면의 가장 눈에 띄는 요소는 무엇인가요?",
        "이 앱이 어떤 종류의 앱인지 추측해보세요.",
        "화면에 표시된 모든 텍스트를 나열해주세요.",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. 질문: {question}")
        try:
            answer = describer.describe_image(image_path, question)
            print(f"   답변: {answer}")
        except Exception as e:
            print(f"   ❌ 오류: {e}")
        print("-" * 30)

if __name__ == "__main__":
    # 간단한 예제 실행
    simple_example()
    
    # 사용자 선택에 따라 추가 예제 실행
    choice = input("\n다양한 질문 예제도 실행하시겠습니까? (y/n): ").strip().lower()
    if choice == 'y':
        custom_questions_example()
    
    print("\n✅ 예제 실행 완료!") 