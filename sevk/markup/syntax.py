from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from .limits import RenderBudget
from .styles import extract_style_attributes, style_to_string

TOKEN_SPACE = "\u00a0\u200d\u200b"

LANGUAGES = frozenset(
    [
        "plain",
        "extend",
        "plaintext",
        "text",
        "txt",
        "markup",
        "html",
        "mathml",
        "svg",
        "xml",
        "ssml",
        "atom",
        "rss",
        "css",
        "clike",
        "javascript",
        "js",
        "typescript",
        "ts",
        "jsx",
        "tsx",
        "python",
        "py",
        "java",
        "c",
        "cpp",
        "csharp",
        "cs",
        "dotnet",
        "php",
        "ruby",
        "rb",
        "go",
        "rust",
        "sql",
        "bash",
        "sh",
        "shell",
        "json",
        "webmanifest",
        "yaml",
        "yml",
        "markdown",
        "md",
    ]
)

LANGUAGE_ALIASES = {"jsx": "javascript", "tsx": "typescript"}

PYGMENTS_LEXERS: Dict[str, Optional[str]] = {
    "markup": "html",
    "mathml": "xml",
    "svg": "xml",
    "ssml": "xml",
    "atom": "xml",
    "rss": "xml",
    "dotnet": "csharp",
    "webmanifest": "json",
    "shell": "bash",
    "plain": None,
    "plaintext": None,
    "text": None,
    "txt": None,
    "clike": None,
}

THEME_BASES: Dict[str, List[Tuple[str, str]]] = {
    "vscDarkPlus": [
        ("color", "#d4d4d4"),
        ("fontSize", "13px"),
        ("textShadow", "none"),
        (
            "fontFamily",
            "Menlo, Monaco, Consolas, 'Andale Mono', 'Ubuntu Mono', 'Courier New', monospace",
        ),
        ("direction", "ltr"),
        ("textAlign", "left"),
        ("whiteSpace", "pre"),
        ("wordSpacing", "normal"),
        ("wordBreak", "normal"),
        ("lineHeight", "1.5"),
        ("MozTabSize", "4"),
        ("OTabSize", "4"),
        ("tabSize", "4"),
        ("WebkitHyphens", "none"),
        ("MozHyphens", "none"),
        ("hyphens", "none"),
        ("padding", "16px"),
        ("overflow", "auto"),
        ("backgroundColor", "#1e1e1e"),
    ],
    "vs": [
        ("color", "#393A34"),
        (
            "fontFamily",
            "'Consolas', 'Bitstream Vera Sans Mono', 'Courier New', Courier, monospace",
        ),
        ("direction", "ltr"),
        ("textAlign", "left"),
        ("whiteSpace", "pre"),
        ("wordSpacing", "normal"),
        ("wordBreak", "normal"),
        ("fontSize", ".9em"),
        ("lineHeight", "1.2em"),
        ("MozTabSize", "4"),
        ("OTabSize", "4"),
        ("tabSize", "4"),
        ("WebkitHyphens", "none"),
        ("MozHyphens", "none"),
        ("hyphens", "none"),
        ("padding", "16px"),
        ("overflow", "auto"),
        ("border", "1px solid #dddddd"),
        ("backgroundColor", "white"),
    ],
    "oneDark": [
        ("backgroundColor", "#282c34"),
        ("color", "#abb2bf"),
        ("textShadow", "0 1px rgba(0, 0, 0, 0.3)"),
        (
            "fontFamily",
            "'Fira Code', 'Fira Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace",
        ),
        ("direction", "ltr"),
        ("textAlign", "left"),
        ("whiteSpace", "pre"),
        ("wordSpacing", "normal"),
        ("wordBreak", "normal"),
        ("lineHeight", "1.5"),
        ("MozTabSize", "2"),
        ("OTabSize", "2"),
        ("tabSize", "2"),
        ("WebkitHyphens", "none"),
        ("MozHyphens", "none"),
        ("hyphens", "none"),
        ("padding", "16px"),
        ("overflow", "auto"),
        ("borderRadius", "6px"),
    ],
    "oneLight": [
        ("backgroundColor", "#fafafa"),
        ("color", "#383a42"),
        (
            "fontFamily",
            "'Fira Code', 'Fira Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace",
        ),
        ("direction", "ltr"),
        ("textAlign", "left"),
        ("whiteSpace", "pre"),
        ("wordSpacing", "normal"),
        ("wordBreak", "normal"),
        ("lineHeight", "1.5"),
        ("MozTabSize", "2"),
        ("OTabSize", "2"),
        ("tabSize", "2"),
        ("WebkitHyphens", "none"),
        ("MozHyphens", "none"),
        ("hyphens", "none"),
        ("padding", "16px"),
        ("overflow", "auto"),
        ("borderRadius", "6px"),
    ],
}

