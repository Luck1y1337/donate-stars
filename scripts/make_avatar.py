"""
Generates a single professional square avatar (512x512 PNG) for the bot.
Upload it to @BotFather:  /setuserpic

Usage:
    venv/Scripts/python.exe scripts/make_avatar.py
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE), "assets")
BOLD_FONT = r"C:\Windows\Fonts\segoeuib.ttf"

SIZE = 512

# Violet gradient close to Telegram's own default avatar palette.
TOP_LEFT_COLOR = (154, 122, 245)
BOTTOM_RIGHT_COLOR = (95, 74, 209)


def diagonal_gradient(top_left, bottom_right):
    """Строит плавный диагональный градиент SIZE x SIZE."""
    image = Image.new("RGB", (SIZE, SIZE))
    pixels = image.load()
    max_distance = (SIZE - 1) + (SIZE - 1)
    for y in range(SIZE):
        for x in range(SIZE):
            factor = (x + y) / max_distance
            r = int(top_left[0] + (bottom_right[0] - top_left[0]) * factor)
            g = int(top_left[1] + (bottom_right[1] - top_left[1]) * factor)
            b = int(top_left[2] + (bottom_right[2] - top_left[2]) * factor)
            pixels[x, y] = (r, g, b)
    return image


def add_soft_glow(image, center, radius, strength):
    """Добавляет мягкое свечение позади монограммы для эффекта глубины."""
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

    white_layer = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    return Image.composite(white_layer, image, glow_layer)


def draw_monogram(image, text):
    """Рисует монограмму с мягкой тенью для глубины."""
    font = ImageFont.truetype(BOLD_FONT, 220)
    draw = ImageDraw.Draw(image, "RGBA")

    center_x = SIZE // 2
    center_y = SIZE // 2 - 6

    # Soft drop shadow.
    shadow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_draw.text(
        (center_x, center_y + 10),
        text,
        font=font,
        fill=(30, 20, 70, 130),
        anchor="mm",
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(8))
    image.paste(shadow_layer, (0, 0), shadow_layer)

    draw.text(
        (center_x, center_y),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        anchor="mm",
    )


def add_bottom_vignette(image):
    """Слегка затемняет нижний край для ощущения глубины и премиальности."""
    overlay = Image.new("L", (SIZE, SIZE), 0)
    draw = ImageDraw.Draw(overlay)
    for y in range(SIZE):
        if y > SIZE * 0.6:
            factor = (y - SIZE * 0.6) / (SIZE * 0.4)
            alpha = int(60 * factor)
            draw.line([(0, y), (SIZE, y)], fill=alpha)
    black_layer = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
    return Image.composite(black_layer, image, overlay)


def build_avatar():
    """Собирает финальную профессиональную аватарку."""
    image = diagonal_gradient(TOP_LEFT_COLOR, BOTTOM_RIGHT_COLOR)
    image = add_soft_glow(image, (SIZE // 2, SIZE // 2 - 6), 190, 55)
    image = add_bottom_vignette(image)
    image = image.convert("RGBA")
    draw_monogram(image, "SL")
    return image.convert("RGB")


def main():
    old_variants = [
        "avatar-clover.png",
        "avatar-star.png",
        "avatar-clover-star.png",
        "avatar-monogram.png",
    ]
    for name in old_variants:
        path = os.path.join(OUT_DIR, name)
        if os.path.exists(path):
            os.remove(path)
            print("removed old variant:", path)

    avatar = build_avatar()
    out_path = os.path.join(OUT_DIR, "avatar.png")
    avatar.save(out_path, "PNG")
    print("saved", out_path)


if __name__ == "__main__":
    main()
