import base64
import os
import requests
import time
from pathlib import Path

def encode_image_to_base64(image_path):
    """이미지 파일을 Base64로 인코딩"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    except Exception as e:
        print(f"❌ 이미지 인코딩 실패: {e}")
        return None

def test_showui_fastapi_server():
    """ShowUI FastAPI 서버 테스트"""
    
    print("=" * 60)
    print("🚀 ShowUI FastAPI 서버 테스트 시작")
    print("=" * 60)
    
    # 서버 URL 설정
    BASE_URL = "http://localhost:8001"
    
    # 1. 서버 상태 확인
    print("\n📋 1. 서버 상태 확인 중...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 서버 상태: {health_data['status']}")
            print(f"🤖 모델 로드됨: {health_data['model_loaded']}")
            print(f"🚀 GPU 사용 가능: {health_data['gpu_available']}")
            print(f"⏰ 시간: {health_data['timestamp']}")
            
            if not health_data['model_loaded']:
                print("❌ 모델이 로드되지 않았습니다. 서버가 준비될 때까지 기다려주세요.")
                return
        else:
            print(f"❌ 서버 상태 확인 실패: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ 서버에 연결할 수 없습니다: {e}")
        print("💡 서버가 실행 중인지 확인하세요: python showui_fastapi_server.py")
        return
    
    # 2. 테스트 이미지 확인
    test_image = "test_screenshot.png"
    if not os.path.exists(test_image):
        print(f"❌ 테스트 이미지를 찾을 수 없습니다: {test_image}")
        print("💡 test_screenshot.png 파일을 ui-test 디렉토리에 준비해주세요.")
        return
    
    print(f"\n📸 2. 테스트 이미지: {test_image}")
    
    # 3. 이미지를 Base64로 인코딩
    print("📤 3. 이미지 인코딩 중...")
    base64_image = encode_image_to_base64(test_image)
    if not base64_image:
        return
    
    print(f"✅ 이미지 인코딩 완료 ({len(base64_image)} 문자)")
    
    # 4. 테스트 케이스들
    test_cases = [
        {
            "query": "1일",
            "description": "하루 버튼 찾기"
        },
        {
            "query": "검색",
            "description": "검색 버튼/입력창 찾기"
        },
        {
            "query": "로그인",
            "description": "로그인 버튼 찾기"
        },
        {
            "query": "메뉴",
            "description": "메뉴 버튼 찾기"
        }
    ]
    
    # 5. 각 테스트 케이스 실행
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 {i}. {test_case['description']} 테스트")
        print(f"📝 쿼리: '{test_case['query']}'")
        
        try:
            start_time = time.time()
            
            # API 요청
            response = requests.post(
                f"{BASE_URL}/find_click_position",
                json={
                    "image_base64": base64_image,
                    "query": test_case['query']
                },
                timeout=60  # ShowUI 모델은 시간이 좀 걸릴 수 있음
            )
            
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                if result['success']:
                    print(f"✅ 성공! 처리 시간: {request_time:.2f}초")
                    print(f"📍 상대 좌표: {result['coordinates']}")
                    print(f"📍 절대 좌표: {result['absolute_coordinates']}")
                    print(f"📐 이미지 크기: {result['image_size']}")
                    print(f"🖼️ 결과 이미지: {result['result_image_filename']}")
                    print(f"⚡ 모델 처리 시간: {result['processing_time']:.2f}초")
                else:
                    print(f"❌ 실패: {result.get('error', '알 수 없는 오류')}")
            else:
                print(f"❌ API 요청 실패: {response.status_code}")
                print(f"응답: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ 요청 시간 초과 (60초)")
        except requests.exceptions.RequestException as e:
            print(f"❌ 요청 실패: {e}")
        
        # 테스트 간 간격
        if i < len(test_cases):
            print("⏳ 다음 테스트까지 2초 대기...")
            time.sleep(2)
    
    # 6. 결과 이미지 목록 확인
    print(f"\n📂 6. 저장된 결과 이미지 목록 확인")
    try:
        response = requests.get(f"{BASE_URL}/results")
        if response.status_code == 200:
            results = response.json()['results']
            print(f"✅ 총 {len(results)}개의 결과 이미지가 저장됨")
            
            for result in results[:3]:  # 최신 3개만 표시
                print(f"  - {result['filename']} ({result['size']} bytes, {result['created']})")
                print(f"    다운로드: {BASE_URL}{result['download_url']}")
        else:
            print(f"❌ 결과 목록 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 결과 목록 조회 중 오류: {e}")
    
    # 7. 파일 업로드 테스트
    print(f"\n📤 7. 파일 업로드 방식 테스트")
    try:
        with open(test_image, 'rb') as f:
            files = {'file': (test_image, f, 'image/png')}
            data = {'query': '버튼'}
            
            response = requests.post(
                f"{BASE_URL}/upload_and_find",
                files=files,
                data=data,
                timeout=60
            )
            
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ 파일 업로드 테스트 성공!")
                print(f"📍 좌표: {result['coordinates']}")
            else:
                print(f"❌ 파일 업로드 테스트 실패: {result.get('error')}")
        else:
            print(f"❌ 파일 업로드 요청 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 파일 업로드 테스트 중 오류: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 ShowUI FastAPI 서버 테스트 완료!")
    print("=" * 60)
    print(f"📚 API 문서: {BASE_URL}/docs")
    print(f"🔍 Redoc 문서: {BASE_URL}/redoc")
    print(f"❤️ 서버 상태: {BASE_URL}/health")
    print(f"📂 결과 목록: {BASE_URL}/results")

def test_specific_element():
    """특정 UI 요소 찾기 테스트"""
    
    BASE_URL = "http://localhost:8001"
    test_image = "test_screenshot.png"
    
    if not os.path.exists(test_image):
        print(f"❌ 테스트 이미지가 없습니다: {test_image}")
        return
    
    # 사용자 입력 받기
    query = input("\n🔍 찾고 싶은 UI 요소를 설명하세요 (예: '버튼', '검색창', '로그인'): ").strip()
    
    if not query:
        print("❌ 쿼리가 입력되지 않았습니다.")
        return
    
    print(f"\n📤 '{query}' 요소를 찾는 중...")
    
    # 이미지 인코딩
    base64_image = encode_image_to_base64(test_image)
    if not base64_image:
        return
    
    try:
        response = requests.post(
            f"{BASE_URL}/find_click_position",
            json={
                "image_base64": base64_image,
                "query": query
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result['success']:
                print(f"\n✅ '{query}' 요소를 찾았습니다!")
                print(f"📍 상대 좌표: {result['coordinates']}")
                print(f"📍 절대 좌표: {result['absolute_coordinates']}")
                print(f"🖼️ 결과 이미지: {result['result_image_filename']}")
                print(f"⚡ 처리 시간: {result['processing_time']:.2f}초")
                print(f"\n📂 결과 이미지 다운로드: {BASE_URL}/download_result/{result['result_image_filename']}")
            else:
                print(f"❌ '{query}' 요소를 찾을 수 없습니다: {result.get('error')}")
        else:
            print(f"❌ API 요청 실패: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 요청 중 오류 발생: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "specific":
        test_specific_element()
    else:
        test_showui_fastapi_server() 