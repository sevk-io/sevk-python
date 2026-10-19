from __future__ import annotations

import math
import re
from typing import Dict, List, Tuple

from .limits import RenderBudget, assert_markup_depth
from .parser import parse_attributes, process_tag
from .styles import (
    compute_font_width,
    extract_style_attributes,
    parse_padding,
    parse_px,
    px_to_pt,
    style_to_string,
)
from .syntax import process_codeblock
from .tag_scan import replace_self_closing
from .template import process_block


def process_markup(content: str) -> Tuple[str, str]:
    assert_markup_depth(content)
    budget = RenderBudget()
    result = process_tag(content, "block", process_block, budget)

    result = replace_self_closing(
        result, "block", True, lambda attrs: process_block(parse_attributes(attrs), "")
    )
    assert_markup_depth(result)

    result = re.sub(
        r"<link(\s+(?:[\w-]+=(?:\"[^\"]*\"|'[^']*')\s+)*)href=",
        r"<sevk-link\1href=",
        result,
        flags=re.IGNORECASE,
    )
    result = re.sub(r"</link>", "</sevk-link>", result, flags=re.IGNORECASE)

    result = process_tag(result, "section", _process_section, budget)
    result = process_tag(result, "column", _process_column, budget)

    row_counter = [0]
    gap_styles: List[str] = []

    def process_row(attrs: Dict[str, str], inner: str) -> str:
        gap = attrs.get("gap", "0")
        style = extract_style_attributes(attrs)
        style.pop("gap", None)

        gap_px = gap.replace("px", "", 1)
        gap_num = parse_px(gap)
        row_id = f"sevk-row-{row_counter[0]}"
        row_counter[0] += 1

        column_count = len(re.findall(r'class="sevk-column"', inner))
        if column_count > 1:
            equal_width = f"{100 // column_count}%"

            def add_width(match: re.Match[str]) -> str:
                existing_style = match.group(1)
                if "width:" in existing_style:
                    return match.group(0)
                return (
                    f'<td class="sevk-column" '
                    f'style="width:{equal_width};{existing_style}"'
                )

            inner = re.sub(
                r'<td class="sevk-column" style="([^"]*)"',
                add_width,
                inner,
            )

        if gap_num > 0:
            spacer = (
                f'</td><td class="sevk-gap" '
                f'style="width:{gap_px}px;min-width:{gap_px}px" '
                f'width="{gap_px}"></td><td class="sevk-column"'
            )
            inner = re.sub(r'</td>\s*<td class="sevk-column"', spacer, inner)
            gap_styles.append(
                f".{row_id} .sevk-gap{{display:none !important;}}"
                f".{row_id} > tbody > tr > td.sevk-column"
                f"{{display:block !important;width:100% !important;"
                f"margin-bottom:{gap_px}px !important;}}"
                f".{row_id} > tbody > tr > td.sevk-column:last-of-type"
                "{margin-bottom:0 !important;}"
            )

        return f'''<table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" class="sevk-row-table {row_id}" style="{style_to_string(style)}">
<tbody style="width:100%">
<tr style="width:100%">{inner}</tr>
</tbody>
</table>'''

    result = process_tag(result, "row", process_row, budget)
    result = process_tag(result, "container", _process_container, budget)
    result = process_tag(result, "heading", _process_heading, budget)
    result = process_tag(result, "paragraph", _process_paragraph, budget)
    result = process_tag(
        result,
        "text",
        lambda attrs, inner: (
            f'<span style="{style_to_string(extract_style_attributes(attrs))}">'
            f"{inner}</span>"
        ),
        budget,
    )
    result = process_tag(result, "button", _process_button, budget)
    result = re.sub(r"<image([^>]*)/?>", _replace_image, result, flags=re.IGNORECASE)
    result = re.sub(
        r"<divider([^>]*)/?>", _replace_divider, result, flags=re.IGNORECASE
    )
    result = re.sub(r"</(?:divider|image)>", "", result, flags=re.IGNORECASE)
    result = process_tag(result, "sevk-link", _process_link, budget)
    result = process_tag(result, "list", _process_list, budget)
    result = process_tag(result, "li", _process_list_item, budget)
    result = process_tag(
        result,
        "codeblock",
        lambda attrs, inner: process_codeblock(attrs, inner, budget),
        budget,
    )

    result = re.sub(
        (
            r"</(?:container|section|row|column|heading|paragraph|text|"
            r"button|sevk-link)>"
        ),
        "",
        result,
        flags=re.IGNORECASE,
    )
    for pattern in (
        r"<sevk-email[^>]*>",
        r"</sevk-email>",
        r"<sevk-body[^>]*>",
        r"</sevk-body>",
        r"<email[^>]*>",
        r"</email>",
        r"<mail[^>]*>",
        r"</mail>",
        r"<body[^>]*>",
        r"</body>",
    ):
        result = re.sub(pattern, "", result, flags=re.IGNORECASE)

    responsive_styles = ""
    if gap_styles:
        responsive_styles = (
            "@media only screen and (max-width:479px){" + "".join(gap_styles) + "}"
        )
    return result.strip(), responsive_styles


