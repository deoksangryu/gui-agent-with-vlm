#!/usr/bin/env python3
"""
🎯 1단계: OmniParser 기본 데모 - Excel 이미지 성공 사례
=======================================================

이 스크립트는 OmniParser의 기본 기능을 excel.png 예제로 실제 실행합니다.
- 기본 설정으로 UI 요소 검출
- Florence2 캡션 모델 사용
- 영어 OCR만 지원
"""

import sys
import os

# 현재 파일의 위치를 기준으로 상위 디렉토리를 path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import torch
import time
from PIL import Image
import base64
import io
import csv
from util.utils import check_ocr_box, get_yolo_model, get_caption_model_processor, get_som_labeled_img

def run_step1_basic_demo():
    print("=" * 60)
    print("🎯 1단계: OmniParser 기본 데모 - Excel 이미지")
    print("=" * 60)
    print("✅ 이 단계에서는 기본 설정으로 Excel 이미지를 성공적으로 처리합니다.")
    print("📝 영어 OCR과 Florence2 캡션 모델을 사용합니다.")
    print("")
    
    # 기본 설정
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"🔧 Device: {device}")
    
    # 이미지 파일 확인
    image_path = os.path.join(parent_dir, 'imgs', 'excel.png')
    if not os.path.exists(image_path):
        print(f"❌ Excel 이미지 파일을 찾을 수 없습니다: {image_path}")
        print("💡 excel.png 파일을 OmniParser 폴더에 추가해주세요.")
        return False
    
    print(f"🖼️ 이미지 처리 시작: {image_path}")
    
    try:
        # 모델 로딩 (기본 설정)
        print("📦 모델 로딩 중...")
        
        # SOM 모델 (기본)
        som_model_path = os.path.join(parent_dir, 'weights', 'icon_detect', 'model.pt')
        som_model = get_yolo_model(model_path=som_model_path)
        print("✅ SOM 모델 로드 완료")
        
        # 캡션 모델 (Florence2 - 기본)
        caption_model_path = os.path.join(parent_dir, 'weights', 'icon_caption_florence')
        caption_model_processor = get_caption_model_processor(
            model_name="florence2", 
            model_name_or_path=caption_model_path, 
            device=device
        )
        print("✅ Florence2 캡션 모델 로드 완료")
        
        # OCR 처리 (기본 설정 - 영어만)
        print("\n🔍 OCR 처리 중...")
        print("⚠️  기본 설정: 영어 OCR만 지원, 임계값 0.9")
        start_time = time.time()
        
        ocr_bbox_rslt, _ = check_ocr_box(
            image_path,
            display_img=False,
            output_bb_format='xyxy',
            easyocr_args={'paragraph': False, 'text_threshold': 0.9},  # 기본 임계값
            use_paddleocr=False
        )
        text, ocr_bbox = ocr_bbox_rslt
        ocr_time = time.time() - start_time
        
        print(f"⏱️ OCR 완료: {ocr_time:.2f}초, {len(text)}개 텍스트 감지")
        
        # 감지된 텍스트 출력 (일부)
        print("\n📝 감지된 텍스트 (처음 10개):")
        for i, txt in enumerate(text[:10]):
            print(f"  {i}: {txt}")
        if len(text) > 10:
            print(f"  ... 총 {len(text)}개")
        
        # SOM + 캡션 처리
        print("\n🏷️ UI 요소 감지 및 캡션 생성 중...")
        start_time = time.time()
        
        dino_labeled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
            image_path,  # 원본처럼 경로를 전달
            som_model,
            BOX_TRESHOLD=0.05,
            output_coord_in_ratio=True,
            ocr_bbox=ocr_bbox,
            caption_model_processor=caption_model_processor,
            ocr_text=text,
            use_local_semantics=True,
            iou_threshold=0.7,
            scale_img=False,
            batch_size=128
        )
        
        som_time = time.time() - start_time
        print(f"⏱️ UI 요소 감지 완료: {som_time:.2f}초")
        
        # 결과 저장
        output_dir = "step1_results"
        os.makedirs(output_dir, exist_ok=True)
        
        # 라벨된 이미지 저장
        if dino_labeled_img:
            labeled_image = Image.open(io.BytesIO(base64.b64decode(dino_labeled_img)))
            labeled_image.save(f"{output_dir}/excel_labeled.png")
            print(f"💾 라벨된 이미지 저장: {output_dir}/excel_labeled.png")
        
        # OCR 결과 저장
        with open(f"{output_dir}/excel_ocr.txt", 'w', encoding='utf-8') as f:
            f.write("# 1단계 OCR 결과 - 기본 설정 (영어만)\n\n")
            for i, txt in enumerate(text):
                f.write(f"{i}: {txt}\n")
        
        # 요소 결과 저장
        if parsed_content_list:
            with open(f"{output_dir}/excel_elements.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=parsed_content_list[0].keys())
                writer.writeheader()
                writer.writerows(parsed_content_list)
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 1단계 결과 요약:")
        print("=" * 60)
        print(f"✅ OCR 텍스트: {len(text)}개 (영어)")
        print(f"✅ UI 요소: {len(parsed_content_list)}개")
        print(f"✅ 처리 시간: OCR {ocr_time:.2f}초 + SOM {som_time:.2f}초 = {ocr_time + som_time:.2f}초")
        print(f"✅ 결과 저장: {output_dir}/")
        print("\n🎉 Excel 이미지에서 성공적으로 UI 요소들을 감지했습니다!")
        print("📝 영어 텍스트와 아이콘들이 정확히 인식되었습니다.")
        print("💡 이제 토스 이미지에 같은 설정을 적용해보겠습니다 (2단계)")
        
        return True
        
    except Exception as e:
        print(f"❌ 처리 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_step1_basic_demo()
    
    if success:
        print("\n" + "🎯" * 20)
        print("1단계 데모 완료! 다음은 2단계로 진행해보세요.")
        print("python step2_toss_initial_attempt.py")
        print("🎯" * 20)
    else:
        print("\n❌ 1단계 실행 실패. 모델 파일과 이미지를 확인해주세요.") 