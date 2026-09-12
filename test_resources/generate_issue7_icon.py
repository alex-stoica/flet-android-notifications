"""Render the demo's reference-inspired speech-bubble symbol (Pillow required).

Run: uv run --no-sync --with pillow python test_resources/generate_issue7_icon.py
This is a demo approximation, not an extracted or official Bot Commander asset.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main():
    root = Path(__file__).resolve().parents[1]
    image = Image.new("RGBA", (512, 512))
    draw = ImageDraw.Draw(image)
    ink = "#232F35"
    draw.rounded_rectangle((0, 0, 511, 511), radius=160, fill=ink)
    draw.rounded_rectangle((96, 108, 416, 365), radius=30, fill="white")
    draw.polygon([(96, 333), (174, 353), (96, 425)], fill="white")
    # Use the bundled Pillow font; no platform-specific font dependency.
    font = ImageFont.load_default(size=112)
    draw.text((256, 245), ":Bot", font=font, anchor="mm", fill=ink, stroke_width=2)
    image.resize((256, 256), Image.Resampling.LANCZOS).save(
        root / "test_resources" / "ic_issue7_bot.png"
    )
    # Android adaptive icons crop their outer region. Keep the symbol in its
    # safe zone; this asset affects only the demo app, never the library.
    assets = root / "assets"
    assets.mkdir(exist_ok=True)
    launcher = Image.new("RGBA", (1024, 1024), ink)
    launcher.alpha_composite(image, (256, 256))
    launcher.save(assets / "icon_android.png")


if __name__ == "__main__":
    main()
