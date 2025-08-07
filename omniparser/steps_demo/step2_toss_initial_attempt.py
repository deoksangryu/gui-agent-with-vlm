#!/usr/bin/env python3
"""
⚠️ 2단계: 토스 앱 초기 시도 - 문제점 발견
=======================================

이 스크립트는 토스 한국어 앱 이미지를 기본 설정으로 처리하여 문제점을 보여줍니다.
- 기본 설정(영어 OCR, 높은 임계값)으로 토스 이미지 처리
- 한국어 텍스트 인식 실패 문제 확인
- Florence2 모델 호환성 문제 확인
"""

import sys
import os
sys.path.append('..')

import torch
import time
from PIL import Image
import base64
import io
import csv
from util.utils import check_ocr_box, get_yolo_model, get_caption_model_processor, get_som_labeled_img

def run_step2_toss_initial():
    print("=" * 60)
    print("⚠️ 2단계: 토스 앱 초기 시도 - 문제점 발견")
    print("=" * 60)
    print("❌ 이 단계에서는 기본 설정으로 토스 이미지를 처리하여 문제점을 확인합니다.")
    print("📝 영어 OCR만 사용하여 한국어 텍스트가 감지되지 않을 것입니다.")
    print("")
    
    # 기본 설정 (1단계와 동일)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"🔧 Device: {device}")
    
    # 토스 이미지 파일 확인
    image_path = '../imgs/toss_page.png'
    if not os.path.exists(image_path):
        print(f"❌ 토스 이미지 파일을 찾을 수 없습니다: {image_path}")
        print("💡 toss_page.png 파일을 OmniParser/imgs/ 폴더에 추가해주세요.")
        return False
    
    print(f"🖼️ 토스 이미지 처리 시작: {image_path}")
    
    try:
        # 모델 로딩 (기본 설정)
        print("📦 모델 로딩 중...")
        
        # SOM 모델 (기본)
        som_model = get_yolo_model(model_path='../weights/icon_detect/model.pt')
        print("✅ SOM 모델 로드 완료")
        
        # 캡션 모델 (Florence2 - 기본, 문제가 될 수 있음)
        try:
            caption_model_processor = get_caption_model_processor(
                model_name="florence2", 
                model_name_or_path="../weights/icon_caption_florence", 
                device=device
            )
            print("✅ Florence2 캡션 모델 로드 완료")
            florence2_loaded = True
        except Exception as e:
            print(f"⚠️ Florence2 모델 로드 실패: {e}")
            print("💡 이 문제는 5단계에서 BLIP2로 해결할 예정입니다.")
            caption_model_processor = None
            florence2_loaded = False
        
        # OCR 처리 (기본 설정 - 영어만, 높은 임계값)
        print("\n🔍 OCR 처리 중...")
        print("⚠️  문제가 될 설정: 영어 OCR만 지원, 높은 임계값 0.9")
        start_time = time.time()
        
        ocr_bbox_rslt, _ = check_ocr_box(
            image_path,
            display_img=False,
            output_bb_format='xyxy',
            easyocr_args={'paragraph': False, 'text_threshold': 0.9},  # 높은 임계값 (문제)
            use_paddleocr=False
        )
        text, ocr_bbox = ocr_bbox_rslt
        ocr_time = time.time() - start_time
        
        print(f"⏱️ OCR 완료: {ocr_time:.2f}초, {len(text)}개 텍스트 감지")
        
        # 감지된 텍스트 분석
        print("\n📝 감지된 텍스트 분석:")
        korean_count = 0
        english_count = 0
        
        for i, txt in enumerate(text):
            # 한국어 문자가 포함되어 있는지 확인
            has_korean = any('\uac00' <= char <= '\ud7af' for char in txt)
            if has_korean:
                korean_count += 1
            else:
                english_count += 1
            
            if i < 10:  # 처음 10개만 출력
                print(f"  {i}: {txt} {'(한국어 포함)' if has_korean else '(영어/숫자)'}")
        
        if len(text) > 10:
            print(f"  ... 총 {len(text)}개")
        
        print(f"📊 언어별 분석: 한국어 {korean_count}개, 영어/숫자 {english_count}개")
        
        if korean_count == 0:
            print("❌ 문제 확인: 한국어 텍스트가 전혀 감지되지 않음!")
            print("💡 해결 방법: 3단계에서 한국어 OCR 지원 추가 예정")
        
        # SOM + 캡션 처리 (Florence2 문제 확인)
        if florence2_loaded and caption_model_processor:
            print("\n🏷️ UI 요소 감지 및 캡션 생성 시도 중...")
            try:
                start_time = time.time()
                
                # 이미지 열기
                image = Image.open(image_path)
                
                dino_labeled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
                    image,
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
                
            except Exception as e:
                print(f"❌ Florence2 캡션 생성 실패: {e}")
                print("💡 해결 방법: 5단계에서 BLIP2 모델로 교체 예정")
                dino_labeled_img = None
                parsed_content_list = []
        else:
            print("\n⚠️ 캡션 모델이 로드되지 않아 UI 요소 감지를 건너뜁니다.")
            dino_labeled_img = None
            parsed_content_list = []
        
        # 결과 저장
        output_dir = "step2_results"
        os.makedirs(output_dir, exist_ok=True)
        
        # 라벨된 이미지 저장 (가능한 경우)
        if dino_labeled_img:
            labeled_image = Image.open(io.BytesIO(base64.b64decode(dino_labeled_img)))
            labeled_image.save(f"{output_dir}/toss_labeled.png")
            print(f"💾 라벨된 이미지 저장: {output_dir}/toss_labeled.png")
        else:
            print("⚠️ 라벨된 이미지 생성 실패")
        
        # OCR 결과 저장
        with open(f"{output_dir}/toss_ocr.txt", 'w', encoding='utf-8') as f:
            f.write("# 2단계 OCR 결과 - 기본 설정 (문제점 확인)\n")
            f.write(f"# 총 {len(text)}개 텍스트, 한국어 {korean_count}개, 영어/숫자 {english_count}개\n\n")
            for i, txt in enumerate(text):
                has_korean = any('\uac00' <= char <= '\ud7af' for char in txt)
                f.write(f"{i}: {txt} {'(한국어)' if has_korean else '(영어/숫자)'}\n")
        
        # 요소 결과 저장
        if parsed_content_list:
            with open(f"{output_dir}/toss_elements.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=parsed_content_list[0].keys())
                writer.writeheader()
                writer.writerows(parsed_content_list)
        
        # 문제점 분석 결과
        print("\n" + "=" * 60)
        print("❌ 2단계 문제점 분석:")
        print("=" * 60)
        print(f"🔍 OCR 텍스트: {len(text)}개 (한국어 {korean_count}개, 영어/숫자 {english_count}개)")
        print(f"🏷️ UI 요소: {len(parsed_content_list)}개")
        print(f"⏱️ 처리 시간: OCR {ocr_time:.2f}초")
        print(f"💾 결과 저장: {output_dir}/")
        
        print("\n🚨 발견된 주요 문제점들:")
        if korean_count == 0:
            print("  1. ❌ 한국어 텍스트 감지 실패 (영어 OCR만 사용)")
        if len(parsed_content_list) == 0:
            print("  2. ❌ UI 요소 감지 실패 (Florence2 모델 문제)")
        if len(text) < 30:
            print("  3. ❌ 전체적으로 적은 텍스트 감지 (높은 임계값 0.9)")
        
        print("\n💡 해결 계획:")
        print("  3단계: 한국어 OCR 지원 추가")
        print("  4단계: OCR 민감도 개선")
        print("  5단계: BLIP2 모델로 교체")
        print("  6단계: 최종 통합 솔루션")
        
        return True
        
    except Exception as e:
        print(f"❌ 처리 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_step2_toss_initial()
    
    if success:
        print("\n" + "⚠️" * 20)
        print("2단계 문제점 확인 완료! 다음은 3단계로 진행해보세요.")
        print("python step3_korean_ocr_support.py")
        print("⚠️" * 20)
    else:
        print("\n❌ 2단계 실행 실패. 모델 파일과 이미지를 확인해주세요.") 