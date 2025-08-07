#!/usr/bin/env python3
"""
🇰🇷 3단계: 한국어 OCR 지원 추가
==============================

이 스크립트는 EasyOCR 언어 설정을 수정하여 한국어 텍스트 감지를 활성화합니다.
- EasyOCR 언어: ['en'] → ['ko', 'en']
- 한국어 텍스트 "토스증권", "주식", "코스피" 등 감지 가능
- OCR 텍스트 수 크게 증가 예상 (~30개 → ~91개)
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
import easyocr
from util.utils import check_ocr_box, get_yolo_model, get_caption_model_processor, get_som_labeled_img

def run_step3_korean_ocr():
    print("=" * 60)
    print("🇰🇷 3단계: 한국어 OCR 지원 추가")
    print("=" * 60)
    print("✅ 이 단계에서는 EasyOCR 언어 설정을 수정하여 한국어 텍스트를 감지합니다.")
    print("📝 언어 설정: ['en'] → ['ko', 'en']")
    print("")
    
    # 기본 설정
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
        # 모델 로딩
        print("📦 모델 로딩 중...")
        
        # SOM 모델
        som_model = get_yolo_model(model_path='../weights/icon_detect/model.pt')
        print("✅ SOM 모델 로드 완료")
        
        # 캡션 모델 (Florence2 - 여전히 문제가 있을 수 있음)
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
        
        # OCR 처리 (한국어 지원 추가)
        print("\n🔍 OCR 처리 중...")
        print("🇰🇷 새로운 설정: 한국어+영어 OCR 지원, 임계값 0.9 유지")
        start_time = time.time()
        
        # 한국어 지원을 위한 EasyOCR 초기화
        reader = easyocr.Reader(['ko', 'en'], gpu=torch.cuda.is_available())
        
        # 이미지 읽기
        image = Image.open(image_path)
        
        # EasyOCR로 텍스트 감지
        results = reader.readtext(
            image_path,
            paragraph=False,
            text_threshold=0.9,  # 아직 높은 임계값 유지
            width_ths=0.7,
            height_ths=0.7
        )
        
        # 결과를 check_ocr_box 형식으로 변환
        text = []
        ocr_bbox = []
        
        for (bbox, txt, conf) in results:
            if conf >= 0.9:  # 임계값 확인
                text.append(txt)
                # bbox를 xyxy 형식으로 변환
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                x1, y1 = min(x_coords), min(y_coords)
                x2, y2 = max(x_coords), max(y_coords)
                ocr_bbox.append([x1, y1, x2, y2])
        
        ocr_time = time.time() - start_time
        print(f"⏱️ OCR 완료: {ocr_time:.2f}초, {len(text)}개 텍스트 감지")
        
        # 감지된 텍스트 분석
        print("\n📝 감지된 텍스트 분석:")
        korean_count = 0
        english_count = 0
        korean_texts = []
        
        for i, txt in enumerate(text):
            # 한국어 문자가 포함되어 있는지 확인
            has_korean = any('\uac00' <= char <= '\ud7af' for char in txt)
            if has_korean:
                korean_count += 1
                korean_texts.append(txt)
            else:
                english_count += 1
            
            if i < 15:  # 처음 15개 출력
                print(f"  {i}: {txt} {'(한국어 포함)' if has_korean else '(영어/숫자)'}")
        
        if len(text) > 15:
            print(f"  ... 총 {len(text)}개")
        
        print(f"\n📊 언어별 분석: 한국어 {korean_count}개, 영어/숫자 {english_count}개")
        
        # 한국어 텍스트 향상도 확인
        if korean_count > 0:
            print("✅ 성공: 한국어 텍스트 감지됨!")
            print("🇰🇷 주요 한국어 텍스트:")
            for i, txt in enumerate(korean_texts[:10]):
                print(f"    {txt}")
            if len(korean_texts) > 10:
                print(f"    ... 총 {len(korean_texts)}개")
        
        # SOM + 캡션 처리 (여전히 Florence2 문제 있을 수 있음)
        if florence2_loaded and caption_model_processor:
            print("\n🏷️ UI 요소 감지 및 캡션 생성 시도 중...")
            try:
                start_time = time.time()
                
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
        output_dir = "step3_results"
        os.makedirs(output_dir, exist_ok=True)
        
        # 라벨된 이미지 저장 (가능한 경우)
        if dino_labeled_img:
            labeled_image = Image.open(io.BytesIO(base64.b64decode(dino_labeled_img)))
            labeled_image.save(f"{output_dir}/toss_labeled.png")
            print(f"💾 라벨된 이미지 저장: {output_dir}/toss_labeled.png")
        else:
            print("⚠️ 라벨된 이미지 생성 실패 (Florence2 문제)")
        
        # OCR 결과 저장
        with open(f"{output_dir}/toss_ocr.txt", 'w', encoding='utf-8') as f:
            f.write("# 3단계 OCR 결과 - 한국어 지원 추가\n")
            f.write(f"# 총 {len(text)}개 텍스트, 한국어 {korean_count}개, 영어/숫자 {english_count}개\n\n")
            f.write("## 한국어 텍스트 목록:\n")
            for txt in korean_texts:
                f.write(f"한국어: {txt}\n")
            f.write("\n## 전체 텍스트 목록:\n")
            for i, txt in enumerate(text):
                has_korean = any('\uac00' <= char <= '\ud7af' for char in txt)
                f.write(f"{i}: {txt} {'(한국어)' if has_korean else '(영어/숫자)'}\n")
        
        # 요소 결과 저장
        if parsed_content_list:
            with open(f"{output_dir}/toss_elements.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=parsed_content_list[0].keys())
                writer.writeheader()
                writer.writerows(parsed_content_list)
        
        # 2단계 대비 개선점 분석
        print("\n" + "=" * 60)
        print("🇰🇷 3단계 한국어 OCR 결과:")
        print("=" * 60)
        print(f"🔍 OCR 텍스트: {len(text)}개 (한국어 {korean_count}개, 영어/숫자 {english_count}개)")
        print(f"🏷️ UI 요소: {len(parsed_content_list)}개")
        print(f"⏱️ 처리 시간: OCR {ocr_time:.2f}초")
        print(f"💾 결과 저장: {output_dir}/")
        
        print("\n✅ 3단계 주요 개선사항:")
        if korean_count > 0:
            print(f"  1. ✅ 한국어 텍스트 감지 성공: {korean_count}개")
            print(f"     주요 텍스트: {', '.join(korean_texts[:5])}")
        print(f"  2. ✅ 전체 텍스트 증가: ~30개 → {len(text)}개")
        
        remaining_issues = []
        if len(parsed_content_list) == 0:
            remaining_issues.append("UI 요소 감지 실패 (Florence2 문제)")
        if korean_count < 20:
            remaining_issues.append("작은 한국어 텍스트 일부 누락 (높은 임계값)")
        
        if remaining_issues:
            print("\n⚠️ 아직 남은 문제:")
            for i, issue in enumerate(remaining_issues, 1):
                print(f"  {i}. {issue}")
        
        print("\n💡 다음 단계 계획:")
        print("  4단계: OCR 민감도 개선 (임계값 낮추기)")
        print("  5단계: BLIP2 모델로 UI 요소 감지 문제 해결")
        
        return True
        
    except Exception as e:
        print(f"❌ 처리 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_step3_korean_ocr()
    
    if success:
        print("\n" + "🇰🇷" * 20)
        print("3단계 한국어 OCR 지원 완료! 다음은 4단계로 진행해보세요.")
        print("python step4_improved_ocr_sensitivity.py")
        print("🇰🇷" * 20)
    else:
        print("\n❌ 3단계 실행 실패. 모델 파일과 이미지를 확인해주세요.") 