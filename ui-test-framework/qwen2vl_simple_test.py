"""
Qwen2VL 간단 테스트 스크립트

이 스크립트는 Qwen2VL 이미지 설명 기능을 빠르게 테스트하기 위한 간단한 예제입니다.
"""

from qwen2vl_describe_test import Qwen2VLDescriber

def quick_test():
    """
    빠른 테스트 함수
    """
    print("🚀 Qwen2VL 빠른 테스트")
    print("=" * 40)
    
    # 모델 초기화
    try:
        print("모델 로딩 중...")
        describer = Qwen2VLDescriber()
        print("✅ 모델 로딩 완료!")
    except Exception as e:
        print(f"❌ 모델 로딩 실패: {e}")
        return
    
    # 테스트 이미지
    image_path = "test_screenshot.png"
    
    # 간단한 설명 테스트
    print(f"\n📸 이미지 설명 테스트: {image_path}")
    
    try:
        # 기본 설명
        print("\n📝 기본 설명:")
        description = describer.describe_image(image_path)
        print(description)
        
        # 간단한 질문
        print("\n❓ 간단한 질문:")
        question = "이 화면에서 가장 중요한 요소는 무엇인가요?"
        answer = describer.describe_image(image_path, question)
        print(f"질문: {question}")
        print(f"답변: {answer}")
        
        print("\n✅ 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

def test_with_url():
    """
    URL 이미지로 테스트
    """
    print("\n🌐 URL 이미지 테스트")
    print("=" * 40)
    
    # 모델 초기화
    try:
        describer = Qwen2VLDescriber()
    except Exception as e:
        print(f"❌ 모델 로딩 실패: {e}")
        return
    
    # 테스트용 URL 이미지 (구글 로고)
    image_url = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
    
    print(f"📸 URL 이미지 분석: {image_url}")
    
    try:
        description = describer.describe_image(image_url, "이 이미지에 무엇이 보이나요?")
        print(f"📝 설명: {description}")
        print("✅ URL 테스트 완료!")
        
    except Exception as e:
        print(f"❌ URL 테스트 실패: {e}")

if __name__ == "__main__":
    # 기본 테스트
    quick_test()
    
    # URL 테스트 여부 선택
    choice = input("\nURL 이미지 테스트도 실행하시겠습니까? (y/n): ").strip().lower()
    if choice == 'y':
        test_with_url()
    
    print("\n🎉 모든 테스트 완료!") 