THEME_TOKENS: Dict[str, Dict[str, Dict[str, str]]] = {
    "vscDarkPlus": {
        "comment": {"color": "#6a9955"},
        "prolog": {"color": "#6a9955"},
        "punctuation": {"color": "#d4d4d4"},
        "property": {"color": "#9cdcfe"},
        "tag": {"color": "#569cd6"},
        "boolean": {"color": "#569cd6"},
        "number": {"color": "#b5cea8"},
        "constant": {"color": "#9cdcfe"},
        "symbol": {"color": "#b5cea8"},
        "inserted": {"color": "#b5cea8"},
        "selector": {"color": "#d7ba7d"},
        "attr-name": {"color": "#9cdcfe"},
        "string": {"color": "#ce9178"},
        "builtin": {"color": "#ce9178"},
        "deleted": {"color": "#ce9178"},
        "operator": {"color": "#d4d4d4"},
        "entity": {"color": "#569cd6"},
        "atrule": {"color": "#ce9178"},
        "keyword": {"color": "#569CD6"},
        "function": {"color": "#dcdcaa"},
        "regex": {"color": "#d16969"},
        "important": {"color": "#569cd6"},
        "italic": {"font-style": "italic"},
        "class-name": {"color": "#4ec9b0"},
        "variable": {"color": "#9cdcfe"},
        "attr-value": {"color": "#ce9178"},
        "cdata": {"color": "#808080"},
        "namespace": {"color": "#4ec9b0"},
    },
    "vs": {
        "comment": {"color": "#008000", "font-style": "italic"},
        "prolog": {"color": "#008000", "font-style": "italic"},
        "doctype": {"color": "#008000", "font-style": "italic"},
        "cdata": {"color": "#008000", "font-style": "italic"},
        "namespace": {"opacity": ".7"},
        "string": {"color": "#A31515"},
        "punctuation": {"color": "#393A34"},
        "operator": {"color": "#393A34"},
        "url": {"color": "#36acaa"},
        "symbol": {"color": "#36acaa"},
        "number": {"color": "#36acaa"},
        "boolean": {"color": "#36acaa"},
        "variable": {"color": "#36acaa"},
        "constant": {"color": "#36acaa"},
        "inserted": {"color": "#36acaa"},
        "atrule": {"color": "#0000ff"},
        "keyword": {"color": "#0000ff"},
        "attr-value": {"color": "#0000ff"},
        "function": {"color": "#393A34"},
        "deleted": {"color": "#9a050f"},
        "selector": {"color": "#800000"},
        "important": {"color": "#e90", "font-weight": "bold"},
        "bold": {"font-weight": "bold"},
        "italic": {"font-style": "italic"},
        "class-name": {"color": "#2B91AF"},
        "tag": {"color": "#800000"},
        "attr-name": {"color": "#ff0000"},
        "property": {"color": "#ff0000"},
        "regex": {"color": "#ff0000"},
        "entity": {"color": "#ff0000"},
    },
    "oneDark": {
        "comment": {"color": "#5c6370", "font-style": "italic"},
        "prolog": {"color": "#5c6370"},
        "cdata": {"color": "#5c6370"},
        "doctype": {"color": "#abb2bf"},
        "punctuation": {"color": "#abb2bf"},
        "entity": {"color": "#abb2bf", "cursor": "help"},
        "attr-name": {"color": "#d19a66"},
        "class-name": {"color": "#d19a66"},
        "boolean": {"color": "#d19a66"},
        "constant": {"color": "#d19a66"},
        "number": {"color": "#d19a66"},
        "atrule": {"color": "#d19a66"},
        "keyword": {"color": "#c678dd"},
        "property": {"color": "#e06c75"},
        "tag": {"color": "#e06c75"},
        "symbol": {"color": "#e06c75"},
        "deleted": {"color": "#e06c75"},
        "important": {"color": "#e06c75"},
        "selector": {"color": "#98c379"},
        "string": {"color": "#98c379"},
        "builtin": {"color": "#98c379"},
        "inserted": {"color": "#98c379"},
        "regex": {"color": "#98c379"},
        "attr-value": {"color": "#98c379"},
        "variable": {"color": "#61afef"},
        "operator": {"color": "#61afef"},
        "function": {"color": "#61afef"},
        "url": {"color": "#56b6c2"},
        "bold": {"font-weight": "bold"},
        "italic": {"font-style": "italic"},
        "namespace": {"opacity": "0.8"},
    },
    "oneLight": {
        "comment": {"color": "#a0a1a7", "font-style": "italic"},
        "prolog": {"color": "#a0a1a7"},
        "cdata": {"color": "#a0a1a7"},
        "doctype": {"color": "#383a42"},
        "punctuation": {"color": "#383a42"},
        "entity": {"color": "#383a42", "cursor": "help"},
        "attr-name": {"color": "#b76b01"},
        "class-name": {"color": "#b76b01"},
        "boolean": {"color": "#b76b01"},
        "constant": {"color": "#b76b01"},
        "number": {"color": "#b76b01"},
        "atrule": {"color": "#b76b01"},
        "keyword": {"color": "#a626a4"},
        "property": {"color": "#e45649"},
        "tag": {"color": "#e45649"},
        "symbol": {"color": "#e45649"},
        "deleted": {"color": "#e45649"},
        "important": {"color": "#e45649"},
        "selector": {"color": "#50a14f"},
        "string": {"color": "#50a14f"},
        "builtin": {"color": "#50a14f"},
        "inserted": {"color": "#50a14f"},
        "regex": {"color": "#50a14f"},
        "attr-value": {"color": "#50a14f"},
        "variable": {"color": "#4078f2"},
        "operator": {"color": "#4078f2"},
        "function": {"color": "#4078f2"},
        "url": {"color": "#0184bc"},
        "bold": {"font-weight": "bold"},
        "italic": {"font-style": "italic"},
        "namespace": {"opacity": "0.8"},
    },
}