def _process_section(attrs: Dict[str, str], inner: str) -> str:
    style = extract_style_attributes(attrs)
    cell_style: Dict[str, str] = {}
    if "padding" in style:
        cell_style["padding"] = style.pop("padding")
    if "text-align" in style:
        cell_style["text-align"] = style.pop("text-align")
    if any(
        key in style
        for key in (
            "border-radius",
            "border-top-left-radius",
            "border-top-right-radius",
            "border-bottom-left-radius",
            "border-bottom-right-radius",
        )
    ):
        style["border-collapse"] = "separate"
    return f'''<table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" style="{style_to_string(style)}">
<tbody>
<tr>
<td style="{style_to_string(cell_style)}">{inner}</td>
</tr>
</tbody>
</table>'''


def _process_column(attrs: Dict[str, str], inner: str) -> str:
    style = extract_style_attributes(attrs)
    style.setdefault("vertical-align", "top")
    return f'<td class="sevk-column" style="{style_to_string(style)}">{inner}</td>'


def _process_heading(attrs: Dict[str, str], inner: str) -> str:
    level = attrs.get("level") or "1"
    style = extract_style_attributes(attrs)
    style.setdefault("margin", "0")
    return f'<h{level} style="{style_to_string(style)}">{inner}</h{level}>'


def _process_paragraph(attrs: Dict[str, str], inner: str) -> str:
    style = extract_style_attributes(attrs)
    style.setdefault("margin", "0")
    return f'<p style="{style_to_string(style)}">{inner}</p>'


def _replace_image(match: re.Match[str]) -> str:
    attrs = parse_attributes(match.group(1) or "")
    style = extract_style_attributes(attrs)
    style.setdefault("vertical-align", "middle")
    style.setdefault("max-width", "100%")
    width = attrs.get("width", "").replace("px", "", 1)
    height = attrs.get("height", "").replace("px", "", 1)
    width_attr = f' width="{width}"' if width else ""
    height_attr = f' height="{height}"' if height else ""
    return (
        f'<img src="{attrs.get("src", "")}" alt="{attrs.get("alt", "")}"'
        f'{width_attr}{height_attr} style="{style_to_string(style)}" />'
    )


def _replace_divider(match: re.Match[str]) -> str:
    attrs = parse_attributes(match.group(1) or "")
    class_name = attrs.get("class") or attrs.get("className")
    class_attr = f' class="{class_name}"' if class_name else ""
    return (
        f'<hr style="{style_to_string(extract_style_attributes(attrs))}"{class_attr} />'
    )


def _process_link(attrs: Dict[str, str], inner: str) -> str:
    return (
        f'<a href="{attrs.get("href") or "#"}" '
        f'target="{attrs.get("target") or "_blank"}" '
        f'style="{style_to_string(extract_style_attributes(attrs))}">'
        f"{inner}</a>"
    )


