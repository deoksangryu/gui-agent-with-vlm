#!/usr/bin/env python3
"""
🚨 2단계: 토스 이미지 첫 시도 - 문제 발생 
==========================================

기본 설정으로 토스 앱 이미지를 처리했을 때 발생한 문제들을 보여줍니다.
"""

print("🚨 2단계: 토스 이미지 첫 시도 - 문제점들")
print("=" * 50)
print("")
print("❌ 발견된 주요 문제점들:")
print("1. �� 한국어 텍스트 대부분 누락 (영어 OCR만 지원)")
print("2. 🎯 높은 임계값 (0.9)으로 작은 텍스트 미감지")
print("3. 🤖 Florence2 모델 호환성 문제 (generate 메서드 오류)")
print("4. 🔤 '3', '4', '5', '6', '1일', '도방' 등 작은 요소 누락")
print("")
print("📊 기본 설정 결과:")
print("- OCR 텍스트: ~30개 (대부분 영어/숫자만)")
print("- UI 요소: 0개 (캡션 생성 실패)")
print("- 한국어 감지율: 거의 0%")
print("")
print("🔄 실제 문제 재현 명령어:")
print("python ../omniparser_demo.py -i ../toss_page.png -o toss_problematic")
print("")
print("💡 다음 단계: 한국어 OCR 지원 추가 필요")
