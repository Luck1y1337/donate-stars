"""
Generates a single dark, angular "gaming logo" style avatar (512x512 PNG)
for the bot: black background, electric-blue monogram, glitch accents.
Upload it to @BotFather:  /setuserpic

Usage:
    venv/Scripts/python.exe scripts/make_avatar.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE), "assets")
DISPLAY_FONT = r"C:\Windows\Fonts\impact.ttf"

SIZE = 512
BG_COLOR = (5, 6, 10)
BLUE = (36, 130, 255)
BLUE_BRIGHT = (90, 180, 255)
BLUE_DEEP = (10, 40, 110)


def add_corner_glow(image, center, radius, color, strength):
    """Добавляет мягкое неоновое свечение в указанной точке."""
    glow_layer = Image.new("L", (SIZE, SIZE), 0)
    draw = ImageDraw.Draw(glow_layer)
    draw.ellipse(
        [
            center[0] - radius,
            center[1] - radius,
            center[0] + radius,
            center[1] + radius,
        ],
        fill=strength,
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius // 2))

    color_layer = Image.new("RGB", (SIZE, SIZE), color)
    return Image.composite(color_layer, image, glow_layer)


def draw_glitch_shard(draw, points, color, width, glow_image=None):
    """Рисует тонкий угловатый контур-акцент («глитч» деталь)."""
    draw.line(points + [points[0]], fill=color, width=width, joint="curve")


def build_glitch_accents(image):
    """Добавляет несколько острых контурных акцентов по углам."""
    accents = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(accents)

    # Top-right shard cluster.
    draw_glitch_shard(
        draw,
        [(360, -10), (500, 40), (430, 150)],
        (150, 210, 255, 200),
        3,
    )
    draw_glitch_shard(
        draw,
        [(430, 10), (520, 60)],
        (90, 170, 255, 140),
        2,
    )

    # Bottom-left shard cluster.
    draw_glitch_shard(
        draw,
        [(150, 520), (20, 470), (85, 360)],
        (150, 210, 255, 200),
        3,
    )
    draw_glitch_shard(
        draw,
        [(80, 500), (-10, 450)],
        (90, 170, 255, 140),
        2,
    )

    glow = accents.filter(ImageFilter.GaussianBlur(3))
    combined = Image.alpha_composite(glow, accents)
    image_rgba = image.convert("RGBA")
    image_rgba.alpha_composite(combined)
    return image_rgba.convert("RGB")


def draw_monogram(image, text, angle_degrees):
    """Рисует угловатую неоновую монограмму с бевелем и свечением."""
    font = ImageFont.truetype(DISPLAY_FONT, 230)

    layer_size = (SIZE * 2, SIZE * 2)
    text_layer = Image.new("RGBA", layer_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    center = (layer_size[0] // 2, layer_size[1] // 2)

    # Dark bevel shadow, offset down-right.
    draw.text(
        (center[0] + 6, center[1] + 8),
        text,
        font=font,
        fill=BLUE_DEEP + (255,),
        anchor="mm",
    )
    # Bright highlight rim, offset up-left.
    draw.text(
        (center[0] - 3, center[1] - 3),
        text,
        font=font,
        fill=(210, 235, 255, 255),
        anchor="mm",
    )
    # Main fill on top.
    draw.text(
        (center[0], center[1]),
        text,
        font=font,
        fill=BLUE + (255,),
        anchor="mm",
    )

    rotated = text_layer.rotate(
        angle_degrees, resample=Image.BICUBIC, center=center
    )
    left = center[0] - SIZE // 2
    top = center[1] - SIZE // 2
    cropped = rotated.crop((left, top, left + SIZE, top + SIZE))

    # Neon glow behind the letters.
    alpha = cropped.split()[3]
    glow_alpha = alpha.filter(ImageFilter.GaussianBlur(14))
    glow_layer = Image.new("RGBA", (SIZE, SIZE), BLUE_BRIGHT + (0,))
    glow_layer.putalpha(glow_alpha.point(lambda a: int(a * 0.55)))

    base = image.convert("RGBA")
    base.alpha_composite(glow_layer)
    base.alpha_composite(cropped)
    return base.convert("RGB")


def build_avatar():
    """Собирает финальную тёмную неоновую аватарку."""
    image = Image.new("RGB", (SIZE, SIZE), BG_COLOR)
    image = add_corner_glow(image, (60, 40), 260, (14, 40, 90), 110)
    image = add_corner_glow(image, (452, 472), 260, (14, 40, 90), 110)
    image = build_glitch_accents(image)
    image = draw_monogram(image, "SL", angle_degrees=-8)
    return image


def main():
    avatar = build_avatar()
    out_path = os.path.join(OUT_DIR, "avatar.png")
    avatar.save(out_path, "PNG")
    print("saved", out_path)


if __name__ == "__main__":
    main()
