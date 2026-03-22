"""
Sevk Markup Renderer
Converts Sevk markup to email-compatible HTML using regex-based parsing (like Node.js)
"""

import re
import html
import json
import math
from typing import Dict, List, Tuple, Optional, Callable, Any


class FontConfig:
    """Font configuration"""
    def __init__(self, id: str = "", name: str = "", url: str = ""):
        self.id = id
        self.name = name
        self.url = url


class EmailHeadSettings:
    """Head settings for email generation"""
    def __init__(self):
        self.title: str = ""
        self.preview_text: str = ""
        self.styles: str = ""
        self.fonts: List[FontConfig] = []
        self.lang: str = ""
        self.dir: str = ""


class ParsedEmailContent:
    """Parsed email content"""
    def __init__(self):
        self.body: str = ""
        self.head_settings: EmailHeadSettings = EmailHeadSettings()


def generate_email_from_markup(html_content: str, head_settings: Optional[EmailHeadSettings] = None) -> str:
    """Generate email HTML from Sevk markup"""
    # Always parse to extract clean body content (strips <mail>/<head> wrapper tags)
    parsed = parse_email_html(html_content)
    if head_settings is None:
        head_settings = parsed.head_settings
    content_to_process = parsed.body
    settings = head_settings

    normalized = _normalize_markup(content_to_process)
    body, gap_styles = _process_markup(normalized)

    # Build head content
    title_tag = f"<title>{settings.title}</title>" if settings.title else ""
    font_links = _generate_font_links(settings.fonts)
    gap_style_tag = f'<style type="text/css">{gap_styles}</style>' if gap_styles else ""
    custom_styles = f'<style type="text/css">{settings.styles}</style>' if settings.styles else ""
    preview_text = f'<div style="display:none;font-size:1px;color:#ffffff;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">{settings.preview_text}</div>' if settings.preview_text else ""

    lang = settings.lang or 'en'
    dir_attr = settings.dir or 'ltr'

    return f'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="{lang}" dir="{dir_attr}" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta content="text/html; charset=UTF-8" http-equiv="Content-Type"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="x-apple-disable-message-reformatting"/>
