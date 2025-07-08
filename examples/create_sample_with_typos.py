#!/usr/bin/env python3
"""
Create a sample student composition with intentional typos
for testing the annotation system.
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

def create_composition_with_typos():
    """Create a handwritten-style composition with common student errors"""
    
    # Create a white canvas
    width, height = 800, 600
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to load a system font, fallback to default
    try:
        # Use a font that looks more handwritten
        font_title = ImageFont.truetype("/System/Library/Fonts/Marker Felt.ttc", 24)
        font_text = ImageFont.truetype("/System/Library/Fonts/Marker Felt.ttc", 18)
    except:
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
            font_text = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
    
    # Title
    title = "My Summer Vacation"
    draw.text((50, 30), title, fill='black', font=font_title)
    
    # Composition with intentional errors
    lines = [
        "Last sumer I went to the beach with my familly.",  # sumer -> summer, familly -> family
        "We stayed at a hotel wich was very nice.",          # wich -> which
        "The whether was perfect and the ocean was beutiful.", # whether -> weather, beutiful -> beautiful
        "I enjoied swiming in the waves every day.",         # enjoied -> enjoyed, swiming -> swimming
        "My favrite activity was bulding sand castles.",     # favrite -> favorite, bulding -> building
        "We also went to a resturant that served delisious", # resturant -> restaurant, delisious -> delicious
        "sea food. I cant wait to go back next year!"        # cant -> can't
    ]
    
    y_pos = 80
    line_spacing = 35
    
    for line in lines:
        draw.text((50, y_pos), line, fill='black', font=font_text)
        y_pos += line_spacing
    
    # Add some margin lines to make it look like notebook paper
    for i in range(10, height - 10, 30):
        draw.line([(40, i), (width - 40, i)], fill='lightblue', width=1)
    
    # Add left margin
    draw.line([(80, 10), (80, height - 10)], fill='red', width=2)
    
    # Save the image
    output_path = 'composition_with_typos.png'
    img.save(output_path)
    print(f"✅ Created sample composition with typos: {output_path}")
    
    return output_path

def create_typo_corrections():
    """Define the typos and their corrections"""
    return {
        'sumer': 'summer',
        'familly': 'family', 
        'wich': 'which',
        'whether': 'weather',
        'beutiful': 'beautiful',
        'enjoied': 'enjoyed',
        'swiming': 'swimming',
        'favrite': 'favorite',
        'bulding': 'building',
        'resturant': 'restaurant',
        'delisious': 'delicious',
        'cant': "can't"
    }

if __name__ == "__main__":
    create_composition_with_typos()
    typos = create_typo_corrections()
    print(f"\n📝 Intentional typos created:")
    for typo, correction in typos.items():
        print(f"   ❌ {typo} → ✅ {correction}")
