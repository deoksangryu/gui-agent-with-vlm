#!/usr/bin/env python3
"""
Image resizing script for GitHub compatibility
"""

import os
from PIL import Image

def resize_image(input_path, output_path, max_width=1200, max_height=800):
    """Resize image while maintaining aspect ratio"""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate new size
            width, height = img.size
            ratio = min(max_width/width, max_height/height)
            new_size = (int(width * ratio), int(height * ratio))
            
            # Resize image
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Save with optimized settings
            resized_img.save(output_path, 'PNG', optimize=True, quality=85)
            
            print(f"Resized {input_path} from {img.size} to {new_size}")
            print(f"Saved as {output_path}")
            
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def main():
    # Resize OmniParser demo image
    input_file = "omniparser/youtube_test_labeled.png"
    output_file = "omniparser/youtube_test_labeled_resized.png"
    
    if os.path.exists(input_file):
        resize_image(input_file, output_file)
    else:
        print(f"Input file {input_file} not found")
    
    # Resize ShowUI demo image
    input_file2 = "showui/showui_result_1753354654.png"
    output_file2 = "showui/showui_result_1753354654_resized.png"
    
    if os.path.exists(input_file2):
        resize_image(input_file2, output_file2)
    else:
        print(f"Input file {input_file2} not found")

if __name__ == "__main__":
    main() 