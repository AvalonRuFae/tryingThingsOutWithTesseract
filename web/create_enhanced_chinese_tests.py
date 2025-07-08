#!/usr/bin/env python3
"""
Enhanced Chinese Test Image Generator
Creates test images with different Chinese text styles for OCR testing
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_chinese_test_images():
    """Create multiple Chinese test images with different characteristics"""
    
    # Test texts
    test_texts = {
        'simple': '你好世界！这是一个简单的测试。',
        'complex': '中华人民共和国成立于一九四九年十月一日。北京是中国的首都，拥有丰富的历史文化遗产。',
        'mixed': '今天天气很好，温度25°C。我们计划去参观故宫博物院。',
        'numbers': '学生编号：20231001，姓名：张三，年级：高三年级，班级：3班。',
        'punctuation': '问题：什么是人工智能？答案：AI是计算机科学的一个分支。',
    }
    
    # Create output directory
    output_dir = 'chinese_test_images'
    os.makedirs(output_dir, exist_ok=True)
    
    for test_name, text in test_texts.items():
        # Create different variations for each text
        variations = [
            ('standard', 1200, 400, 48, (255, 255, 255), (0, 0, 0)),
            ('high_res', 2400, 800, 96, (255, 255, 255), (0, 0, 0)),
            ('low_contrast', 1200, 400, 48, (240, 240, 240), (80, 80, 80)),
            ('colored_bg', 1200, 400, 48, (240, 248, 255), (25, 25, 112)),
        ]
        
        for var_name, width, height, font_size, bg_color, text_color in variations:
            try:
                # Create image
                img = Image.new('RGB', (width, height), bg_color)
                draw = ImageDraw.Draw(img)
                
                # Try to use a system Chinese font
                font_paths = [
                    '/System/Library/Fonts/STHeiti Light.ttc',  # macOS
                    '/System/Library/Fonts/STHeitiSC-Light.otf',  # macOS alternative
                    '/System/Library/Fonts/PingFang.ttc',  # macOS Ping Fang
                    'C:/Windows/Fonts/simsun.ttc',  # Windows SimSun
                    'C:/Windows/Fonts/msyh.ttc',  # Windows Microsoft YaHei
                    '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',  # Linux
                    '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # Linux WQY
                ]
                
                font = None
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        try:
                            font = ImageFont.truetype(font_path, font_size)
                            print(f"Using font: {font_path}")
                            break
                        except Exception as e:
                            print(f"Could not load {font_path}: {e}")
                            continue
                
                if font is None:
                    print("Warning: No Chinese font found, using default font")
                    font = ImageFont.load_default()
                
                # Calculate text position for centering
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Add some padding and word wrapping for long text
                max_width = width - 100  # Leave 50px margin on each side
                if text_width > max_width:
                    # Simple word wrapping
                    words = text.split('，')  # Split on Chinese comma
                    if len(words) == 1:
                        words = text.split('。')  # Split on Chinese period
                    if len(words) == 1:
                        # If still too long, split by character count
                        words = [text[i:i+15] for i in range(0, len(text), 15)]
                    
                    lines = []
                    current_line = ""
                    for word in words:
                        test_line = current_line + word + "，" if current_line else word
                        test_bbox = draw.textbbox((0, 0), test_line, font=font)
                        if test_bbox[2] - test_bbox[0] <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                lines.append(current_line.rstrip('，'))
                            current_line = word
                    if current_line:
                        lines.append(current_line.rstrip('，'))
                    
                    # Draw multiple lines
                    line_height = text_height + 10
                    total_height = len(lines) * line_height
                    start_y = (height - total_height) // 2
                    
                    for i, line in enumerate(lines):
                        line_bbox = draw.textbbox((0, 0), line, font=font)
                        line_width = line_bbox[2] - line_bbox[0]
                        x = (width - line_width) // 2
                        y = start_y + i * line_height
                        draw.text((x, y), line, font=font, fill=text_color)
                else:
                    # Single line - center it
                    x = (width - text_width) // 2
                    y = (height - text_height) // 2
                    draw.text((x, y), text, font=font, fill=text_color)
                
                # Save image
                filename = f"{output_dir}/{test_name}_{var_name}.png"
                img.save(filename, 'PNG', optimize=True, quality=95)
                print(f"Created: {filename}")
                
            except Exception as e:
                print(f"Error creating {test_name}_{var_name}: {e}")
    
    # Create a composite image showing all variations
    try:
        create_comparison_image(output_dir)
    except Exception as e:
        print(f"Error creating comparison image: {e}")
    
    print(f"\n✅ Chinese test images created in '{output_dir}' directory")
    print("🧪 Test these images with your OCR system to identify the best settings!")

def create_comparison_image(output_dir):
    """Create a single image showing multiple test samples"""
    
    # Simple comparison texts
    texts = [
        '测试文本一：你好世界！',
        '测试文本二：人工智能',
        '测试文本三：学习中文',
        '测试文本四：北京大学'
    ]
    
    img = Image.new('RGB', (1600, 1200), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Find system font
    font_paths = [
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/System/Library/Fonts/PingFang.ttc',
        'C:/Windows/Fonts/simsun.ttc',
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
    ]
    
    font = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, 72)
                break
            except:
                continue
    
    if font is None:
        font = ImageFont.load_default()
    
    # Draw texts in grid
    y_positions = [200, 400, 600, 800]
    for i, text in enumerate(texts):
        draw.text((200, y_positions[i]), text, font=font, fill=(0, 0, 0))
    
    # Add title
    title_font = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                title_font = ImageFont.truetype(font_path, 48)
                break
            except:
                continue
    
    if title_font is None:
        title_font = font
    
    draw.text((400, 50), '中文OCR测试图片', font=title_font, fill=(0, 0, 0))
    
    img.save(f"{output_dir}/comparison_test.png", 'PNG', optimize=True, quality=95)
    print(f"Created comparison image: {output_dir}/comparison_test.png")

if __name__ == "__main__":
    create_chinese_test_images()
