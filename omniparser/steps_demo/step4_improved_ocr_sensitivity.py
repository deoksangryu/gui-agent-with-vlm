#!/usr/bin/env python3
"""
🎯 4단계: OCR 민감도 개선
=======================

이 스크립트는 OCR 파라미터를 조정하여 작은 텍스트들도 감지할 수 있도록 개선합니다.
- text_threshold: 0.9 → 0.6 (민감도 증가)
- 추가 파라미터: low_text=0.3, link_threshold=0.4, canvas_size=3000, mag_ratio=1.5
- 작은 텍스트 "1일", "3", "5", "동방" 등 감지 목표
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

def run_step4_improved_ocr():
    print("=" * 60)
    print("🎯 4단계: OCR 민감도 개선")
    print("=" * 60)
    print("✅ 이 단계에서는 OCR 파라미터를 조정하여 작은 텍스트들도 감지합니다.")
    print("📝 임계값 낮추기: 0.9 → 0.6, 추가 파라미터 조정")
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
        
        # OCR 처리 (개선된 민감도 설정)
        print("\n🔍 OCR 처리 중...")
        print("🎯 개선된 설정: 낮은 임계값 0.6 + 추가 파라미터 조정")
        print("   - text_threshold: 0.9 → 0.6")
        print("   - low_text: 0.3 (추가)")
        print("   - link_threshold: 0.4 (추가)")
        print("   - canvas_size: 3000 (추가)")
        print("   - mag_ratio: 1.5 (추가)")
        
        start_time = time.time()
        
        # 개선된 파라미터로 EasyOCR 초기화
        reader = easyocr.Reader(['ko', 'en'], gpu=torch.cuda.is_available())
        
        # 이미지 읽기
        image = Image.open(image_path)
        
        # 개선된 파라미터로 EasyOCR 실행
        results = reader.readtext(
            image_path,
            paragraph=False,
            text_threshold=0.6,      # 낮아진 임계값 (0.9 → 0.6)
            low_text=0.3,            # 낮은 신뢰도 텍스트 감지
            link_threshold=0.4,      # 텍스트 연결 임계값
            width_ths=0.7,
            height_ths=0.7,
            # 추가 성능 파라미터
            canvas_size=3000,        # 캔버스 크기 증가
            mag_ratio=1.5            # 확대 비율
        )
        
        # 결과를 check_ocr_box 형식으로 변환
        text = []
        ocr_bbox = []
        
        for (bbox, txt, conf) in results:
            if conf >= 0.6:  # 낮아진 임계값 적용
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
        small_texts = []  # 작은 텍스트들 (길이 3자 이하)
        
        for i, txt in enumerate(text):
            # 한국어 문자가 포함되어 있는지 확인
            has_korean = any('\uac00' <= char <= '\ud7af' for char in txt)
            if has_korean:
                korean_count += 1
                korean_texts.append(txt)
            else:
                english_count += 1
            
            # 작은 텍스트 확인 (3자 이하)
            if len(txt.strip()) <= 3:
                small_texts.append(txt)
            
            if i < 20:  # 처음 20개 출력
                size_indicator = " (작은 텍스트)" if len(txt.strip()) <= 3 else ""
                print(f"  {i}: {txt} {'(한국어 포함)' if has_korean else '(영어/숫자)'}{size_indicator}")
        
        if len(text) > 20:
            print(f"  ... 총 {len(text)}개")
        
        print(f"\n📊 언어별 분석: 한국어 {korean_count}개, 영어/숫자 {english_count}개")
        print(f"🔍 작은 텍스트: {len(small_texts)}개 (3자 이하)")
        
        # 작은 텍스트들 출력
        if small_texts:
            print("🎯 감지된 작은 텍스트들:")
            for txt in small_texts[:15]:
                print(f"    '{txt}'")
            if len(small_texts) > 15:
                print(f"    ... 총 {len(small_texts)}개")
        
        # 3단계 대비 개선 확인
        print(f"\n✅ 개선 효과: 3단계 ~91개 → 4단계 {len(text)}개 (+{len(text)-91}개)")
        
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
        output_dir = "step4_results"
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
            f.write("# 4단계 OCR 결과 - 민감도 개선\n")
            f.write(f"# 총 {len(text)}개 텍스트, 한국어 {korean_count}개, 영어/숫자 {english_count}개\n")
            f.write(f"# 작은 텍스트 {len(small_texts)}개 (3자 이하)\n\n")
            
            f.write("## 개선된 OCR 파라미터:\n")
            f.write("- text_threshold: 0.9 → 0.6\n")
            f.write("- low_text: 0.3\n")
            f.write("- link_threshold: 0.4\n")
            f.write("- canvas_size: 3000\n")
            f.write("- mag_ratio: 1.5\n\n")
            
            f.write("## 작은 텍스트 목록:\n")
            for txt in small_texts:
                f.write(f"작은텍스트: '{txt}'\n")
            
            f.write("\n## 한국어 텍스트 목록:\n")
            for txt in korean_texts:
                f.write(f"한국어: {txt}\n")
            
            f.write("\n## 전체 텍스트 목록:\n")
            for i, txt in enumerate(text):
                has_korean = any('\uac00' <= char <= '\ud7af' for char in txt)
                size_info = " (작은텍스트)" if len(txt.strip()) <= 3 else ""
                f.write(f"{i}: {txt} {'(한국어)' if has_korean else '(영어/숫자)'}{size_info}\n")
        
        # 요소 결과 저장
        if parsed_content_list:
            with open(f"{output_dir}/toss_elements.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=parsed_content_list[0].keys())
                writer.writeheader()
                writer.writerows(parsed_content_list)
        
        # 3단계 대비 개선점 분석
        print("\n" + "=" * 60)
        print("🎯 4단계 OCR 민감도 개선 결과:")
        print("=" * 60)
        print(f"🔍 OCR 텍스트: {len(text)}개 (한국어 {korean_count}개, 영어/숫자 {english_count}개)")
        print(f"🎯 작은 텍스트: {len(small_texts)}개 (3자 이하)")
        print(f"🏷️ UI 요소: {len(parsed_content_list)}개")
        print(f"⏱️ 처리 시간: OCR {ocr_time:.2f}초")
        print(f"💾 결과 저장: {output_dir}/")
        
        print("\n✅ 4단계 주요 개선사항:")
        print(f"  1. ✅ OCR 민감도 향상: 임계값 0.9 → 0.6")
        print(f"  2. ✅ 작은 텍스트 감지: {len(small_texts)}개 추가")
        print(f"  3. ✅ 전체 텍스트 증가: 3단계 ~91개 → 4단계 {len(text)}개")
        
        # 특별히 찾고 있던 작은 텍스트들 확인
        target_small_texts = ['1일', '3', '4', '5', '6', '동방', '7', '토스']
        found_targets = [txt for txt in text if any(target in txt for target in target_small_texts)]
        if found_targets:
            print(f"  4. ✅ 목표 작은 텍스트 감지: {found_targets}")
        
        remaining_issues = []
        if len(parsed_content_list) == 0:
            remaining_issues.append("UI 요소 감지 실패 (Florence2 문제)")
        
        if remaining_issues:
            print("\n⚠️ 아직 남은 문제:")
            for i, issue in enumerate(remaining_issues, 1):
                print(f"  {i}. {issue}")
        
        print("\n💡 다음 단계 계획:")
        print("  5단계: BLIP2 모델로 UI 요소 감지 문제 해결")
        print("  6단계: 최종 통합 솔루션")
        
        return True
        
    except Exception as e:
        print(f"❌ 처리 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_step4_improved_ocr()
    
    if success:
        print("\n" + "🎯" * 20)
        print("4단계 OCR 민감도 개선 완료! 다음은 5단계로 진행해보세요.")
        print("python step5_blip2_model_switch.py")
        print("🎯" * 20)
    else:
        print("\n❌ 4단계 실행 실패. 모델 파일과 이미지를 확인해주세요.") 