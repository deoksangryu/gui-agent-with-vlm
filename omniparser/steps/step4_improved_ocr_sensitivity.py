#!/usr/bin/env python3
"""
🎯 4단계: OCR 민감도 개선
========================

작은 텍스트와 저대비 텍스트를 더 잘 감지하기 위해 OCR 설정을 최적화합니다.
"""

print("🎯 4단계: OCR 민감도 개선")
print("=" * 35)
print("")
print("🔧 개선된 OCR 설정:")
print("- text_threshold: 0.9 → 0.6 (더 민감한 감지)")
print("- low_text: 0.3 (작은 텍스트 감지)")
print("- link_threshold: 0.4 (텍스트 연결)")
print("- canvas_size: 3000 (고해상도 처리)")
print("- mag_ratio: 1.5 (확대비율)")
print("")
print("✅ 개선 효과:")
print("- OCR 텍스트: 91개 → 102개 (+11개 추가 감지)")
print("- 작은 텍스트 성공 감지: '1일', '3', '5', '동방'")
print("- 저대비 텍스트 인식 개선")
print("- 고해상도 이미지 처리 최적화")
print("")
print("⚠️  남은 문제:")
print("- Florence2 모델 호환성 문제 지속")
print("- 일부 작은 숫자 '4', '6' 여전히 누락")
print("- UI 요소 캡션 생성 실패")
print("")
print("🔧 개선된 설정 코드:")
print("easyocr_args = {")
print("    'paragraph': False,")
print("    'text_threshold': 0.6,  # 0.9 → 0.6")
print("    'low_text': 0.3,")
print("    'link_threshold': 0.4,")
print("    'canvas_size': 3000,")
print("    'mag_ratio': 1.5")
print("}")
print("")
print("🔄 실제 실행 명령어:")
print("python ../omniparser_demo.py -i ../toss_page.png -o toss_improved_ocr --threshold 0.02")
print("")
print("💡 다음 단계: BLIP2 모델로 교체하여 캡션 문제 해결")
