import re
from typing import Any, Dict, List, Optional

from .document import _render_document, parse_email_html
from .models import EmailHeadSettings, FontConfig, ParsedEmailContent
from .template import process_block, render_template


def _process_block_tag(attrs: Dict[str, str], inner: str) -> str:
    return process_block(attrs, inner)


def _render_template(template: str, config: Dict[str, Any]) -> str:
    return render_template(template, config)


def render(markup: str, head_settings: Optional[EmailHeadSettings] = None) -> str:
    """Convert Sevk markup into complete, email-compatible HTML."""
    return _render_document(markup, head_settings)


def extract_variables(markup: str) -> List[str]:
    """Return unique template variable names in first-seen order."""
    variables = []
    seen = set()
    for match in re.finditer(r"\{\{(.+?)\}\}", markup):
        name = match.group(1).strip().split("??")[0].strip()
        if name not in seen:
            seen.add(name)
            variables.append(name)
    return variables


class Renderer:
    """Object-oriented renderer entry point."""

    def render(self, markup: str) -> str:
        """Convert Sevk markup into complete, email-compatible HTML."""
        return render(markup)


__all__ = [
    "EmailHeadSettings",
    "FontConfig",
    "ParsedEmailContent",
    "Renderer",
    "extract_variables",
    "parse_email_html",
    "render",
]
