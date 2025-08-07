#!/usr/bin/env python3
"""
OmniParser Demo Script
Based on the demo.ipynb notebook, this script demonstrates how to use OmniParser
to analyze UI elements in images.
"""

import os
import sys
import time
import base64
import argparse
from pathlib import Path
from PIL import Image
import pandas as pd
import torch

# Add the current directory to Python path for imports
sys.path.append('.')
sys.path.append('./util')

from util.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model

class OmniParserDemo:
    def __init__(self, device='auto', som_model_path=None, caption_model_name="blip2", caption_model_path=None):
        """
        Initialize OmniParser Demo
        
        Args:
            device: 'cuda', 'cpu', or 'auto' for automatic detection
            som_model_path: Path to SOM model, if None will try to find available models
            caption_model_name: 'florence2' or 'blip2'
            caption_model_path: Path to caption model, if None will use default
        """
        # Device setup
        if device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        print(f"🔧 Using device: {self.device}")
        
        # Load SOM model
        self.som_model = self._load_som_model(som_model_path)
        
        # Load caption model
        self.caption_model_processor = self._load_caption_model(caption_model_name, caption_model_path)
        
        print("✅ OmniParser Demo initialized successfully!")
    
    def _load_som_model(self, model_path):
        """Load SOM (Set-of-Mark) model"""
        possible_paths = [
            model_path,
            'weights/icon_detect/model.pt',
            'icon_detect.pt',
            'yolo11n.pt'  # fallback to basic YOLO model
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                print(f"📦 Loading SOM model from: {path}")
                try:
                    som_model = get_yolo_model(path)
                    som_model.to(self.device)
                    return som_model
                except Exception as e:
                    print(f"❌ Failed to load {path}: {e}")
                    continue
        
        # If no model found, try to download a basic YOLO model
        print("📥 Downloading basic YOLO model...")
        try:
            from ultralytics import YOLO
            som_model = YOLO('yolo11n.pt')  # This will auto-download
            som_model.to(self.device)
            return som_model
        except Exception as e:
            raise RuntimeError(f"Failed to load any SOM model: {e}")
    
    def _load_caption_model(self, model_name, model_path):
        """Load caption model"""
        possible_paths = [
            model_path,
            'Salesforce/blip2-opt-2.7b',  # BLIP2 primary option
            'weights/icon_caption_florence',
            'microsoft/Florence-2-base',  # Florence2 fallback
        ]
        
        for path in possible_paths:
            if not path:
                continue
                
            print(f"📦 Loading caption model: {model_name} from {path}")
            try:
                caption_model_processor = get_caption_model_processor(
                    model_name=model_name, 
                    model_name_or_path=path, 
                    device=self.device
                )
                return caption_model_processor
            except Exception as e:
                print(f"❌ Failed to load {path}: {e}")
                continue
        
        raise RuntimeError(f"Failed to load any caption model")
    
    def process_image(self, image_path, box_threshold=0.05, output_dir="results"):
        """
        Process an image and extract UI elements
        
        Args:
            image_path: Path to input image
            box_threshold: Confidence threshold for detection
            output_dir: Directory to save results
        
        Returns:
            tuple: (labeled_image_base64, parsed_content_list, ocr_results)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        print(f"🖼️ Processing image: {image_path}")
        
        # Load and prepare image
        image = Image.open(image_path)
        image_rgb = image.convert('RGB')
        print(f"📏 Image size: {image.size}")
        
        # Calculate box overlay ratio for drawing
        box_overlay_ratio = max(image.size) / 3200
        draw_bbox_config = {
            'text_scale': 0.8 * box_overlay_ratio,
            'text_thickness': max(int(2 * box_overlay_ratio), 1),
            'text_padding': max(int(3 * box_overlay_ratio), 1),
            'thickness': max(int(3 * box_overlay_ratio), 1),
        }
        
        # Step 1: OCR detection
        print("🔍 Running OCR detection...")
        start_time = time.time()
        try:
            ocr_bbox_rslt, is_goal_filtered = check_ocr_box(
                image_path, 
                display_img=False, 
                output_bb_format='xyxy', 
                goal_filtering=None, 
                easyocr_args={
                    'paragraph': False, 
                    'text_threshold': 0.6,  # Lowered from 0.9 to 0.6 for more sensitive detection
                    'low_text': 0.3,       # Added for better small text detection
                    'link_threshold': 0.4,  # Added for better text linking
                    'canvas_size': 3000,    # Increased canvas size for high-res images
                    'mag_ratio': 1.5        # Magnification ratio for better recognition
                }, 
                use_paddleocr=False  # Use EasyOCR with Korean support
            )
            text, ocr_bbox = ocr_bbox_rslt
            ocr_time = time.time() - start_time
            print(f"⏱️ OCR completed in {ocr_time:.2f}s, found {len(text)} text items")
        except Exception as e:
            print(f"⚠️ OCR failed, continuing without OCR: {e}")
            text, ocr_bbox = [], []
        
        # Step 2: SOM labeling and caption generation
        print("🏷️ Running SOM labeling and caption generation...")
        start_time = time.time()
        try:
            dino_labeled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
                image_path, 
                self.som_model, 
                BOX_TRESHOLD=box_threshold, 
                output_coord_in_ratio=True, 
                ocr_bbox=ocr_bbox,
                draw_bbox_config=draw_bbox_config, 
                caption_model_processor=self.caption_model_processor, 
                ocr_text=text,
                use_local_semantics=True, 
                iou_threshold=0.7, 
                scale_img=False, 
                batch_size=128
            )
            caption_time = time.time() - start_time
            print(f"⏱️ Caption generation completed in {caption_time:.2f}s")
            
            # Handle empty results
            if parsed_content_list is None:
                parsed_content_list = []
            if not isinstance(parsed_content_list, list):
                parsed_content_list = []
                
            print(f"📊 Found {len(parsed_content_list)} UI elements")
            
        except Exception as e:
            print(f"⚠️ SOM labeling failed: {e}")
            print("Creating minimal result...")
            # Create a minimal result to avoid crash
            import io
            buffer = io.BytesIO()
            Image.open(image_path).convert('RGB').save(buffer, format='PNG')
            dino_labeled_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
            parsed_content_list = []
        
        # Save results
        os.makedirs(output_dir, exist_ok=True)
        self._save_results(image_path, dino_labeled_img, parsed_content_list, text, output_dir)
        
        return dino_labeled_img, parsed_content_list, (text, ocr_bbox)
    
    def _save_results(self, original_image_path, labeled_image_base64, parsed_content_list, ocr_text, output_dir):
        """Save processing results to files"""
        base_name = Path(original_image_path).stem
        
        # Save labeled image
        labeled_image_path = os.path.join(output_dir, f"{base_name}_labeled.png")
        with open(labeled_image_path, "wb") as f:
            f.write(base64.b64decode(labeled_image_base64))
        print(f"💾 Labeled image saved: {labeled_image_path}")
        
        # Save parsed content as CSV
        if parsed_content_list:
            df = pd.DataFrame(parsed_content_list)
            df['ID'] = range(len(df))
            csv_path = os.path.join(output_dir, f"{base_name}_elements.csv")
            df.to_csv(csv_path, index=False)
            print(f"💾 Elements data saved: {csv_path}")
        
        # Save OCR text
        if ocr_text:
            ocr_path = os.path.join(output_dir, f"{base_name}_ocr.txt")
            with open(ocr_path, "w", encoding="utf-8") as f:
                for text_item in ocr_text:
                    f.write(f"{text_item}\n")
            print(f"💾 OCR text saved: {ocr_path}")

def main():
    parser = argparse.ArgumentParser(description="OmniParser Demo - UI Element Detection and Analysis")
    parser.add_argument("--image", "-i", required=True, help="Path to input image")
    parser.add_argument("--output", "-o", default="results", help="Output directory")
    parser.add_argument("--threshold", "-t", type=float, default=0.05, help="Box detection threshold")
    parser.add_argument("--device", "-d", default="auto", choices=["auto", "cuda", "cpu"], help="Device to use")
    parser.add_argument("--som-model", help="Path to SOM model")
    parser.add_argument("--caption-model", default="blip2", choices=["florence2", "blip2"], help="Caption model")
    parser.add_argument("--caption-path", help="Path to caption model")
    
    args = parser.parse_args()
    
    print("🚀 Starting OmniParser Demo")
    print("=" * 50)
    
    try:
        # Initialize demo
        demo = OmniParserDemo(
            device=args.device,
            som_model_path=args.som_model,
            caption_model_name=args.caption_model,
            caption_model_path=args.caption_path
        )
        
        # Process image
        labeled_img, elements, ocr_results = demo.process_image(
            args.image, 
            box_threshold=args.threshold,
            output_dir=args.output
        )
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Processing Summary:")
        print(f"   • Detected elements: {len(elements)}")
        print(f"   • OCR text items: {len(ocr_results[0])}")
        print(f"   • Results saved to: {args.output}/")
        print("✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 