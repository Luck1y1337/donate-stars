"""
Generates square avatar options (512x512 PNG) for the bot.
Upload the one you like to @BotFather:  /setuserpic

Usage:
    venv/Scripts/python.exe scripts/make_avatar.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE), "assets")
EMOJI_FONT = r"C:\Windows\Fonts\seguiemj.ttf"

SIZE = 512


def vertical_gradient(top_color, bottom_color):
    """Создаёт вертикальный градиент SIZE x SIZE."""
    image = Image.new("RGB", (SIZE, SIZE), top_color)
    draw = ImageDraw.Draw(image)
    for y in range(SIZE):
        factor = y / (SIZE - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * factor)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * factor)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * factor)
        draw.line([(0, y), (SIZE, y)], fill=(r, g, b))
    return image


def draw_emoji(image, emoji, size, center_x, center_y):
    """Рисует цветной эмодзи по центру указанной точки."""
    font = ImageFont.truetype(EMOJI_FONT, size)
    draw = ImageDraw.Draw(image)
    draw.text(
        (center_x, center_y),
        emoji,
        font=font,
        embedded_color=True,
        anchor="mm",
    )


def draw_caption(image, text, color):
    """Подписывает низ аватарки жирным текстом."""
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 54)
    except OSError:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)
    draw.text(
        (SIZE // 2, SIZE - 70),
        text,
        font=font,
        fill=color,
        anchor="mm",
    )


def build_clover():
    """Фиолетовый градиент + зелёный клевер (высокий контраст)."""
    image = vertical_gradient((139, 108, 255), (124, 77, 179))
    draw_emoji(image, "🍀", 300, SIZE // 2, SIZE // 2 - 10)
    return image


def build_star():
    """Фиолетовый градиент + звезда (перекликается с текущей аватаркой)."""
    image = vertical_gradient((139, 108, 255), (124, 77, 179))
    draw_emoji(image, "⭐", 300, SIZE // 2, SIZE // 2)
    return image


def build_clover_star():
    """Зелёный градиент + клевер и звёздочка-бейдж."""
    image = vertical_gradient((80, 200, 140), (20, 140, 120))
    draw_emoji(image, "🍀", 250, SIZE // 2 - 30, SIZE // 2 - 40)
    draw_emoji(image, "⭐", 150, SIZE // 2 + 120, SIZE // 2 + 110)
    return image


def build_monogram():
    """Фиолетовый градиент + монограмма SL и клевер."""
    image = vertical_gradient((150, 120, 255), (110, 90, 210))
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 210)
    except OSError:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)
    draw.text(
        (SIZE // 2, SIZE // 2 - 20),
        "SL",
        font=font,
        fill=(255, 255, 255),
        anchor="mm",
    )
    draw_emoji(image, "🍀", 120, SIZE // 2 + 130, SIZE // 2 + 140)
    return image


def main():
    variants = {
        "avatar-clover.png": build_clover(),
        "avatar-star.png": build_star(),
        "avatar-clover-star.png": build_clover_star(),
        "avatar-monogram.png": build_monogram(),
    }
    for name, image in variants.items():
        path = os.path.join(OUT_DIR, name)
        image.save(path, "PNG")
        print("saved", path)


if __name__ == "__main__":
    main()
