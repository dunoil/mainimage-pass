"""Create a synthetic 'product photo' for end-to-end testing.
Created 18 Nov 2026. Draws a blue mug on a beige background with Pillow —
no real product photos are used anywhere in this project.
Usage: python tests/make_test_image.py [output_path] [size]
"""
import sys
from PIL import Image, ImageDraw

out = sys.argv[1] if len(sys.argv) > 1 else "test-evidence/input_mug_beige.jpg"
size = int(sys.argv[2]) if len(sys.argv) > 2 else 900

img = Image.new("RGB", (size, size), (216, 199, 165))  # beige background
d = ImageDraw.Draw(img)
# table shadow
d.ellipse([size*0.28, size*0.80, size*0.74, size*0.88], fill=(190, 172, 138))
# mug body
d.rounded_rectangle([size*0.36, size*0.30, size*0.62, size*0.82],
                    radius=int(size*0.04), fill=(47, 127, 196))
# mug handle
d.arc([size*0.58, size*0.40, size*0.76, size*0.66], start=-80, end=85,
      fill=(47, 127, 196), width=int(size*0.035))
# highlight
d.rounded_rectangle([size*0.40, size*0.36, size*0.46, size*0.72],
                    radius=int(size*0.03), fill=(110, 175, 230))
# coffee surface
d.ellipse([size*0.36, size*0.28, size*0.62, size*0.36], fill=(70, 45, 25))
img.save(out, quality=95)
print(f"wrote {out} ({size}x{size})")
