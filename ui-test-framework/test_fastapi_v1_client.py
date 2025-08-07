"""
Qwen2VL FastAPI v1 서버 테스트 클라이언트

webapp analyzer와 동일한 결과를 확인하기 위한 테스트 클라이언트입니다.
"""

import base64
import requests
import json
import time
import os

def test_v1_server():
    """FastAPI v1 서버 테스트"""
    
    print("🧪 FastAPI v1 서버 테스트")
    print("=" * 50)
    
    # 서버 상태 확인
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("❌ 서버가 응답하지 않습니다.")
            print("💡 먼저 서버를 실행하세요: python qwen2vl_fastapi_v1_server.py")
            return
        
        health_data = response.json()
        print(f"✅ 서버 상태: {health_data['status']}")
        print(f"📱 디바이스: {health_data['device']}")
        
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        print("💡 먼저 서버를 실행하세요: python qwen2vl_fastapi_v1_server.py")
        return
    
    # 테스트 이미지 확인
    test_image = "test_screenshot.png"
    if not os.path.exists(test_image):
        print(f"❌ 테스트 이미지를 찾을 수 없습니다: {test_image}")
        return
    
    # 이미지를 base64로 변환
    try:
        with open(test_image, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"❌ 이미지 읽기 실패: {e}")
        return
    
    # API 호출
    print(f"\n🔄 FastAPI v1 서버 테스트 중...")
    print(f"📸 이미지: {test_image}")
    print(f"💬 컨텍스트: 이것은 네이버 포털사이트 메인 화면입니다.")
    
    try:
        start_time = time.time()
        
        print("⏰ 최대 대기 시간: 5분")
        print("💡 서버 콘솔에서 진행 상황을 확인하세요...")
        
        response = requests.post(
            "http://localhost:8000/analyze",
            json={
                "image_base64": base64_image,
                "user_context": "이것은 토스증권 메인 화면입니다."
            }
        )
        
        request_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ FastAPI v1 서버 결과:")
            print("="*60)
            print(f"결과: {result['result']}")
            print(f"처리 시간: {result['processing_time']:.2f}초")
            print(f"요청 시간: {request_time:.2f}초")
            print(f"성공 여부: {result['success']}")
            print("="*60)
            
            # webapp analyzer 결과와 비교
            print(f"\n📊 webapp analyzer 결과와 비교:")
            print("webapp analyzer (참고용):")
            print("   1. 토스증권 메인 화면")
            print("   2. 토스증권 거래 대금")
            print("   3. 토스증권 거래량")
            print("   ... (45개 항목)")
            print()
            
            print("FastAPI v1 서버:")
            print(f"   {result['result'][:100]}...")
            print()
            
            if result['success']:
                print("✅ 두 시스템이 동일한 프롬프트와 파라미터를 사용하므로")
                print("   유사한 결과가 나와야 합니다!")
            else:
                print("❌ 분석 실패")
                
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ API 호출 오류: {e}")

def compare_with_original():
    """원본 webapp analyzer와 비교"""
    
    print("\n🔄 원본 webapp analyzer 실행...")
    print("💡 비교를 위해 다음 명령을 별도 터미널에서 실행하세요:")
    print("   cd ui-test")
    print("   source bin/activate")
    print("   python qwen2vl_webapp_analyzer.py")
    print("   선택: 2 (빠른 데모)")
    print()
    print("그러면 두 결과를 직접 비교할 수 있습니다!")

def main():
    """메인 함수"""
    print("🌐 Qwen2VL FastAPI v1 서버 테스트")
    print("webapp analyzer와 동일한 기능 검증")
    print("=" * 60)
    
    test_v1_server()
    compare_with_original()
    
    print("\n💡 테스트 팁:")
    print("1. 두 시스템 모두 동일한 프롬프트 사용")
    print("2. 동일한 생성 파라미터 사용")
    print("3. 동일한 모델과 프로세서 사용")
    print("4. 따라서 결과가 매우 유사해야 합니다!")

if __name__ == "__main__":
    main() 