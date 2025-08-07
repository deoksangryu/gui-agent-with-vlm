"""
FastAPI 서버 타임아웃 진단 스크립트

타임아웃 원인을 찾고 해결하기 위한 진단 도구입니다.
"""

import base64
import requests
import json
import time
import os
import threading

def monitor_request(url, data, timeout=300):
    """요청을 모니터링하면서 진행 상황 표시"""
    
    def make_request():
        """실제 요청을 수행하는 함수"""
        nonlocal response, error, completed
        try:
            response = requests.post(url, json=data, timeout=timeout)
            completed = True
        except Exception as e:
            error = e
            completed = True
    
    response = None
    error = None
    completed = False
    
    # 백그라운드에서 요청 실행
    thread = threading.Thread(target=make_request)
    thread.start()
    
    # 진행 상황 모니터링
    start_time = time.time()
    last_update = 0
    
    while not completed:
        elapsed = time.time() - start_time
        
        # 10초마다 진행 상황 출력
        if elapsed - last_update >= 10:
            print(f"⏱️ 경과 시간: {elapsed:.0f}초 / {timeout}초")
            last_update = elapsed
        
        time.sleep(1)
        
        # 타임아웃 체크
        if elapsed > timeout:
            print(f"❌ {timeout}초 타임아웃!")
            break
    
    thread.join(timeout=1)
    
    if error:
        raise error
    
    return response

def test_small_image():
    """작은 이미지로 빠른 테스트"""
    print("🧪 작은 이미지 테스트")
    
    # 1x1 픽셀 흰색 이미지 생성
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    base64_image = base64.b64encode(img_bytes.read()).decode('utf-8')
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/analyze",
            json={
                "image_base64": base64_image,
                "user_context": "테스트 이미지"
            },
            timeout=60
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 작은 이미지 테스트 성공: {elapsed:.2f}초")
            print(f"   결과: {result['result'][:50]}...")
            return True
        else:
            print(f"❌ 응답 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 작은 이미지 테스트 실패: {e}")
        return False

def diagnose_server():
    """서버 진단"""
    print("🔍 서버 진단 시작")
    print("=" * 50)
    
    # 1. 서버 상태 확인
    print("1️⃣ 서버 상태 확인...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ 서버 상태: {health['status']}")
            print(f"📱 디바이스: {health['device']}")
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False
    
    # 2. 작은 이미지 테스트
    print("\n2️⃣ 작은 이미지 테스트...")
    if not test_small_image():
        print("❌ 기본 기능에 문제가 있습니다.")
        return False
    
    # 3. 실제 이미지 테스트
    print("\n3️⃣ 실제 이미지 테스트...")
    test_image = "test_screenshot2.png"
    
    if not os.path.exists(test_image):
        print(f"❌ 테스트 이미지를 찾을 수 없습니다: {test_image}")
        return False
    
    try:
        with open(test_image, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
        
        print(f"📸 이미지 크기: {len(base64_image)} 문자")
        print("🔄 분석 시작 (최대 5분 대기)...")
        
        response = monitor_request(
            "http://localhost:8000/analyze",
            {
                "image_base64": base64_image,
                "user_context": "이것은 네이버 포털사이트의 메인 화면입니다."
            },
            timeout=300
        )
        
        if response and response.status_code == 200:
            result = response.json()
            print(f"✅ 실제 이미지 테스트 성공!")
            print(f"   처리 시간: {result['processing_time']:.2f}초")
            print(f"   결과: {result['result'][:100]}...")
            return True
        else:
            print(f"❌ 실제 이미지 테스트 실패")
            return False
            
    except Exception as e:
        print(f"❌ 실제 이미지 테스트 오류: {e}")
        return False

def print_recommendations():
    """추천 해결책 출력"""
    print("\n💡 타임아웃 해결 방법:")
    print("=" * 50)
    print("1. 생성 파라미터 조정:")
    print("   - max_new_tokens를 1000 이하로 감소")
    print("   - repetition_penalty 추가")
    print("   - EOS 토큰 설정")
    print()
    print("2. 서버 최적화:")
    print("   - GPU 메모리 확인")
    print("   - 다른 프로세스 종료")
    print("   - CPU 모드로 테스트")
    print()
    print("3. 이미지 최적화:")
    print("   - 이미지 크기 줄이기")
    print("   - 압축률 높이기")
    print("   - 작은 이미지로 먼저 테스트")

def main():
    """메인 진단 함수"""
    print("🔧 FastAPI 서버 타임아웃 진단")
    print("=" * 60)
    
    success = diagnose_server()
    
    if not success:
        print_recommendations()
        print("\n❌ 진단 완료 - 문제가 발견되었습니다.")
    else:
        print("\n✅ 진단 완료 - 모든 테스트 통과!")

if __name__ == "__main__":
    main() 