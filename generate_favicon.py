"""
Generate favicon.ico and logo PNG files from SVG
Requires: pip install cairosvg pillow
"""
import os
from pathlib import Path

try:
    import cairosvg
    from PIL import Image
    import io
except ImportError:
    print("\n⚠️  Required packages not installed!")
    print("\nPlease run:")
    print("  pip install cairosvg pillow")
    print("\nThen run this script again.")
    exit(1)

# Paths
PUBLIC_DIR = Path(__file__).parent / "frontend" / "public"
SVG_PATH = PUBLIC_DIR / "logo.svg"

def generate_png(svg_path, output_path, size):
    """Generate PNG from SVG at specified size"""
    png_data = cairosvg.svg2png(
        url=str(svg_path),
        output_width=size,
        output_height=size
    )
    
    img = Image.open(io.BytesIO(png_data))
    img.save(output_path, "PNG")
    print(f"✓ Generated: {output_path.name} ({size}x{size})")

def generate_ico(svg_path, output_path):
    """Generate multi-size ICO file"""
    sizes = [16, 32, 48, 64]
    images = []
    
    for size in sizes:
        png_data = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size,
            output_height=size
        )
        img = Image.open(io.BytesIO(png_data))
        images.append(img)
    
    # Save as ICO with multiple sizes
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    print(f"✓ Generated: {output_path.name} (16, 32, 48, 64)")

def main():
    print("\n🎨 Generating Favicon and Logo Files...\n")
    
    if not SVG_PATH.exists():
        print(f"❌ Error: {SVG_PATH} not found!")
        return
    
    try:
        # Generate PNG logos for PWA
        generate_png(SVG_PATH, PUBLIC_DIR / "logo192.png", 192)
        generate_png(SVG_PATH, PUBLIC_DIR / "logo512.png", 512)
        
        # Generate favicon.ico
        generate_ico(SVG_PATH, PUBLIC_DIR / "favicon.ico")
        
        print("\n✅ All files generated successfully!")
        print("\nGenerated files:")
        print("  • favicon.ico (16, 32, 48, 64)")
        print("  • logo192.png (for PWA)")
        print("  • logo512.png (for PWA)")
        print("  • logo.svg (modern browsers)")
        
        print("\n📝 Next steps:")
        print("  1. Restart your React dev server")
        print("  2. Hard refresh browser (Ctrl+Shift+R)")
        print("  3. Check browser tab - you should see the new icon!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have the required packages:")
        print("  pip install cairosvg pillow")

if __name__ == "__main__":
    main()
