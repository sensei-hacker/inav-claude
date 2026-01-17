#!/usr/bin/env python3
"""
Generate YouTube thumbnail for Context Engineering presentation
Creates a split-screen before/after comparison
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Thumbnail dimensions (YouTube standard)
WIDTH = 1280
HEIGHT = 720

# Colors
RED_BG = (229, 57, 53)  # Problem side
RED_LIGHT = (255, 205, 210)
GREEN_BG = (67, 160, 71)  # Solution side
GREEN_LIGHT = (200, 230, 201)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (50, 50, 50)

def create_thumbnail():
    # Create base image
    img = Image.new('RGB', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    # Split screen - left (problem) and right (solution)
    split_x = WIDTH // 2

    # Left side - RED (problem)
    draw.rectangle([0, 0, split_x, HEIGHT], fill=RED_BG)

    # Right side - GREEN (solution)
    draw.rectangle([split_x, 0, WIDTH, HEIGHT], fill=GREEN_BG)

    # Try to load fonts (fallback to default if not available)
    try:
        # Large font for numbers
        font_huge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except:
        # Fallback to default
        font_huge = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # LEFT SIDE - Problem visualization
    # Title
    left_title = "❌ Overloaded"
    draw.text((split_x // 2, 80), left_title, fill=WHITE, font=font_large, anchor="mm",
              stroke_width=3, stroke_fill=BLACK)

    # Simulate overflowing text (saturated context)
    overflow_text = [
        "100k lines of code...",
        "5k lines of docs...",
        "Build instructions...",
        "Testing guides...",
        "Architecture docs...",
        "Project tracking...",
        "MSP protocol...",
        "Configuration...",
        "Error handling...",
        "..."
    ]

    y_pos = 200
    for i, line in enumerate(overflow_text):
        # Make text progressively more faded/cut off
        alpha = max(20, 255 - (i * 20))
        color = (255, alpha, alpha, alpha) if i < 8 else (255, 255, 255, 100)
        draw.text((20, y_pos), line, fill=color, font=font_small)
        y_pos += 40
        if i == 7:
            # Draw a "fade out" effect
            draw.text((20, y_pos), "[context limit reached]", fill=(255, 150, 150), font=font_small)
            break

    # Big number at bottom
    draw.text((split_x // 2, HEIGHT - 100), "110K", fill=WHITE, font=font_huge, anchor="mm",
              stroke_width=4, stroke_fill=BLACK)
    draw.text((split_x // 2, HEIGHT - 40), "LINES", fill=WHITE, font=font_medium, anchor="mm")

    # RIGHT SIDE - Solution visualization
    # Title
    right_title = "✅ Focused"
    draw.text((split_x + split_x // 2, 80), right_title, fill=WHITE, font=font_large, anchor="mm",
              stroke_width=3, stroke_fill=BLACK)

    # Clean box showing organized context
    box_left = split_x + 60
    box_top = 200
    box_width = 560
    box_height = 280

    # Draw clean box
    draw.rectangle([box_left, box_top, box_left + box_width, box_top + box_height],
                   outline=WHITE, width=4, fill=(50, 120, 60))

    # Organized sections
    sections = [
        "Developer Role",
        "",
        # "─────────────",
        "✓ Coding standards",
        "✓ Testing guide",
        "✓ Build agent",
        "✓ Current task only",
    ]

    y_pos = box_top + 30
    for line in sections:
        if "─" in line:
            draw.text((box_left + box_width // 2, y_pos), line, fill=WHITE, font=font_small, anchor="mm")
        else:
            draw.text((box_left + 20, y_pos), line, fill=WHITE, font=font_small)
        y_pos += 40

    # Big number at bottom
    draw.text((split_x + split_x // 2, HEIGHT - 100), "250", fill=WHITE, font=font_huge, anchor="mm",
              stroke_width=4, stroke_fill=BLACK)
    draw.text((split_x + split_x // 2, HEIGHT - 40), "LINES", fill=WHITE, font=font_medium, anchor="mm")

    # Draw arrow in the middle
    arrow_y = HEIGHT - 70
    arrow_start_x = split_x - 80
    arrow_end_x = split_x + 80

    # Arrow line
    draw.line([arrow_start_x, arrow_y, arrow_end_x, arrow_y], fill=WHITE, width=8)
    # Arrow head
    draw.polygon([
        (arrow_end_x, arrow_y),
        (arrow_end_x - 30, arrow_y - 20),
        (arrow_end_x - 30, arrow_y + 20)
    ], fill=WHITE)

    return img

def main():
    print("Generating YouTube thumbnail...")
    img = create_thumbnail()

    # Save to presentation directory
    output_path = "youtube-thumbnail.png"
    img.save(output_path, "PNG", quality=95)

    print(f"✓ Thumbnail saved to: {output_path}")
    print(f"  Dimensions: {WIDTH}x{HEIGHT} pixels")
    print(f"  File size: {os.path.getsize(output_path) / 1024:.1f} KB")
    print("\nNext steps:")
    print("  1. Review the thumbnail")
    print("  2. Adjust colors/text if needed")
    print("  3. Upload to YouTube when publishing")

if __name__ == "__main__":
    main()
