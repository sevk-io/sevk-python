import math
import re
from typing import Dict, Tuple

STYLE_ORDER = (
    "color",
    "background-color",
    "background-image",
    "background-size",
    "background-position",
    "background-repeat",
    "font-size",
    "font-family",
    "font-weight",
    "line-height",
    "text-align",
    "text-decoration",
    "width",
    "height",
    "max-width",
    "max-height",
    "min-width",
    "min-height",
    "padding",
    "padding-top",
    "padding-right",
    "padding-bottom",
    "padding-left",
    "margin",
    "margin-top",
    "margin-right",
    "margin-bottom",
    "margin-left",
    "border",
    "border-color",
    "border-width",
    "border-style",
    "border-top",
    "border-right",
    "border-bottom",
    "border-left",
    "border-radius",
    "border-top-left-radius",
    "border-top-right-radius",
    "border-bottom-left-radius",
    "border-bottom-right-radius",
    "border-collapse",
    "list-style-type",
    "vertical-align",
)


def extract_style_attributes(attrs: Dict[str, str]) -> Dict[str, str]:
    attrs = {key: value for key, value in attrs.items() if value}
    style = {}

    if "text-color" in attrs:
        style["color"] = attrs["text-color"]
    elif "color" in attrs:
        style["color"] = attrs["color"]
    if "background-color" in attrs:
        style["background-color"] = attrs["background-color"]

    background_image = attrs.get("background-image")
    if background_image:
        style["background-image"] = f"url('{background_image}')"
    if "background-size" in attrs:
        style["background-size"] = attrs["background-size"]
    elif background_image:
        style["background-size"] = "cover"
    if "background-position" in attrs:
        style["background-position"] = attrs["background-position"]
    elif background_image:
        style["background-position"] = "center"
    if "background-repeat" in attrs:
        style["background-repeat"] = attrs["background-repeat"]
    elif background_image:
        style["background-repeat"] = "no-repeat"

    direct_properties = (
        "font-size",
        "font-family",
        "font-weight",
        "line-height",
        "text-align",
        "text-decoration",
        "width",
        "height",
        "max-width",
        "max-height",
        "min-width",
        "min-height",
        "padding",
        "padding-top",
        "padding-right",
        "padding-bottom",
        "padding-left",
        "margin",
        "margin-top",
        "margin-right",
        "margin-bottom",
        "margin-left",
        "border",
        "border-color",
        "border-width",
        "border-style",
        "border-top",
        "border-right",
        "border-bottom",
        "border-left",
        "border-radius",
        "border-top-left-radius",
        "border-top-right-radius",
        "border-bottom-left-radius",
        "border-bottom-right-radius",
    )
    for key in direct_properties:
        if key in attrs:
            style[key] = attrs[key]

    return style


def style_to_string(style: Dict[str, str]) -> str:
    seen = set()
    parts = []
    for key in STYLE_ORDER:
        value = style.get(key)
        if value is not None and value != "":
            parts.append(f"{key}:{value}")
            seen.add(key)
    for key, value in style.items():
        if key not in seen and value is not None and value != "":
            parts.append(f"{key}:{value}")
    return ";".join(parts)


def parse_padding(style: Dict[str, str]) -> Tuple[int, int, int, int]:
    top = right = bottom = left = 0
    if "padding" in style:
        parts = style["padding"].split()
        if len(parts) == 1:
            top = right = bottom = left = parse_px(parts[0])
        elif len(parts) == 2:
            vertical = parse_px(parts[0])
            horizontal = parse_px(parts[1])
            top, right, bottom, left = (
                vertical,
                horizontal,
                vertical,
                horizontal,
            )
        elif len(parts) == 3:
            top = parse_px(parts[0])
            right = left = parse_px(parts[1])
            bottom = parse_px(parts[2])
        elif len(parts) == 4:
            top, right, bottom, left = (parse_px(part) for part in parts)

    if "padding-top" in style:
        top = parse_px(style["padding-top"])
    if "padding-right" in style:
        right = parse_px(style["padding-right"])
    if "padding-bottom" in style:
        bottom = parse_px(style["padding-bottom"])
    if "padding-left" in style:
        left = parse_px(style["padding-left"])
    return top, right, bottom, left


def parse_px(value: str) -> int:
    match = re.match(r"^\s*([+-]?[0-9]+)", value)
    return int(match.group(1)) if match else 0


def px_to_pt(px: int) -> int:
    return (px * 3 + 2) // 4


def compute_font_width(expected_width: int) -> Tuple[float, int]:
    if expected_width <= 0:
        return 0, 0

    space_count = min(1000, max(1, math.ceil(expected_width / 10)))
    return expected_width / space_count / 2.0, space_count
