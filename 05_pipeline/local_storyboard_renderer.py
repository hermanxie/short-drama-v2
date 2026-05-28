from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fit_crop(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def pencil(image: Image.Image, contrast: float = 1.7) -> Image.Image:
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.invert(edges)
    edges = ImageEnhance.Contrast(edges).enhance(contrast)
    return ImageOps.grayscale(edges).convert("RGB")


def crop_character_sheet(image: Image.Image, name: str) -> Image.Image:
    w, h = image.size
    if name == "亚特":
        return image.crop((0, 0, int(w * 0.5), h))
    if name == "解伊":
        return image.crop((int(w * 0.38), 0, int(w * 0.7), h))
    return image


def find_manifest_item(manifest: dict, section: str, key: str) -> dict:
    values = manifest.get(section, {})
    if key in values:
        return values[key]
    for name, item in values.items():
        if key in name or name in key:
            return item
    raise KeyError(f"Cannot find {section} item: {key}")


def scene_key(location: str) -> str:
    if "大厅" in location:
        return "精绝宫殿大厅"
    if "连廊" in location or "走廊" in location:
        return "精绝宫殿连廊"
    if "空房" in location:
        return "精绝宫殿空房间"
    if "浴池" in location:
        return "精绝宫殿浴池"
    if "床榻" in location or "卧室" in location:
        return "精绝宫殿卧室"
    return "精绝宫殿寝宫"


def text_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def draw_arrow(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], color: tuple[int, int, int], width: int = 4) -> None:
    x1, y1, x2, y2 = xy
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    dx = 1 if x2 >= x1 else -1
    dy = 1 if y2 >= y1 else -1
    draw.line((x2, y2, x2 - 16 * dx, y2), fill=color, width=width)
    draw.line((x2, y2, x2, y2 - 16 * dy), fill=color, width=width)


def paste_character(panel: Image.Image, char_img: Image.Image, x: int, y: int, height: int) -> None:
    ratio = height / char_img.height
    resized = char_img.resize((max(1, int(char_img.width * ratio)), height), Image.Resampling.LANCZOS)
    panel.paste(resized, (x, y))


def render(args: argparse.Namespace) -> Path:
    manifest_path = args.manifest
    plan_path = args.plan
    manifest = load_json(manifest_path)
    plan = load_json(plan_path)
    block = next(item for item in plan["shot_blocks"] if item["block_id"] == args.block)

    asset_base = manifest_path.parent
    scene = find_manifest_item(manifest, "scenes", scene_key(block["scene_location"]))
    scene_img = Image.open(asset_base / scene["refs"][0])
    char_images = {}
    for name in block["characters"]:
        if name in ("亚特", "解伊"):
            item = find_manifest_item(manifest, "characters", name)
            char_images[name] = pencil(crop_character_sheet(Image.open(asset_base / item["refs"][0]), name), 1.35)

    board_w, board_h = 1024, 1536
    top_h, legend_h = 28, 92
    panel_w, panel_h = board_w // 2, (board_h - top_h - legend_h) // 3
    board = Image.new("RGB", (board_w, board_h), "white")
    draw = ImageDraw.Draw(board)
    font_num = text_font(34)
    font_small = text_font(15)
    font_legend = text_font(18)

    panels = block["panel_plan"]
    for idx, panel_data in enumerate(panels[:6]):
        col, row = idx % 2, idx // 2
        x0, y0 = col * panel_w, top_h + row * panel_h
        bg = pencil(fit_crop(scene_img, (panel_w, panel_h)), 1.15)
        bg = ImageEnhance.Brightness(bg).enhance(1.18)
        bg = ImageEnhance.Contrast(bg).enhance(0.82)
        board.paste(bg, (x0, y0))
        panel = board.crop((x0, y0, x0 + panel_w, y0 + panel_h))

        if "亚特" in char_images:
            if idx in (0, 4, 5):
                paste_character(panel, char_images["亚特"], 110 if idx != 5 else 55, 122, 300)
            else:
                paste_character(panel, char_images["亚特"], 90, 150, 250)
        if "解伊" in char_images:
            if idx in (0, 4):
                paste_character(panel, char_images["解伊"], 292, 150, 270)
            elif idx == 5:
                paste_character(panel, char_images["解伊"], 302, 150, 265)
            else:
                paste_character(panel, char_images["解伊"], 310, 160, 240)

        board.paste(panel, (x0, y0))
        d = ImageDraw.Draw(board)
        d.rectangle((x0, y0, x0 + panel_w - 1, y0 + panel_h - 1), outline=(40, 40, 40), width=2)
        d.text((x0 + 12, y0 + 8), str(idx + 1), fill=(0, 0, 0), font=font_num)
        cam = panel_data["camera_design"][:44]
        d.text((x0 + 58, y0 + 16), cam, fill=(0, 0, 0), font=font_small)
        d.rectangle((x0 + 20, y0 + 55, x0 + panel_w - 24, y0 + panel_h - 28), outline=(60, 150, 80), width=2)
        draw_arrow(d, (x0 + 76, y0 + panel_h - 90, x0 + 190, y0 + panel_h - 138), (210, 40, 40), 5)
        draw_arrow(d, (x0 + 285, y0 + 78, x0 + 405, y0 + 92), (40, 90, 210), 4)
        d.line((x0 + panel_w - 58, y0 + 54, x0 + panel_w - 26, y0 + 25), fill=(230, 120, 40), width=4)
        d.arc((x0 + 32, y0 + panel_h - 86, x0 + 110, y0 + panel_h - 18), 185, 275, fill=(230, 190, 30), width=4)

    draw.text((16, 2), f"{plan['episode_id']} {args.block} local reference storyboard", fill=(0, 0, 0), font=font_small)
    legend_y = board_h - legend_h + 10
    draw.text(
        (28, legend_y),
        "RED = BODY MOVEMENT | BLUE = CAMERA MOVEMENT | GREEN = FRAMING / COMPOSITION",
        fill=(20, 20, 20),
        font=font_legend,
    )
    draw.text(
        (28, legend_y + 32),
        "ORANGE = LIGHTING DIRECTION | YELLOW = ELEMENTAL VFX / ENERGY",
        fill=(20, 20, 20),
        font=font_legend,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    board.save(args.out)
    return args.out


def main() -> None:
    parser = argparse.ArgumentParser(description="Render local no-API storyboard grids from local references.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--block", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    print(render(args))


if __name__ == "__main__":
    main()
