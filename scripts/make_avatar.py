"""
Generates a single dark, neon "gaming logo" style avatar (512x512 PNG)
for the bot: black-green background, glowing clover + Stars badge,
glitch accents. Upload it to @BotFather:  /setuserpic

Usage:
    venv/Scripts/python.exe scripts/make_avatar.py
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE), "assets")
EMOJI_FONT = r"C:\Windows\Fonts\seguiemj.ttf"

SIZE = 512
BG_COLOR = (4, 8, 6)
GREEN_GLOW = (12, 70, 40)
GREEN_BRIGHT = (60, 220, 130)
GOLD_GLOW = (120, 95, 10)


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


def draw_glitch_shard(draw, points, color, width):
    """Рисует тонкий угловатый контур-акцент («глитч» деталь)."""
    draw.line(points + [points[0]], fill=color, width=width, joint="curve")


def build_glitch_accents(image):
    """Добавляет несколько острых контурных акцентов по углам."""
    accents = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(accents)

    draw_glitch_shard(
        draw, [(360, -10), (500, 40), (430, 150)], (150, 255, 200, 190), 3
    )
    draw_glitch_shard(draw, [(430, 10), (520, 60)], (100, 230, 160, 140), 2)

    draw_glitch_shard(
        draw, [(150, 520), (20, 470), (85, 360)], (150, 255, 200, 190), 3
    )
    draw_glitch_shard(draw, [(80, 500), (-10, 450)], (100, 230, 160, 140), 2)

    glow = accents.filter(ImageFilter.GaussianBlur(3))
    combined = Image.alpha_composite(glow, accents)
    image_rgba = image.convert("RGBA")
    image_rgba.alpha_composite(combined)
    return image_rgba.convert("RGB")


def render_emoji_layer(emoji, font_size, center_x, center_y, angle_degrees):
    """Рендерит эмодзи на прозрачном слое с поворотом вокруг своего центра."""
    layer_size = (SIZE * 2, SIZE * 2)
    layer = Image.new("RGBA", layer_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font = ImageFont.truetype(EMOJI_FONT, font_size)
    origin = (layer_size[0] // 2, layer_size[1] // 2)
    draw.text(origin, emoji, font=font, embedded_color=True, anchor="mm")

    if angle_degrees != 0:
        layer = layer.rotate(angle_degrees, resample=Image.BICUBIC, center=origin)

    left = origin[0] - center_x
    top = origin[1] - center_y
    return layer.crop((left, top, left + SIZE, top + SIZE))


def add_glow_behind(base, layer, color, blur_radius, opacity):
    """Добавляет неоновое свечение позади непрозрачного слоя эмодзи."""
    alpha = layer.split()[3]
    glow_alpha = alpha.filter(ImageFilter.GaussianBlur(blur_radius))
    glow_layer = Image.new("RGBA", (SIZE, SIZE), color + (0,))
    glow_layer.putalpha(glow_alpha.point(lambda a: int(a * opacity)))

    result = base.convert("RGBA")
    result.alpha_composite(glow_layer)
    return result


def build_avatar():
    """Собирает финальную тёмную неоновую аватарку: клевер + звезда."""
    image = Image.new("RGB", (SIZE, SIZE), BG_COLOR)
    image = add_corner_glow(image, (60, 40), 260, GREEN_GLOW, 110)
    image = add_corner_glow(image, (452, 472), 260, GREEN_GLOW, 110)
    image = build_glitch_accents(image)

    clover = render_emoji_layer(
        "🍀", 340, SIZE // 2 - 10, SIZE // 2 - 16, angle_degrees=-6
    )
    image_rgba = add_glow_behind(image, clover, GREEN_BRIGHT, 16, 0.6)
    image_rgba.alpha_composite(clover)

    star = render_emoji_layer(
        "⭐", 170, SIZE // 2 + 140, SIZE // 2 + 150, angle_degrees=10
    )
    image_rgba = add_glow_behind(image_rgba.convert("RGB"), star, (255, 200, 60), 14, 0.7)
    image_rgba.alpha_composite(star)

    return image_rgba.convert("RGB")


def main():
    avatar = build_avatar()
    out_path = os.path.join(OUT_DIR, "avatar.png")
    avatar.save(out_path, "PNG")
    print("saved", out_path)


if __name__ == "__main__":
    main()
