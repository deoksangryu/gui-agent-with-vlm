"""
Qwen2VL FastAPI 서버 테스트 클라이언트

FastAPI 서버를 테스트하기 위한 클라이언트 예제입니다.
"""

import base64
import requests
import json
import time
from PIL import Image
import io

class FastAPIClient:
    """FastAPI 서버 테스트 클라이언트"""
    
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        
    def image_to_base64(self, image_path):
        """이미지 파일을 base64로 인코딩"""
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except Exception as e:
            print(f"❌ 이미지 인코딩 실패: {e}")
            return None
    
    def check_server_health(self):
        """서버 상태 확인"""
        try:
            response = requests.get(f"{self.server_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 서버 상태: {data['status']}")
                print(f"📱 모델 로딩: {data['model_loaded']}")
                print(f"🔧 디바이스: {data['device']}")
                return True
            else:
                print(f"❌ 서버 응답 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
            return False
    
    def analyze_image(self, image_path, context=""):
        """이미지 분석 요청"""
        # 이미지를 base64로 인코딩
        base64_image = self.image_to_base64(image_path)
        if not base64_image:
            return None
        
        # 요청 데이터 구성
        request_data = {
            "image_base64": base64_image,
            "context": context
        }
        
        try:
            print(f"🔄 이미지 분석 요청 중: {image_path}")
            start_time = time.time()
            
            # API 요청
            response = requests.post(
                f"{self.server_url}/analyze",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 분석 완료!")
                print(f"⏱️ 요청 시간: {request_time:.2f}초")
                print(f"🔧 처리 시간: {result['processing_time']:.2f}초")
                print(f"📝 클릭 요소들: {result['clickable_elements']}")
                return result
            else:
                print(f"❌ 분석 실패: {response.status_code}")
                print(f"📄 응답: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 요청 실패: {e}")
            return None
    
    def test_with_sample_images(self):
        """샘플 이미지들로 테스트"""
        test_images = [
            "test_screenshot.png",
            "screenshot.png", 
            "toss_screenshot.png",
            "examples/app_store.png"
        ]
        
        for image_path in test_images:
            try:
                # 파일 존재 확인
                with open(image_path, 'rb'):
                    pass
                    
                print(f"\n{'='*50}")
                print(f"📸 테스트 이미지: {image_path}")
                
                # 컨텍스트 설정
                if "toss" in image_path.lower():
                    context = "토스 증권 앱 화면"
                elif "app_store" in image_path.lower():
                    context = "앱스토어 화면"
                else:
                    context = "웹 애플리케이션 화면"
                
                # 분석 실행
                result = self.analyze_image(image_path, context)
                
                if result and result['success']:
                    print(f"🎯 결과: {result['clickable_elements']}")
                else:
                    print("❌ 분석 실패")
                    
            except FileNotFoundError:
                print(f"⚠️ 파일 없음: {image_path}")
                continue
            except Exception as e:
                print(f"❌ 테스트 오류: {e}")
                continue

def main():
    """메인 테스트 함수"""
    print("🧪 Qwen2VL FastAPI 서버 테스트 클라이언트")
    print("=" * 50)
    
    # 클라이언트 초기화
    client = FastAPIClient()
    
    # 서버 상태 확인
    print("1️⃣ 서버 상태 확인")
    if not client.check_server_health():
        print("❌ 서버가 실행되지 않았거나 응답하지 않습니다.")
        print("💡 서버를 먼저 실행해주세요:")
        print("   python qwen2vl_fastapi_server.py")
        return
    
    print("\n2️⃣ 샘플 이미지 테스트")
    client.test_with_sample_images()
    
    print("\n3️⃣ 대화형 테스트")
    while True:
        image_path = input("\n📁 이미지 경로를 입력하세요 (종료: quit): ").strip()
        if image_path.lower() == 'quit':
            break
            
        if not image_path:
            continue
            
        context = input("💬 컨텍스트 입력 (선택사항): ").strip()
        
        result = client.analyze_image(image_path, context)
        if result and result['success']:
            print(f"\n🎯 최종 결과:")
            print(f"   {result['clickable_elements']}")
    
    print("👋 테스트 완료!")

if __name__ == "__main__":
    main() 