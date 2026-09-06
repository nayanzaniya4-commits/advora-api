from pathlib import Path
import uuid

from PIL import Image, ImageDraw, ImageFont

from app.config import settings


def _font(size=72):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def create_template(image_path: str, headline: str, cta: str) -> str:
    src = Image.open(image_path).convert("RGB")
    w, h = 1080, 1920
    canvas = Image.new("RGB", (w, h), "black")
    src.thumbnail((900, 1250))
    x = (w - src.width) // 2
    y = 250
    canvas.paste(src, (x, y))
    draw = ImageDraw.Draw(canvas)
    draw.text((80, 90), headline[:42], font=_font(64), fill="white")
    draw.text((80, 1620), cta.upper(), font=_font(54), fill="white")
    out = Path(settings.DATA_DIR) / f"template_{uuid.uuid4().hex}.jpg"
    canvas.save(out, quality=95)
    return str(out)


def create_stickers(headline: str):
    out = []
    labels = ["PREMIUM", "NEW ARRIVAL", "LIMITED EDITION", "BEST SELLER", "SHOP NOW"]
    for label in labels:
        img = Image.new("RGBA", (900, 300), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((20, 20, 880, 280), radius=70, outline="white", width=8)
        d.text((450, 150), label, anchor="mm", font=_font(58), fill="white")
        p = Path(settings.DATA_DIR) / f"sticker_{uuid.uuid4().hex}.png"
        img.save(p)
        out.append(str(p))
    return out
