from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from .limits import TOO_COMPLEX
from .number import js_number

MAX_EACH_ITEMS = 1000
MAX_EACH_OUTPUT = 2_000_000
MAX_TEMPLATE_WORK = 20_000_000
MAX_IF_ITERATIONS = 2000
OUTPUT_EXCEEDED = "Email block exceeds the maximum template output size"

IF_PATTERN = re.compile(r"\{%#if\s+([^%]+)%\}((?:(?!\{%#if\s)[\s\S])*?)\{%/if%\}")
EACH_OPEN_PATTERN = re.compile(r"\{%#each\s+(\w+)(?:\s+as\s+(\w+))?%\}")
FALLBACK_PATTERN = re.compile(r"\{%(\w+)\s*\?\?([^%]+)%\}")
VALUE_PATTERN = re.compile(r"\{%(\w+)%\}")


def is_truthy(value: Any) -> bool:
    if value is None or value == "" or value is False:
        return False
    if isinstance(value, (int, float)) and value == 0:
        return False
    return not isinstance(value, list) or bool(value)


def evaluate_condition(expression: str, config: Dict[str, Any]) -> bool:
    expression = expression.strip()
    if "||" in expression:
        return any(evaluate_condition(part, config) for part in expression.split("||"))
    if "&&" in expression:
        return all(evaluate_condition(part, config) for part in expression.split("&&"))

    match = re.match(r'^(\w+)\s*==\s*"([^"]*)"$', expression)
    if match:
        return _value_to_text(config.get(match.group(1))) == match.group(2)

    match = re.match(r'^(\w+)\s*!=\s*"([^"]*)"$', expression)
    if match:
        return _value_to_text(config.get(match.group(1))) != match.group(2)

    return is_truthy(config.get(expression))


def _value_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return js_number(float(value))
    if isinstance(value, dict):
        return "[object Object]"
    if isinstance(value, list):
        return ",".join(
            "[object Object]" if isinstance(item, dict) else _value_to_text(item)
            for item in value
        )
    return str(value)


class _OutputMeter:
    def __init__(self) -> None:
        self.rendered = 0

    def charge(self, value: str) -> str:
        if self.rendered + len(value) > MAX_EACH_OUTPUT:
            raise ValueError(OUTPUT_EXCEEDED)
        self.rendered += len(value)
        return value


def render_template(template: str, config: Dict[str, Any]) -> str:
    meter = _OutputMeter()
    result = _render_conditionals(template, config)
    result = _render_loops(result, config, meter)

    def replace_fallback(match: re.Match[str]) -> str:
        value = config.get(match.group(1))
        if value is not None and value != "":
            return meter.charge(_value_to_text(value))
        return meter.charge(match.group(2).strip())

    result = FALLBACK_PATTERN.sub(replace_fallback, result)
    return VALUE_PATTERN.sub(
        lambda match: meter.charge(_value_to_text(config.get(match.group(1)))), result
    )


def _render_conditionals(template: str, config: Dict[str, Any]) -> str:
    result = template
    work = 0

    def replace_if(match: re.Match[str]) -> str:
        body = match.group(2)
        else_index = body.find("{%else%}")
        true_branch = body[:else_index] if else_index >= 0 else body
        false_branch = body[else_index + 8 :] if else_index >= 0 else ""
        return (
            true_branch if evaluate_condition(match.group(1), config) else false_branch
        )

    for _ in range(MAX_IF_ITERATIONS):
        work += len(result)
        if work > MAX_TEMPLATE_WORK:
            raise ValueError(TOO_COMPLEX)
        replaced = IF_PATTERN.sub(replace_if, result, count=1)
        if replaced == result:
            break
        result = replaced

    return result


def _render_loops(template: str, config: Dict[str, Any], meter: _OutputMeter) -> str:
    if "{%/each%}" not in template:
        return template

    output: List[str] = []
    position = 0
    work = 0

    while position <= len(template):
        opening = EACH_OPEN_PATTERN.search(template, position)
        if opening is None:
            output.append(template[position:])
            break

        body_start = opening.end()
        close_index = template.find("{%/each%}", body_start)
        if close_index == -1:
            output.append(template[position:])
            break

        output.append(template[position : opening.start()])
        items = config.get(opening.group(1))

        if isinstance(items, list) and items:
            if len(items) > MAX_EACH_ITEMS:
                raise ValueError(
                    f"Email block exceeds the maximum of {MAX_EACH_ITEMS} loop items"
                )

            alias = opening.group(2) or "this"
            property_pattern = re.compile(r"\{%" + re.escape(alias) + r"\.(\w+)%\}")
            body = template[body_start:close_index]

            for item in items:
                work += len(body) + 16
                if work > MAX_TEMPLATE_WORK:
                    raise ValueError(TOO_COMPLEX)

                rendered = _render_item(body, item, config, property_pattern, meter)
                output.append(rendered)
                meter.rendered += len(rendered)
                if meter.rendered > MAX_EACH_OUTPUT:
                    raise ValueError(OUTPUT_EXCEEDED)

        position = close_index + len("{%/each%}")

    return "".join(output)


def _item_property(item: Any, name: str) -> Any:
    if isinstance(item, dict):
        return item.get(name)
    if name != "length":
        return None
    if isinstance(item, str):
        return len(item.encode("utf-16-le")) // 2
    if isinstance(item, list):
        return len(item)
    return None


def _render_item(
    body: str,
    item: Any,
    config: Dict[str, Any],
    property_pattern: re.Pattern[str],
    meter: _OutputMeter,
) -> str:
    item_out = 0

    def charge(value: str) -> str:
        nonlocal item_out
        if meter.rendered + item_out + len(value) > MAX_EACH_OUTPUT:
            raise ValueError(OUTPUT_EXCEEDED)
        item_out += len(value)
        return value

    rendered = property_pattern.sub(
        lambda match: charge(_value_to_text(_item_property(item, match.group(1)))), body
    )
    return VALUE_PATTERN.sub(
        lambda match: charge(_value_to_text(config.get(match.group(1)))), rendered
    )


def process_block(attrs: Dict[str, str], inner: str) -> str:
    template = inner.strip() or attrs.get("template", "")
    if not template:
        return ""

    serialized_config = re.sub(
        r"&(?:amp|quot|apos|lt|gt|#39|#x27|#34|#x22);",
        lambda match: {
            "&amp;": "&",
            "&quot;": '"',
            "&#34;": '"',
            "&#x22;": '"',
            "&apos;": "'",
            "&#39;": "'",
            "&#x27;": "'",
            "&lt;": "<",
            "&gt;": ">",
        }[match.group(0).lower()],
        attrs.get("config", "{}"),
        flags=re.IGNORECASE,
    )
    try:
        config = json.loads(serialized_config)
    except (TypeError, ValueError):
        try:
            config = json.loads(serialized_config.replace("'", '"'))
        except (TypeError, ValueError):
            config = {}
    return render_template(template, config if isinstance(config, dict) else {})