PYGMENTS_TOKENS = {
    "Token.Comment": "comment",
    "Token.Keyword": "keyword",
    "Token.Keyword.Constant": "boolean",
    "Token.Keyword.Type": "class-name",
    "Token.Literal.String": "string",
    "Token.Literal.String.Regex": "regex",
    "Token.Literal.String.Symbol": "symbol",
    "Token.Literal.Number": "number",
    "Token.Name.Function": "function",
    "Token.Name.Class": "class-name",
    "Token.Name.Constant": "constant",
    "Token.Name.Builtin": "builtin",
    "Token.Name.Variable": "variable",
    "Token.Name.Tag": "tag",
    "Token.Name.Attribute": "attr-name",
    "Token.Name.Decorator": "function",
    "Token.Name.Namespace": "namespace",
    "Token.Name.Entity": "entity",
    "Token.Name.Label": "symbol",
    "Token.Name.Property": "property",
    "Token.Operator": "operator",
    "Token.Operator.Word": "keyword",
    "Token.Punctuation": "punctuation",
    "Token.Generic.Deleted": "deleted",
    "Token.Generic.Inserted": "inserted",
    "Token.Generic.Emph": "italic",
    "Token.Generic.Strong": "bold",
    "Token.Generic.Heading": "important",
    "Token.Generic.Subheading": "important",
}


