import re
from typing import Callable, List, Optional, Tuple

_HIDDEN_STYLE = re.compile(r"style=[\"'][^\"']*display:\s*none", re.IGNORECASE)
_DIV_OPEN = re.compile(r"<div", re.IGNORECASE)
_DIV_CLOSE = re.compile(r"</div>", re.IGNORECASE)


def replace_self_closing(
    source: str, tag: str, self_close_only: bool, processor: Callable[[str], str]
) -> str:
    open_pattern = re.compile(f"<{tag}", re.IGNORECASE)
    name_length = len(tag) + 1
    output: List[str] = []
    last_index = 0
    position = 0

    while True:
        opening = open_pattern.search(source, position)
        if opening is None:
            break
        closing_bracket = source.find(">", opening.start() + name_length)
        if closing_bracket == -1:
            break
        position = closing_bracket + 1
        if self_close_only and source[closing_bracket - 1] != "/":
            continue

        attributes_end = closing_bracket - 1 if self_close_only else closing_bracket
        output.append(source[last_index : opening.start()])
        output.append(processor(source[opening.start() + name_length : attributes_end]))
        last_index = closing_bracket + 1

    output.append(source[last_index:])
    return "".join(output)


def get_first_tag_content(source: str, tag: str) -> Optional[str]:
    opening = re.compile(f"<{tag}", re.IGNORECASE).search(source)
    if opening is None:
        return None
    closing_bracket = source.find(">", opening.start() + len(tag) + 1)
    if closing_bracket == -1:
        return None
    closing = re.compile(f"</{tag}>", re.IGNORECASE).search(source, closing_bracket + 1)
    if closing is None:
        return None
    return source[closing_bracket + 1 : closing.start()]


def get_all_tag_contents(source: str, tag: str) -> List[str]:
    open_pattern = re.compile(f"<{tag}", re.IGNORECASE)
    close_pattern = re.compile(f"</{tag}>", re.IGNORECASE)
    contents: List[str] = []
    position = 0

    while True:
        opening = open_pattern.search(source, position)
        if opening is None:
            break
        closing_bracket = source.find(">", opening.start() + len(tag) + 1)
        if closing_bracket == -1:
            break
        closing = close_pattern.search(source, closing_bracket + 1)
        if closing is None:
            break
        contents.append(source[closing_bracket + 1 : closing.start()])
        position = closing.end()

    return contents


def strip_tag_pairs(source: str, tag: str) -> str:
    open_pattern = re.compile(f"<{tag}", re.IGNORECASE)
    close_pattern = re.compile(f"</{tag}>", re.IGNORECASE)
    output: List[str] = []
    last_index = 0
    position = 0

    while True:
        opening = open_pattern.search(source, position)
        if opening is None:
            break
        closing_bracket = source.find(">", opening.start() + len(tag) + 1)
        if closing_bracket == -1:
            break
        closing = close_pattern.search(source, closing_bracket + 1)
        if closing is None:
            break
        output.append(source[last_index : opening.start()])
        last_index = closing.end()
        position = last_index

    output.append(source[last_index:])
    return "".join(output)


def get_tag_attributes(source: str, tag: str) -> List[str]:
    open_pattern = re.compile(f"<{tag}", re.IGNORECASE)
    attributes: List[str] = []
    position = 0

    while True:
        opening = open_pattern.search(source, position)
        if opening is None:
            break
        closing_bracket = source.find(">", opening.start() + len(tag) + 1)
        if closing_bracket == -1:
            break
        attributes.append(source[opening.start() + len(tag) + 1 : closing_bracket])
        position = closing_bracket + 1

    return attributes


def find_hidden_preview_div(html: str) -> Optional[Tuple[str, str]]:
    position = 0

    while True:
        opening = _DIV_OPEN.search(html, position)
        if opening is None:
            return None
        closing_bracket = html.find(">", opening.start() + 4)
        if closing_bracket == -1:
            return None
        if _HIDDEN_STYLE.search(html, opening.start(), closing_bracket + 1):
            closing = _DIV_CLOSE.search(html, closing_bracket + 1)
            if closing is None:
                return None
            return (
                html[closing_bracket + 1 : closing.start()],
                html[opening.start() : closing.end()],
            )
        position = closing_bracket + 1
