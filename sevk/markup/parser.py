import re
from typing import Callable, Dict, List, Optional, Tuple

from .limits import MAX_RENDER_OUTPUT, MAX_TAG_ITERATIONS, RenderBudget

TagProcessor = Callable[[Dict[str, str], str], str]


def process_tag(
    content: str,
    tag_name: str,
    processor: TagProcessor,
    budget: Optional[RenderBudget] = None,
) -> str:
    budget = budget or RenderBudget()
    result = content
    open_pattern = re.compile(f"<{tag_name}([^>]*)>", re.IGNORECASE)
    close_pattern = re.compile(re.escape(f"</{tag_name}>"), re.IGNORECASE)
    nested_pattern = re.compile(re.escape(f"<{tag_name}"), re.IGNORECASE)

    for _ in range(MAX_TAG_ITERATIONS):
        budget.charge_scan_work(len(result))
        matches = list(open_pattern.finditer(result))
        if not matches:
            break

        replacements: List[Tuple[int, int, str]] = []
        for match in matches:
            start = match.start()
            if replacements and start < replacements[-1][1]:
                continue

            inner_start = match.end()
            close_match = close_pattern.search(result, inner_start)
            budget.charge_scan_work(
                (close_match.start() if close_match else len(result)) - inner_start
            )
            if close_match is None:
                continue

            inner = result[inner_start : close_match.start()]
            if nested_pattern.search(inner):
                continue

            replacements.append(
                (
                    start,
                    close_match.end(),
                    processor(parse_attributes(match.group(1)), inner),
                )
            )

        if not replacements:
            break

        rebuilt = []
        rebuilt_length = 0
        cursor = 0
        for start, end, replacement in replacements:
            rebuilt.append(result[cursor:start])
            rebuilt.append(replacement)
            rebuilt_length += start - cursor + len(replacement)
            cursor = end
            if rebuilt_length > MAX_RENDER_OUTPUT:
                raise ValueError(
                    f"Email markup expands beyond the maximum size of {MAX_RENDER_OUTPUT} bytes"
                )
        rebuilt.append(result[cursor:])
        updated = "".join(rebuilt)
        if updated == result:
            break
        result = updated

    return result


def parse_attributes(attrs: str) -> Dict[str, str]:
    parsed = {}
    for match in re.finditer(r'([\w-]+)=(?:"([^"]*)"|\'([^\']*)\')', attrs):
        parsed[match.group(1)] = (
            match.group(2) if match.group(2) is not None else match.group(3)
        )
    return parsed