def process_codeblock(attrs: Dict[str, str], code: str, budget: RenderBudget) -> str:
    requested = (attrs.get("language") or "javascript").lower()
    language = LANGUAGE_ALIASES.get(requested, requested)
    theme = attrs.get("theme") or "oneDark"
    theme = theme if theme in THEME_BASES else "oneDark"
    custom_style = list(extract_style_attributes(attrs).items())

    if not code:
        return "<pre><code></code></pre>"

    length = len(code) + sum(1 for char in code if ord(char) > 0xFFFF)
    if language not in LANGUAGES or not budget.admits(length):
        style = _pre_style(THEME_BASES[theme], [("width", "100%")], custom_style)
        escaped = code.replace("<", "&lt;").replace(">", "&gt;")
        return f'<pre style="{style}"><code>{escaped}</code></pre>'
    budget.charge(length)

    font_family = attrs.get("font-family") or ""
    inherited = {"font-family": font_family} if font_family else {}
    numbered = attrs.get("line-numbers") == "true"
    html = []
    for index, line in enumerate(_highlight_lines(code, language, theme, inherited)):
        number = (
            f'<span style="width:2em;display:inline-block">{index + 1}</span>'
            if numbered
            else ""
        )
        html.append(f'<p style="margin:0;min-height:1em">{number}{line}</p>')

    style = _pre_style(
        THEME_BASES[theme],
        [("width", "100%"), ("box-sizing", "border-box")],
        custom_style,
    )
    return f'<pre style="{style}"><code>{"".join(html)}</code></pre>'


def _pre_style(*layers: Iterable[Tuple[str, str]]) -> str:
    style: Dict[str, str] = {}
    for layer in layers:
        for key, value in layer:
            style[key] = value
    return ";".join(f"{_kebab_property(key)}:{value}" for key, value in style.items())


def _kebab_property(key: str) -> str:
    prop = re.sub(r"[A-Z]", lambda match: "-" + match.group(0).lower(), key)
    return "-" + prop if prop.startswith("ms-") else prop


def _highlight_lines(
    code: str, language: str, theme: str, inherited: Dict[str, str]
) -> List[str]:
    inherited_style = style_to_string(inherited)
    lexer = _lexer(language)
    tokens: List[Tuple[str, str]] = [(inherited_style, code)]
    if lexer is not None:
        tokens = [
            (_token_style(theme, token_type, inherited), text)
            for _, token_type, text in lexer.get_tokens_unprocessed(code)
        ]

    lines = [""]
    for style, text in tokens:
        for index, part in enumerate(text.split("\n")):
            if index > 0:
                lines.append("")
            if not part:
                continue
            escaped = (
                part.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;")
                .replace(" ", TOKEN_SPACE)
            )
            lines[-1] += f'<span style="{style}">{escaped}</span>' if style else escaped
    return lines


def _lexer(language: str) -> Optional[Lexer]:
    name = PYGMENTS_LEXERS.get(language, language)
    if name is None:
        return None
    try:
        return get_lexer_by_name(name)
    except ClassNotFound:
        return None


def _token_style(theme: str, token_type: Any, inherited: Dict[str, str]) -> str:
    current: Any = token_type
    while current is not None:
        token = PYGMENTS_TOKENS.get(str(current))
        if token is not None:
            return style_to_string({**inherited, **THEME_TOKENS[theme].get(token, {})})
        current = current.parent
    return style_to_string(inherited)
