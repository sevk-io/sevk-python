from __future__ import annotations

from typing import Dict

MAX_MARKUP_DEPTH = 64
MAX_TAG_ITERATIONS = 200
MAX_RENDER_OUTPUT = 5_000_000
MAX_TAG_SCAN_WORK = 30_000_000
MAX_CODEBLOCK_LENGTH = 2500
MAX_TOTAL_CODEBLOCK_LENGTH = 2500

MARKUP_TAG_NAMES = frozenset(
    [
        "block",
        "section",
        "column",
        "row",
        "container",
        "heading",
        "paragraph",
        "text",
        "button",
        "link",
        "sevk-link",
        "list",
        "li",
        "codeblock",
    ]
)

TOO_COMPLEX = "Email markup is too complex to render"


class RenderBudget:
    def __init__(self) -> None:
        self.scan_work = 0
        self.highlighted = 0

    def charge_scan_work(self, work: int) -> None:
        self.scan_work += work
        if self.scan_work > MAX_TAG_SCAN_WORK:
            raise ValueError(TOO_COMPLEX)

    def admits(self, length: int) -> bool:
        return (
            length <= MAX_CODEBLOCK_LENGTH
            and self.highlighted + length <= MAX_TOTAL_CODEBLOCK_LENGTH
        )

    def charge(self, length: int) -> None:
        self.highlighted += length


def _is_tag_name_char(char: str) -> bool:
    return char.isascii() and (char.isalpha() or char == "-")


def assert_markup_depth(content: str) -> None:
    depths: Dict[str, int] = {}
    index = 0
    while True:
        open_index = content.find("<", index)
        if open_index == -1:
            break
        close_index = content.find(">", open_index + 1)
        if close_index == -1:
            break
        index = close_index + 1

        position = open_index + 1
        closing = content[position : position + 1] == "/"
        if closing:
            position += 1
        name_end = position
        while name_end < close_index and _is_tag_name_char(content[name_end]):
            name_end += 1
        name = content[position:name_end].lower()
        if name not in MARKUP_TAG_NAMES:
            continue

        if closing:
            if depths.get(name, 0) > 0:
                depths[name] -= 1
        elif content[close_index - 1] != "/":
            depths[name] = depths.get(name, 0) + 1
            if depths[name] > MAX_MARKUP_DEPTH:
                raise ValueError(
                    f"Email markup nesting exceeds the maximum depth of {MAX_MARKUP_DEPTH}"
                )