def _process_list(attrs: Dict[str, str], inner: str) -> str:
    tag = "ol" if attrs.get("type", "unordered") == "ordered" else "ul"
    style = extract_style_attributes(attrs)
    style.setdefault("margin", "0")
    if "list-style-type" in attrs:
        style["list-style-type"] = attrs["list-style-type"]
    class_name = attrs.get("class") or attrs.get("className")
    class_attr = f' class="{class_name}"' if class_name else ""
    return f'<{tag} style="{style_to_string(style)}"{class_attr}>{inner}</{tag}>'


def _process_list_item(attrs: Dict[str, str], inner: str) -> str:
    class_name = attrs.get("class") or attrs.get("className")
    class_attr = f' class="{class_name}"' if class_name else ""
    return (
        f'<li style="{style_to_string(extract_style_attributes(attrs))}"'
        f"{class_attr}>{inner}</li>"
    )


def _process_container(attrs: Dict[str, str], inner: str) -> str:
    style = extract_style_attributes(attrs)
    cell_style: Dict[str, str] = {}
    table_style: Dict[str, str] = {}
    visual_keys = {
        "background-color",
        "background-image",
        "background-size",
        "background-position",
        "background-repeat",
        "border",
        "border-top",
        "border-right",
        "border-bottom",
        "border-left",
        "border-color",
        "border-width",
        "border-style",
        "border-radius",
        "border-top-left-radius",
        "border-top-right-radius",
        "border-bottom-left-radius",
        "border-bottom-right-radius",
        "padding",
        "padding-top",
        "padding-right",
        "padding-bottom",
        "padding-left",
    }
    for key, value in style.items():
        target = cell_style if key in visual_keys else table_style
        target[key] = value

    if any(
        cell_style.get(key)
        for key in (
            "border-radius",
            "border-top-left-radius",
            "border-top-right-radius",
            "border-bottom-left-radius",
            "border-bottom-right-radius",
        )
    ):
        table_style["border-collapse"] = "separate"

    width = table_style.get("width")
    if width and width not in ("100%", "auto"):
        table_style.setdefault("max-width", width)
        table_style["width"] = "100%"

    return f'''<table width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" style="{style_to_string(table_style)}">
<tbody>
<tr style="width:100%">
<td style="{style_to_string(cell_style)}">{inner}</td>
</tr>
</tbody>
</table>'''


def _process_button(attrs: Dict[str, str], inner: str) -> str:
    style = extract_style_attributes(attrs)
    top, right, bottom, left = parse_padding(style)
    left_width, left_spaces = compute_font_width(left)
    right_width, right_spaces = compute_font_width(right)

    button_style = {
        "line-height": "100%",
        "text-decoration": "none",
        "display": "inline-block",
        "max-width": "100%",
        "mso-padding-alt": "0px",
    }
    button_style.update(style)
    button_style.update(
        {
            "padding-top": f"{top}px",
            "padding-right": f"{right}px",
            "padding-bottom": f"{bottom}px",
            "padding-left": f"{left}px",
        }
    )

    left_padding = "&#8202;" * left_spaces
    right_padding = "&#8202;" * right_spaces
    return (
        f'<a href="{attrs.get("href") or "#"}" target="_blank" '
        f'style="{style_to_string(button_style)}">'
        f'<!--[if mso]><i style="mso-font-width:{math.floor(left_width * 100 + 0.5)}%;'
        f'mso-text-raise:{px_to_pt(top + bottom)}" hidden>{left_padding}</i>'
        f'<![endif]--><span style="max-width:100%;display:inline-block;'
        f"line-height:120%;mso-padding-alt:0px;"
        f'mso-text-raise:{px_to_pt(bottom)}">{inner}</span>'
        f'<!--[if mso]><i style="mso-font-width:{math.floor(right_width * 100 + 0.5)}%" '
        f"hidden>{right_padding}&#8203;</i><![endif]--></a>"
    )
