"""
FastAPI 서버 빠른 테스트 스크립트

webapp analyzer와 FastAPI 서버 결과를 비교하기 위한 스크립트입니다.
"""

import base64
import requests
import json
import os

def test_fastapi_server():
    """FastAPI 서버 테스트"""
    
    # 서버 상태 확인
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 응답하지 않습니다.")
            print("💡 먼저 서버를 실행하세요: python qwen2vl_fastapi_server.py")
            return
        
        health_data = response.json()
        print(f"✅ 서버 상태: {health_data['status']}")
        print(f"📱 디바이스: {health_data['device']}")
        
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        print("💡 먼저 서버를 실행하세요: python qwen2vl_fastapi_server.py")
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
    print(f"\n🔄 FastAPI 서버 테스트 중...")
    print(f"📸 이미지: {test_image}")
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze",
            json={
                "image_base64": base64_image,
                "context": "토스증권 메인 화면"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ FastAPI 서버 결과:")
            print("="*60)
            print(f"클릭 요소들: {result['clickable_elements']}")
            print(f"처리 시간: {result['processing_time']:.2f}초")
            print(f"성공 여부: {result['success']}")
            print("="*60)
            
            # 결과 분석
            elements = result['clickable_elements']
            if ',' in elements:
                element_list = [e.strip() for e in elements.split(',')]
                print(f"\n📊 분석:")
                print(f"   - 총 요소 수: {len(element_list)}")
                print(f"   - 형식: 쉼표 구분 문자열 ✅")
                print(f"   - 첫 3개 요소: {', '.join(element_list[:3])}")
            else:
                print(f"\n⚠️ 주의: 쉼표로 구분되지 않은 응답")
                
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ API 호출 오류: {e}")

def main():
    """메인 함수"""
    print("🧪 FastAPI 서버 빠른 테스트")
    print("=" * 50)
    
    print("📋 비교용 webapp analyzer 결과:")
    print("   1. 토스증권 메인 화면")
    print("   2. 토스증권 거래 대금")
    print("   3. 토스증권 거래량")
    print("   ... (45개 항목, 숫자 리스트 형태)")
    print()
    
    print("🎯 기대하는 FastAPI 결과:")
    print("   삼성전자 링크, NAVER 링크, 검색 버튼, 메뉴 아이콘, 차트 탭, ...")
    print("   (쉼표로 구분된 클릭 가능한 요소들)")
    print()
    
    test_fastapi_server()

if __name__ == "__main__":
    main() 