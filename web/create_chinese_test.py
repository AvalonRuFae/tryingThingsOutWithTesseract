#!/usr/bin/env python3
"""
Create a simple Chinese test image for OCR testing
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_chinese_test_image():
    # Create a white background image
    width, height = 800, 300
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Sample Chinese text (simple, clear characters)
    chinese_text = """你好世界
这是一个测试
中文文字识别
欢迎使用程序"""
    
    try:
        # Try to use a system Chinese font
        font_paths = [
            '/System/Library/Fonts/Arial Unicode MS.ttf',  # macOS
            '/System/Library/Fonts/PingFang.ttc',          # macOS
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',  # Linux
            'C:/Windows/Fonts/msyh.ttc',                   # Windows
            'C:/Windows/Fonts/simsun.ttc',                 # Windows
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, 32)
                    print(f"✅ Using font: {font_path}")
                    break
                except:
                    continue
        
        if not font:
            print("⚠️  No Chinese font found, using default")
            font = ImageFont.load_default()
    
    except Exception as e:
        print(f"Font loading error: {e}")
        font = ImageFont.load_default()
    
    # Draw text with good spacing
    lines = chinese_text.strip().split('\n')
    y_offset = 50
    line_height = 60
    
    for line in lines:
        # Calculate text width for centering
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x_position = (width - text_width) // 2
        
        draw.text((x_position, y_offset), line, fill='black', font=font)
        y_offset += line_height
    
    # Save the image
    output_path = '../data/input/chinese_test.png'
    img.save(output_path)
    print(f"📷 Chinese test image created: {output_path}")
    print("🎯 Text content:")
    for line in lines:
        print(f"   {line}")
    
    return output_path

if __name__ == "__main__":
    create_chinese_test_image()