<meta content="IE=edge" http-equiv="X-UA-Compatible"/>
<meta name="format-detection" content="telephone=no,address=no,email=no,date=no,url=no"/>
<!--[if mso]>
<noscript>
<xml>
<o:OfficeDocumentSettings>
<o:AllowPNG/>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
<style type="text/css">
#outlook a {{ padding: 0; }}
body {{ margin: 0; padding: 0; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
table, td {{ border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
.sevk-row-table {{ border-collapse: separate !important; }}
img {{ border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; }}
@media only screen and (max-width: 479px) {{
  .sevk-row-table {{ width: 100% !important; }}
  .sevk-column {{ display: block !important; width: 100% !important; max-width: 100% !important; box-sizing: border-box !important; }}
}}
</style>
{gap_style_tag}
{title_tag}
{font_links}
{custom_styles}
</head>
<body style="margin:0;padding:0;word-spacing:normal;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;font-family:ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif">
<div aria-roledescription="email" role="article">
{preview_text}
{body}
</div>
</body>
</html>'''


def _normalize_markup(content: str) -> str:
    """Normalize markup by wrapping if needed"""
    result = content

    # Replace <link> with <sevk-link>
    if '<link' in result:
        result = re.sub(r'<link\s+href=', '<sevk-link href=', result, flags=re.IGNORECASE)
        result = result.replace('</link>', '</sevk-link>')

    if '<sevk-email' not in result and '<email' not in result and '<mail' not in result:
        result = f"<mail><body>{result}</body></mail>"

    return result


def _generate_font_links(fonts: List[FontConfig]) -> str:
    """Generate font link tags"""
    return '\n'.join([f'<link href="{f.url}" rel="stylesheet" type="text/css" />' for f in fonts])


def parse_email_html(content: str) -> ParsedEmailContent:
    """Parse email HTML and extract head settings"""
    if '<email>' in content or '<email ' in content or '<mail>' in content or '<mail ' in content:
        return _parse_sevk_markup(content)

    result = ParsedEmailContent()
    result.body = content
    return result


def _parse_sevk_markup(content: str) -> ParsedEmailContent:
    """Parse Sevk markup format"""
    head_settings = EmailHeadSettings()

    # Extract lang and dir from root <mail> or <email> tag
    root_match = re.search(r'<(?:email|mail)([^>]*)>', content, re.IGNORECASE)
    if root_match:
        root_attrs = root_match.group(1)
        lang_match = re.search(r'lang=["\']([^"\']*)["\']', root_attrs)
        if lang_match:
            head_settings.lang = lang_match.group(1)
        dir_match = re.search(r'dir=["\']([^"\']*)["\']', root_attrs)
        if dir_match:
            head_settings.dir = dir_match.group(1)

    # Extract title
    title_match = re.search(r'<title[^>]*>([\s\S]*?)</title>', content, re.IGNORECASE)
    if title_match:
        head_settings.title = title_match.group(1).strip()

    # Extract preview
    preview_match = re.search(r'<preview[^>]*>([\s\S]*?)</preview>', content, re.IGNORECASE)
    if preview_match:
        head_settings.preview_text = preview_match.group(1).strip()

    # Extract styles
    style_match = re.search(r'<style[^>]*>([\s\S]*?)</style>', content, re.IGNORECASE)
    if style_match:
        head_settings.styles = style_match.group(1).strip()

    # Extract fonts
    font_pattern = r'<font[^>]*name=["\']([^"\']*)["\'][^>]*url=["\']([^"\']*)["\'][^>]*/?\s*>'
    for i, match in enumerate(re.finditer(font_pattern, content, re.IGNORECASE)):
        head_settings.fonts.append(FontConfig(
            id=f"font-{i}",
            name=match.group(1),
            url=match.group(2)
        ))

    # Extract body
    body_match = re.search(r'<body[^>]*>([\s\S]*?)</body>', content, re.IGNORECASE)
    if body_match:
        body = body_match.group(1).strip()
    else:
        body = content
        patterns = [
            r'<email[^>]*>', r'</email>',
            r'<mail[^>]*>', r'</mail>',
            r'<head[^>]*>[\s\S]*?</head>',
            r'<title[^>]*>[\s\S]*?</title>',
            r'<preview[^>]*>[\s\S]*?</preview>',
            r'<style[^>]*>[\s\S]*?</style>',
            r'<font[^>]*>[\s\S]*?</font>',
            r'<font[^>]*/?>',
        ]
        for pattern in patterns:
            body = re.sub(pattern, '', body, flags=re.IGNORECASE)
        body = body.strip()

    result = ParsedEmailContent()
    result.body = body
    result.head_settings = head_settings
    return result


def _process_markup(content: str) -> Tuple[str, str]:
    """Process markup using regex-based parsing (like Node.js). Returns (html, gap_styles)."""
    result = content

    # Ensure <link> tags are converted to <sevk-link> for processing
    result = re.sub(r'<link\s+href=', '<sevk-link href=', result, flags=re.IGNORECASE)
    result = result.replace('</link>', '</sevk-link>')

    # Process block tags FIRST - expand blocks into sevk markup before other processing
    result = _process_tag(result, 'block', _process_block_tag)
    # Also handle self-closing <block ... /> tags
    def _replace_self_closing_block(match):
        attrs = _parse_attributes(match.group(1) or '')
        return _process_block_tag(attrs, '')
    result = re.sub(r'<block([^>]*)/\s*>', _replace_self_closing_block, result, flags=re.IGNORECASE)

    # Process section tags
    def _process_section(attrs, inner):
        style = _extract_all_style_attributes(attrs)
        td_style: Dict[str, str] = {}
        if 'padding' in style:
            td_style['padding'] = style.pop('padding')
        if 'text-align' in style:
            td_style['text-align'] = style.pop('text-align')
        return f'''<table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" style="{_style_to_string(style)}">
<tbody>
<tr>
<td style="{_style_to_string(td_style)}">{inner}</td>
</tr>
</tbody>
</table>'''
    result = _process_tag(result, 'section', _process_section)

    # Process column tags first (innermost), then row wraps them
    def _process_column(attrs, inner):
        style = _extract_all_style_attributes(attrs)
        if 'vertical-align' not in style:
            style['vertical-align'] = 'top'
        style_str = _style_to_string(style)
        return f'<td class="sevk-column" style="{style_str}">{inner}</td>'
    result = _process_tag(result, 'column', _process_column)

    # Process row tags
    row_counter = [0]
    gap_styles_arr = []
    def _process_row(attrs, inner):
        gap = attrs.get('gap', '0')
        style = _extract_all_style_attributes(attrs)
        if 'gap' in style:
            del style['gap']

        gap_px = gap.replace('px', '')
        gap_num = int(gap_px) if gap_px.isdigit() else 0
        row_id = f'sevk-row-{row_counter[0]}'
        row_counter[0] += 1

        # Assign equal widths to columns if more than one
        column_count = len(re.findall(r'class="sevk-column"', inner))
        if column_count > 1:
            equal_width = f'{100 // column_count}%'
            def _add_width(m):
                existing_style = m.group(1)
                if 'width:' in existing_style:
                    return m.group(0)
                return f'<td class="sevk-column" style="width:{equal_width};{existing_style}"'
            inner = re.sub(r'<td class="sevk-column" style="([^"]*)"', _add_width, inner)

        # Insert spacer <td> between each column for desktop gap
        processed_inner = inner
        if gap_num > 0:
            spacer_td = f'</td><td class="sevk-gap" style="width:{gap_px}px;min-width:{gap_px}px" width="{gap_px}"></td><td class="sevk-column"'
            processed_inner = re.sub(r'</td>\s*<td class="sevk-column"', spacer_td, processed_inner)

            # Collect mobile responsive styles
            gap_styles_arr.append(
                f'.{row_id} .sevk-gap{{display:none !important;}}'
                f'.{row_id} > tbody > tr > td.sevk-column{{display:block !important;width:100% !important;margin-bottom:{gap_px}px !important;}}'
                f'.{row_id} > tbody > tr > td.sevk-column:last-of-type{{margin-bottom:0 !important;}}'
            )

        style_str = _style_to_string(style)
        return f'''<table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" class="sevk-row-table {row_id}" style="{style_str}">
<tbody style="width:100%">
<tr style="width:100%">{processed_inner}</tr>
</tbody>
</table>'''
    result = _process_tag(result, 'row', _process_row)

    # Process container tags
    result = _process_tag(result, 'container', _process_container)

    # Process heading tags
    def process_heading(attrs: Dict[str, str], inner: str) -> str:
        level = attrs.get('level', '1')
        style = _extract_all_style_attributes(attrs)
        if 'margin' not in style:
            style['margin'] = '0'
        return f'<h{level} style="{_style_to_string(style)}">{inner}</h{level}>'
    result = _process_tag(result, 'heading', process_heading)

    # Process paragraph tags
    def process_paragraph(attrs: Dict[str, str], inner: str) -> str:
        style = _extract_all_style_attributes(attrs)
        if 'margin' not in style:
            style['margin'] = '0'
        return f'<p style="{_style_to_string(style)}">{inner}</p>'
    result = _process_tag(result, 'paragraph', process_paragraph)

    # Process text tags
    result = _process_tag(result, 'text', lambda attrs, inner:
        f'<span style="{_style_to_string(_extract_all_style_attributes(attrs))}">{inner}</span>')

    # Process button tags with MSO compatibility
    result = _process_tag(result, 'button', _process_button)

    # Process image tags
    def replace_image(match):
        attrs = _parse_attributes(match.group(1) or '')
        src = attrs.get('src', '')
        alt = attrs.get('alt', '')
        width = attrs.get('width')
        height = attrs.get('height')

        style = _extract_all_style_attributes(attrs)
        if 'vertical-align' not in style:
            style['vertical-align'] = 'middle'
        if 'max-width' not in style:
            style['max-width'] = '100%'
        if 'outline' not in style:
            style['outline'] = 'none'
        if 'border' not in style:
            style['border'] = 'none'
        if 'text-decoration' not in style:
            style['text-decoration'] = 'none'

        style_str = _style_to_string(style)
        width_attr = f' width="{width.replace("px", "")}"' if width else ''
        height_attr = f' height="{height.replace("px", "")}"' if height else ''

        return f'<img src="{src}" alt="{alt}"{width_attr}{height_attr} style="{style_str}" />'

    result = re.sub(r'<image([^>]*)/?>',  replace_image, result, flags=re.IGNORECASE)

    # Process divider tags
    def replace_divider(match):
        attrs = _parse_attributes(match.group(1) or '')
        style = _extract_all_style_attributes(attrs)
        style_str = _style_to_string(style)
        class_attr = attrs.get('class') or attrs.get('className')
        class_str = f' class="{class_attr}"' if class_attr else ''
        return f'<hr style="{style_str}"{class_str} />'

    result = re.sub(r'<divider([^>]*)/?>',  replace_divider, result, flags=re.IGNORECASE)
    # Remove any stray </divider> closing tags
    result = re.sub(r'</divider>', '', result, flags=re.IGNORECASE)

    # Process link tags
    def process_link(attrs: Dict[str, str], inner: str) -> str:
        href = attrs.get('href', '#')
        target = attrs.get('target', '_blank')
        style = _extract_all_style_attributes(attrs)
        return f'<a href="{href}" target="{target}" style="{_style_to_string(style)}">{inner}</a>'
    result = _process_tag(result, 'sevk-link', process_link)

    # Process list tags
    def process_list(attrs: Dict[str, str], inner: str) -> str:
        list_type = attrs.get('type', 'unordered')
        tag = 'ol' if list_type == 'ordered' else 'ul'
        style = _extract_all_style_attributes(attrs)
        if 'margin' not in style:
            style['margin'] = '0'
        if 'list-style-type' in attrs:
            style['list-style-type'] = attrs['list-style-type']
        style_str = _style_to_string(style)
        class_attr = attrs.get('class') or attrs.get('className')
        class_str = f' class="{class_attr}"' if class_attr else ''
        return f'<{tag} style="{style_str}"{class_str}>{inner}</{tag}>'
    result = _process_tag(result, 'list', process_list)

    # Process list item tags
    def process_li(attrs: Dict[str, str], inner: str) -> str:
        style = _extract_all_style_attributes(attrs)
        style_str = _style_to_string(style)
        class_attr = attrs.get('class') or attrs.get('className')
        class_str = f' class="{class_attr}"' if class_attr else ''
        return f'<li style="{style_str}"{class_str}>{inner}</li>'
    result = _process_tag(result, 'li', process_li)

    # Process codeblock tags with Pygments syntax highlighting
    result = _process_tag(result, 'codeblock', _process_codeblock)

    # Clean up stray Sevk closing tags that weren't consumed by processTag
    result = re.sub(r'</(?:container|section|row|column|heading|paragraph|text|button|sevk-link)>', '', result, flags=re.IGNORECASE)

    # Clean up wrapper tags
    wrapper_patterns = [
        r'<sevk-email[^>]*>', r'</sevk-email>',
        r'<sevk-body[^>]*>', r'</sevk-body>',
        r'<email[^>]*>', r'</email>',
        r'<mail[^>]*>', r'</mail>',
        r'<body[^>]*>', r'</body>',
    ]
    for pattern in wrapper_patterns:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)

    gap_styles = ''
    if gap_styles_arr:
        gap_styles = '@media only screen and (max-width:479px){' + ''.join(gap_styles_arr) + '}'

    return result.strip(), gap_styles


def _is_truthy(val: Any) -> bool:
    """Check if a value is truthy for template conditionals."""
    if val is None or val == '' or val is False or val == 0:
        return False
    if isinstance(val, list) and len(val) == 0:
        return False
    return True


def _evaluate_condition(expr: str, config: Dict[str, Any]) -> bool:
    trimmed = expr.strip()

    # OR: split on ||, return true if any part is true
    if '||' in trimmed:
        return any(_evaluate_condition(part, config) for part in trimmed.split('||'))

    # AND: split on &&, return true if all parts are true
    if '&&' in trimmed:
        return all(_evaluate_condition(part, config) for part in trimmed.split('&&'))

    # Equality: key == "value"
    eq_match = re.match(r'^(\w+)\s*==\s*"([^"]*)"$', trimmed)
    if eq_match:
        return str(config.get(eq_match.group(1), '')) == eq_match.group(2)

    # Inequality: key != "value"
    neq_match = re.match(r'^(\w+)\s*!=\s*"([^"]*)"$', trimmed)
    if neq_match:
        return str(config.get(neq_match.group(1), '')) != neq_match.group(2)

    # Simple truthy check
    return _is_truthy(config.get(trimmed))


def _render_template(template: str, config: Dict[str, Any]) -> str:
    """
    Render a block template with config values.

    Template syntax:
      {%variable%}                          - inject config value
      {%variable ?? fallback%}             - inject with fallback
      {%#each array as alias%}...{%/each%} - iterate arrays
      {%alias.key%}                        - access current item in loop
      {%#if key%}...{%/if%}               - conditional (truthy check)
      {%#if key%}...{%else%}...{%/if%}    - conditional with else
      {%#if a && b%}                       - logical AND
      {%#if a || b%}                       - logical OR
      {%#if key == "value"%}               - string equality
      {%#if key != "value"%}               - string inequality

    Double-brace {{...}} variables are preserved untouched.
    """
    result = template

    # 1. Process {%#if key%}...{%else%}...{%/if%} conditionals
    # Process innermost first (body must not contain another {%#if)
    prev = ''
    while prev != result:
        prev = result

        def _replace_if(m):
            condition = m.group(1)
            body = m.group(2)
            cond_result = _evaluate_condition(condition, config)
            else_idx = body.find('{%else%}')
            true_branch = body[:else_idx] if else_idx >= 0 else body
            false_branch = body[else_idx + 8:] if else_idx >= 0 else ''
            return true_branch if cond_result else false_branch

        result = re.sub(
            r'\{%#if\s+([^%]+)%\}((?:(?!\{%#if\s)[\s\S])*?)\{%/if%\}',
            _replace_if,
            result,
            count=1
        )

    # 2. Process {%#each key as alias%}...{%/each%} loops
    def _replace_each(m):
        key = m.group(1)
        alias = m.group(2) or 'this'
        body = m.group(3)
        arr = config.get(key)
        if not isinstance(arr, list) or len(arr) == 0:
            return ''
        parts = []
        for item in arr:
            item_result = body
            # Replace {%alias.prop%} with item values
            item_re = re.compile(r'\{%' + re.escape(alias) + r'\.(\w+)%\}')
            item_result = item_re.sub(
                lambda pm: str(item.get(pm.group(1), '') if isinstance(item, dict) else ''),
                item_result
            )
            # Replace {%variable%} with config values (parent scope)
            item_result = re.sub(
                r'\{%(\w+)%\}',
                lambda pm: str(config.get(pm.group(1), '') if config.get(pm.group(1)) is not None else ''),
                item_result
            )
            parts.append(item_result)
        return ''.join(parts)

    result = re.sub(
        r'\{%#each\s+(\w+)(?:\s+as\s+(\w+))?%\}([\s\S]*?)\{%/each%\}',
        _replace_each,
        result
    )

    # 3. Process {%variable ?? fallback%} with fallback
    def _replace_fallback(m):
        key = m.group(1)
        fallback = m.group(2).strip()
        val = config.get(key)
        if val is not None and val != '':
            return str(val)
        return fallback

    result = re.sub(
        r'\{%(\w+)\s*\?\?\s*([^%]+)%\}',
        _replace_fallback,
        result
    )

    # 4. Process {%variable%} simple injection
    result = re.sub(
        r'\{%(\w+)%\}',
        lambda m: str(config[m.group(1)]) if config.get(m.group(1)) is not None else '',
        result
    )

    return result


def _process_block_tag(attrs: Dict[str, str], inner: str) -> str:
    """
    Process a <block> tag using the template engine.
    Reads template from inner content or attrs, renders with config.
    Returns sevk markup for further processing.
    """
    template = inner.strip() if inner else ''
    if not template:
        template = attrs.get('template', '')
    if not template:
        return ''

    config_str = attrs.get('config', '{}').replace("'", '"').replace('&quot;', '"').replace('&amp;', '&')
    try:
        config = json.loads(config_str)
    except Exception:
        config = {}

    return _render_template(template, config)


# Theme-to-Pygments style mapping
_THEME_STYLE_MAP: Dict[str, str] = {
    'oneDark': 'monokai',
    'vscDarkPlus': 'monokai',
    'vs': 'friendly',
    'dracula': 'dracula',
    'nightOwl': 'monokai',
    'duotoneDark': 'monokai',
    'duotoneLight': 'friendly',
    'github': 'github-dark',
    'okaidia': 'monokai',
    'synthwave84': 'monokai',
    'shadesOfPurple': 'monokai',
    'coldarkDark': 'monokai',
    'coldarkCold': 'friendly',
    'coy': 'friendly',
    'materialDark': 'monokai',
    'materialLight': 'friendly',
    'materialOceanic': 'monokai',
}

# Default base styles matching the Node SDK's oneDark theme
_CODEBLOCK_BASE_STYLES: Dict[str, str] = {
    'background-color': '#282c34',
    'color': '#abb2bf',
    'font-family': "'Fira Code', 'Fira Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace",
    'font-size': '13px',
    'text-align': 'left',
    'white-space': 'pre',
    'word-spacing': 'normal',
    'word-break': 'normal',
    'line-height': '1.5',
    'tab-size': '4',
    'hyphens': 'none',
    'padding': '1em',
    'margin': '.5em 0',
    'overflow': 'auto',
    'border-radius': '8px',
}


def _process_codeblock(attrs: Dict[str, str], inner: str) -> str:
    """Process codeblock tag with Pygments syntax highlighting."""
    language = attrs.get('language', 'javascript')
    theme_name = attrs.get('theme', 'oneDark')
    line_numbers = attrs.get('line-numbers', 'false') == 'true'
    font_family = attrs.get('font-family')
    custom_style = _extract_all_style_attributes(attrs)

    if not inner:
        return '<pre><code></code></pre>'

    # Build base styles
    base_style: Dict[str, str] = {}
    base_style.update(_CODEBLOCK_BASE_STYLES)
    base_style['width'] = '100%'
    base_style['box-sizing'] = 'border-box'

    if font_family:
        base_style['font-family'] = font_family

    # Apply custom styles last so they override defaults
    base_style.update(custom_style)

    try:
        from pygments import highlight as pygments_highlight
        from pygments.lexers import get_lexer_by_name, TextLexer
        from pygments.formatters import HtmlFormatter
        from pygments.util import ClassNotFound

        # Resolve the Pygments style name from theme
        pygments_style = _THEME_STYLE_MAP.get(theme_name, 'monokai')

        try:
            lexer = get_lexer_by_name(language, stripall=True)
        except ClassNotFound:
            lexer = None

        if lexer is None:
            # Language not recognized - fall back to plain text
            style_str = _style_to_string(base_style)
            escaped = inner.replace('<', '&lt;').replace('>', '&gt;')
            return f'<pre style="{style_str}"><code>{escaped}</code></pre>'

        # Use HtmlFormatter with inline styles (noclasses=True) for email compatibility
        formatter = HtmlFormatter(
            style=pygments_style,
            noclasses=True,
            nowrap=True,
            linenos=False,
        )

        # Highlight the code
        highlighted = pygments_highlight(inner, lexer, formatter)

        # Build line-based output matching Node SDK format
        lines = highlighted.split('\n')
        # Remove trailing empty line from Pygments output
        if lines and lines[-1] == '':
            lines = lines[:-1]

        lines_html = []
        for i, line_content in enumerate(lines):
            line_number_html = ''
            if line_numbers:
                line_number_html = f'<span style="width:2em;display:inline-block">{i + 1}</span>'
            # Use &nbsp; for empty lines to preserve spacing
            content = line_content if line_content.strip() else '&nbsp;'
            lines_html.append(f'<p style="margin:0;min-height:1em">{line_number_html}{content}</p>')

        style_str = _style_to_string(base_style)
        return f'<pre style="{style_str}"><code>{"".join(lines_html)}</code></pre>'

    except ImportError:
        # Pygments not available - fall back to plain <pre><code>
        style_str = _style_to_string(base_style)
        escaped = inner.replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre style="{style_str}"><code>{escaped}</code></pre>'


def _process_container(attrs: Dict[str, str], inner: str) -> str:
    """Process container tag - split visual styles onto <td>, layout styles onto <table>"""
    style = _extract_all_style_attributes(attrs)
    td_style: Dict[str, str] = {}
    table_style: Dict[str, str] = {}

    # Visual style properties that belong on <td>
    visual_keys = {
        'background-color', 'background-image', 'background-size', 'background-position', 'background-repeat',
        'border', 'border-top', 'border-right', 'border-bottom', 'border-left',
        'border-color', 'border-width', 'border-style',
        'border-radius', 'border-top-left-radius', 'border-top-right-radius',
        'border-bottom-left-radius', 'border-bottom-right-radius',
        'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
    }

    for key, value in style.items():
        if key in visual_keys:
            td_style[key] = value
        else:
            table_style[key] = value

    # Add border-collapse: separate when border-radius is used
    has_border_radius = (
        td_style.get('border-radius')
        or td_style.get('border-top-left-radius')
        or td_style.get('border-top-right-radius')
        or td_style.get('border-bottom-left-radius')
        or td_style.get('border-bottom-right-radius')
    )
    if has_border_radius:
        table_style['border-collapse'] = 'separate'

    # Make fixed widths responsive: width becomes max-width, width set to 100%
    if table_style.get('width') and table_style['width'] != '100%' and table_style['width'] != 'auto':
        if 'max-width' not in table_style:
            table_style['max-width'] = table_style['width']
        table_style['width'] = '100%'

    return f'''<table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" style="{_style_to_string(table_style)}">
<tbody>
<tr style="width:100%">
<td style="{_style_to_string(td_style)}">{inner}</td>
</tr>
</tbody>
</table>'''


def _process_button(attrs: Dict[str, str], inner: str) -> str:
    """Process button with MSO compatibility (like Node.js)"""
    href = attrs.get('href', '#')
    style = _extract_all_style_attributes(attrs)

    # Parse padding
    padding_top, padding_right, padding_bottom, padding_left = _parse_padding(style)

    y = padding_top + padding_bottom
    text_raise = _px_to_pt(y)

    pl_font_width, pl_space_count = _compute_font_width_and_space_count(padding_left)
    pr_font_width, pr_space_count = _compute_font_width_and_space_count(padding_right)

    button_style = {
        'line-height': '100%',
        'text-decoration': 'none',
        'display': 'inline-block',
        'max-width': '100%',
        'mso-padding-alt': '0px',
    }

    # Merge with extracted styles
    button_style.update(style)

    # Override padding with parsed values
    button_style['padding-top'] = f'{padding_top}px'
    button_style['padding-right'] = f'{padding_right}px'
    button_style['padding-bottom'] = f'{padding_bottom}px'
    button_style['padding-left'] = f'{padding_left}px'

    style_str = _style_to_string(button_style)

    left_mso_spaces = '&#8202;' * pl_space_count
    right_mso_spaces = '&#8202;' * pr_space_count

    return f'<a href="{href}" target="_blank" style="{style_str}"><!--[if mso]><i style="mso-font-width:{round(pl_font_width * 100)}%;mso-text-raise:{text_raise}" hidden>{left_mso_spaces}</i><![endif]--><span style="max-width:100%;display:inline-block;line-height:120%;mso-padding-alt:0px;mso-text-raise:{_px_to_pt(padding_bottom)}">{inner}</span><!--[if mso]><i style="mso-font-width:{round(pr_font_width * 100)}%" hidden>{right_mso_spaces}&#8203;</i><![endif]--></a>'


def _parse_padding(style: Dict[str, str]) -> Tuple[int, int, int, int]:
    """Parse padding values from style"""
    if 'padding' in style:
        parts = style['padding'].split()
        if len(parts) == 1:
            val = _parse_px(parts[0])
            return val, val, val, val
        elif len(parts) == 2:
            vertical = _parse_px(parts[0])
            horizontal = _parse_px(parts[1])
            return vertical, horizontal, vertical, horizontal
        elif len(parts) == 4:
            return _parse_px(parts[0]), _parse_px(parts[1]), _parse_px(parts[2]), _parse_px(parts[3])

    return (
        _parse_px(style.get('padding-top', '0')),
        _parse_px(style.get('padding-right', '0')),
        _parse_px(style.get('padding-bottom', '0')),
        _parse_px(style.get('padding-left', '0')),
    )


def _parse_px(s: str) -> int:
    """Parse px value"""
    return int(s.replace('px', '')) if s else 0


def _px_to_pt(px: int) -> int:
    """Convert px to pt for MSO"""
    return (px * 3) // 4


def _compute_font_width_and_space_count(expected_width: int) -> Tuple[float, int]:
    """Compute font width and space count for MSO padding"""
    if expected_width == 0:
        return 0, 0

    smallest_space_count = 0
    max_font_width = 5.0

    while True:
        if smallest_space_count > 0:
            required_font_width = expected_width / smallest_space_count / 2.0
        else:
            required_font_width = math.inf

        if required_font_width <= max_font_width:
            return required_font_width, smallest_space_count
        smallest_space_count += 1


def _process_tag(content: str, tag_name: str, processor: Callable[[Dict[str, str], str], str]) -> str:
    """Process a tag with regex-based parsing"""
    result = content
    open_pattern = f'<{tag_name}([^>]*)>'
    close_tag = f'</{tag_name}>'
    open_tag_start = f'<{tag_name}'

    max_iterations = 10000
    iterations = 0

    while iterations < max_iterations:
        iterations += 1

        # Find all opening tags
        matches = list(re.finditer(open_pattern, result, re.IGNORECASE))
        if not matches:
            break

        processed = False

        # Find the innermost tag (one that has no nested same tags)
        for i in range(len(matches) - 1, -1, -1):
            match = matches[i]
            start = match.start()
            inner_start = match.end()
            attrs_str = match.group(1)

            # Find the next close tag after this opening tag
            close_match = re.search(re.escape(close_tag), result[inner_start:], re.IGNORECASE)
            if not close_match:
                continue
            close_pos = inner_start + close_match.start()

            inner = result[inner_start:close_pos]

            # Check if there's another opening tag inside
            if re.search(re.escape(open_tag_start), inner, re.IGNORECASE):
                # This tag has nested same tags, skip it
                continue

            # This is an innermost tag, process it
            attrs = _parse_attributes(attrs_str)
            replacement = processor(attrs, inner)
            end = close_pos + len(close_tag)

            result = result[:start] + replacement + result[end:]
            processed = True
            break

        if not processed:
            break

    return result


def _parse_attributes(attrs_str: str) -> Dict[str, str]:
    """Parse attributes from an attribute string"""
    attrs = {}
    for match in re.finditer(r'([\w-]+)=(?:"([^"]*)"|\'([^\']*)\')', attrs_str):
        attrs[match.group(1)] = match.group(2) if match.group(2) is not None else match.group(3)
    return attrs


def _extract_all_style_attributes(attrs: Dict[str, str]) -> Dict[str, str]:
    """Extract all style attributes from element attributes (like Node.js extractStyleAttributes)"""
    style = {}

    # Typography attributes
    if 'text-color' in attrs:
        style['color'] = attrs['text-color']
    elif 'color' in attrs:
        style['color'] = attrs['color']
    if 'background-color' in attrs:
        style['background-color'] = attrs['background-color']
    if 'font-size' in attrs:
        style['font-size'] = attrs['font-size']
    if 'font-family' in attrs:
        style['font-family'] = attrs['font-family']
    if 'font-weight' in attrs:
        style['font-weight'] = attrs['font-weight']
    if 'line-height' in attrs:
        style['line-height'] = attrs['line-height']
    if 'text-align' in attrs:
        style['text-align'] = attrs['text-align']
    if 'text-decoration' in attrs:
        style['text-decoration'] = attrs['text-decoration']

    # Dimensions
    if 'width' in attrs:
        style['width'] = attrs['width']
    if 'height' in attrs:
        style['height'] = attrs['height']
    if 'max-width' in attrs:
        style['max-width'] = attrs['max-width']
    if 'max-height' in attrs:
        style['max-height'] = attrs['max-height']
    if 'min-width' in attrs:
        style['min-width'] = attrs['min-width']
    if 'min-height' in attrs:
        style['min-height'] = attrs['min-height']

    # Spacing - Padding
    if 'padding' in attrs:
        style['padding'] = attrs['padding']
    else:
        if 'padding-top' in attrs:
            style['padding-top'] = attrs['padding-top']
        if 'padding-right' in attrs:
            style['padding-right'] = attrs['padding-right']
        if 'padding-bottom' in attrs:
            style['padding-bottom'] = attrs['padding-bottom']
        if 'padding-left' in attrs:
            style['padding-left'] = attrs['padding-left']

    # Spacing - Margin
    if 'margin' in attrs:
        style['margin'] = attrs['margin']
    else:
        if 'margin-top' in attrs:
            style['margin-top'] = attrs['margin-top']
        if 'margin-right' in attrs:
            style['margin-right'] = attrs['margin-right']
        if 'margin-bottom' in attrs:
            style['margin-bottom'] = attrs['margin-bottom']
        if 'margin-left' in attrs:
            style['margin-left'] = attrs['margin-left']

    # Borders
    if 'border' in attrs:
        style['border'] = attrs['border']
    else:
        if 'border-top' in attrs:
            style['border-top'] = attrs['border-top']
        if 'border-right' in attrs:
            style['border-right'] = attrs['border-right']
        if 'border-bottom' in attrs:
            style['border-bottom'] = attrs['border-bottom']
        if 'border-left' in attrs:
            style['border-left'] = attrs['border-left']
        if 'border-color' in attrs:
            style['border-color'] = attrs['border-color']
        if 'border-width' in attrs:
            style['border-width'] = attrs['border-width']
        if 'border-style' in attrs:
            style['border-style'] = attrs['border-style']

    # Border Radius
    if 'border-radius' in attrs:
        style['border-radius'] = attrs['border-radius']
    else:
        if 'border-top-left-radius' in attrs:
            style['border-top-left-radius'] = attrs['border-top-left-radius']
        if 'border-top-right-radius' in attrs:
            style['border-top-right-radius'] = attrs['border-top-right-radius']
        if 'border-bottom-left-radius' in attrs:
            style['border-bottom-left-radius'] = attrs['border-bottom-left-radius']
        if 'border-bottom-right-radius' in attrs:
            style['border-bottom-right-radius'] = attrs['border-bottom-right-radius']

    # Background image
    background_image = attrs.get('background-image')
    background_size = attrs.get('background-size')
    background_position = attrs.get('background-position')
    background_repeat = attrs.get('background-repeat')

    if background_image:
        style['background-image'] = f"url('{background_image}')"
    if background_size:
        style['background-size'] = background_size
    elif background_image:
        style['background-size'] = 'cover'
    if background_position:
        style['background-position'] = background_position
    elif background_image:
        style['background-position'] = 'center'
    if background_repeat:
        style['background-repeat'] = background_repeat
    elif background_image:
        style['background-repeat'] = 'no-repeat'

    return style


def _style_to_string(style: Dict[str, str]) -> str:
    """Convert style dict to inline style string"""
    return ';'.join([f'{k}:{v}' for k, v in style.items()])


def render(markup: str) -> str:
    """
    Render Sevk markup to email-compatible HTML

    Args:
        markup: The Sevk markup to render

    Returns:
        The rendered HTML string
    """
    return generate_email_from_markup(markup)


def extract_variables(markup: str) -> List[str]:
    """
    Extract template variables from Sevk markup.

    Finds all {{variable}} patterns and returns unique variable names.
    Handles fallback syntax: {{var ?? fallback}} by extracting just the variable name.

    Args:
        markup: The Sevk markup to scan

    Returns:
        A list of unique variable names found in the markup
    """
    variables = []
    seen = set()
    for match in re.finditer(r'\{\{(.+?)\}\}', markup):
        raw = match.group(1).strip()
        # Handle fallback syntax: {{var ?? fallback}}
        var_name = raw.split('??')[0].strip()
        if var_name not in seen:
            seen.add(var_name)
            variables.append(var_name)
    return variables


class Renderer:
    """Renderer class for compatibility"""

    def render(self, markup: str) -> str:
        """Render Sevk markup to email-compatible HTML"""
        return generate_email_from_markup(markup)
