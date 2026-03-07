"""Generate favicon files from a source image.

Usage:
    uv run --with Pillow tool_scripts/gen_favicon/gen_favicon.py <input_image> [--output-dir static]

Generates:
    - favicon.ico (16/32/48px multi-size)
    - favicon-16x16.png
    - favicon-32x32.png
    - apple-touch-icon.png (180x180)
"""

import argparse
import os
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description="Generate favicon files from a source image")
    parser.add_argument("input", help="Path to source image")
    parser.add_argument("--output-dir", default="static", help="Output directory (default: static)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    img = Image.open(args.input)

    # favicon PNGs
    for size in [16, 32]:
        resized = img.resize((size, size), Image.LANCZOS)
        resized.save(os.path.join(args.output_dir, f"favicon-{size}x{size}.png"))
        print(f"  Created favicon-{size}x{size}.png")

    # apple-touch-icon
    resized = img.resize((180, 180), Image.LANCZOS)
    resized.save(os.path.join(args.output_dir, "apple-touch-icon.png"))
    print("  Created apple-touch-icon.png")

    # favicon.ico
    img.save(
        os.path.join(args.output_dir, "favicon.ico"),
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )
    print("  Created favicon.ico")


if __name__ == "__main__":
    main()
