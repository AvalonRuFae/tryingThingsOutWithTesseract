#!/usr/bin/env python3
"""
Visual Comparison Script
Shows before and after images side by side for typo detection demo
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_comparison_image():
    """Create a side-by-side comparison of original and annotated images"""
    
    # Load images
    original = cv2.imread('composition_with_typos.png')
    annotated = cv2.imread('annotated_typos.png')
    
    if original is None or annotated is None:
        print("❌ Could not load images")
        return
    
    # Resize images to same height if needed
    height = max(original.shape[0], annotated.shape[0])
    original = cv2.resize(original, (original.shape[1], height))
    annotated = cv2.resize(annotated, (annotated.shape[1], height))
    
    # Create side-by-side comparison
    gap = 20  # Gap between images
    total_width = original.shape[1] + annotated.shape[1] + gap
    comparison = np.ones((height + 60, total_width, 3), dtype=np.uint8) * 255
    
    # Place original image
    comparison[60:60+height, 0:original.shape[1]] = original
    
    # Place annotated image
    comparison[60:60+height, original.shape[1]+gap:] = annotated
    
    # Convert to PIL for text
    comparison_pil = Image.fromarray(cv2.cvtColor(comparison, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(comparison_pil)
    
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        font_subtitle = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
    
    # Add titles
    draw.text((10, 10), "Student Composition Typo Detection Demo", fill='black', font=font_title)
    draw.text((10, 35), "Original Composition", fill='blue', font=font_subtitle)
    draw.text((original.shape[1] + gap + 10, 35), "With Typo Annotations", fill='red', font=font_subtitle)
    
    # Add legend
    legend_x = original.shape[1] + gap + 10
    legend_y = height + 10
    draw.text((legend_x, legend_y), "🔴 Red: Known typos  🟠 Orange: Possible typos", fill='black', font=font_subtitle)
    
    # Convert back and save
    final_image = cv2.cvtColor(np.array(comparison_pil), cv2.COLOR_RGB2BGR)
    cv2.imwrite('typo_comparison.png', final_image)
    print("✅ Comparison image saved: typo_comparison.png")

def print_typo_summary():
    """Print a summary of detected typos"""
    print("\n📋 Typo Detection Summary")
    print("=" * 40)
    
    typos = [
        ("sumer", "summer", "Misspelling"),
        ("familly", "family", "Double letter error"),
        ("wich", "which", "Missing letter"),
        ("whether", "weather", "Wrong word"),
        ("beutiful", "beautiful", "Letter transposition"),
        ("enjoied", "enjoyed", "Wrong suffix"),
        ("swiming", "swimming", "Missing double letter"),
        ("favrite", "favorite", "Missing letter"),
        ("bulding", "building", "Missing letter"),
        ("resturant", "restaurant", "Missing letter"),
        ("delisious", "delicious", "Wrong vowel"),
        ("cant", "can't", "Missing apostrophe")
    ]
    
    print("Found typos with corrections:")
    for typo, correction, error_type in typos:
        print(f"   ❌ '{typo}' → ✅ '{correction}' ({error_type})")
    
    print(f"\nTotal confirmed typos detected: {len(typos)}")

if __name__ == "__main__":
    create_comparison_image()
    print_typo_summary()
