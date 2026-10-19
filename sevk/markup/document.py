import re
from typing import List, Optional

from .models import EmailHeadSettings, FontConfig, ParsedEmailContent
from .processor import process_markup
from .tag_scan import (
    find_hidden_preview_div,
    get_all_tag_contents,
    get_first_tag_content,
    get_tag_attributes,
    replace_self_closing,
    strip_tag_pairs,
)


def _render_document(
    html_content: str,
    head_settings: Optional[EmailHeadSettings] = None,
) -> str:
    parsed = parse_email_html(html_content)
    settings = head_settings or parsed.head_settings
    body, gap_styles = process_markup(normalize_markup(parsed.body))

    title_tag = f"<title>{settings.title}</title>" if settings.title else ""
    font_links = generate_font_links(settings.fonts)
    gap_style_tag = f'<style type="text/css">{gap_styles}</style>' if gap_styles else ""
    custom_styles = (
        f'<style type="text/css">{settings.styles}</style>' if settings.styles else ""
    )
    preview_text = (
        '<div style="display:none;font-size:1px;color:#ffffff;line-height:1px;'
        'max-height:0px;max-width:0px;opacity:0;overflow:hidden;">'
        f"{settings.preview_text}</div>"
        if settings.preview_text
        else ""
    )
    lang = settings.lang or "en"
    direction = settings.dir or "ltr"

    return f'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="{lang}" dir="{direction}" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
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
<body style="margin:0;padding:0;word-spacing:normal;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;font-family:ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
<div aria-roledescription="email" role="article">
{preview_text}
{body}
</div>
</body>
</html>'''


def normalize_markup(content: str) -> str:
    result = re.sub(
        r"<link(\s+(?:[\w-]+=(?:\"[^\"]*\"|'[^']*')\s+)*)href=",
        r"<sevk-link\1href=",
        content,
        flags=re.IGNORECASE,
    )
    result = re.sub(r"</link>", "</sevk-link>", result, flags=re.IGNORECASE)
    if not any(tag in result for tag in ("<sevk-email", "<email", "<mail")):
        result = f"<mail><body>{result}</body></mail>"
    return result


def generate_font_links(fonts: List[FontConfig]) -> str:
    return "\n".join(
        f'<link href="{font.url}" rel="stylesheet" type="text/css" />' for font in fonts
    )


def parse_email_html(content: str) -> ParsedEmailContent:
    if re.search(r"<(?:email|mail)[\s>]", content, re.IGNORECASE):
        return _parse_markup_document(content)

    result = ParsedEmailContent()
    result.head_settings.title = (get_first_tag_content(content, "title") or "").strip()
    result.head_settings.styles = "\n".join(get_all_tag_contents(content, "style"))
    for attributes in get_tag_attributes(content, "link"):
        href = re.search(r"href=[\"']([^\"']*)[\"']", attributes, re.IGNORECASE)
        if href is None or "fonts" not in href.group(1).lower():
            continue
        index = len(result.head_settings.fonts)
        family = re.search(r"family=([^:&]+)", href.group(1))
        result.head_settings.fonts.append(
            FontConfig(
                id=f"font-{index}",
                name=family.group(1).replace("+", " ")
                if family
                else f"Font {index + 1}",
                url=href.group(1),
            )
        )

    preview = find_hidden_preview_div(content)
    body = get_first_tag_content(content, "body")
    result.body = content if body is None else body
    if preview:
        result.head_settings.preview_text = preview[0].strip()
        result.body = result.body.replace(preview[1], "", 1)
    result.body = result.body.strip()
    return result


def _parse_markup_document(content: str) -> ParsedEmailContent:
    settings = EmailHeadSettings()
    root_attributes = get_tag_attributes(content, "email") or get_tag_attributes(
        content, "mail"
    )
    if root_attributes:
        lang_match = re.search(
            r'lang=["\']([^"\']*)["\']', root_attributes[0], re.IGNORECASE
        )
        if lang_match:
            settings.lang = lang_match.group(1)
        direction_match = re.search(
            r'dir=["\']([^"\']*)["\']', root_attributes[0], re.IGNORECASE
        )
        if direction_match:
            settings.dir = direction_match.group(1)

    settings.title = (get_first_tag_content(content, "title") or "").strip()
    settings.preview_text = (get_first_tag_content(content, "preview") or "").strip()
    settings.styles = (get_first_tag_content(content, "style") or "").strip()

    seen_font_urls = set()
    for attributes in get_tag_attributes(content, "font"):
        name = re.search(r'name=["\']([^"\']*)["\']', attributes, re.IGNORECASE)
        url = re.search(r'url=["\']([^"\']*)["\']', attributes, re.IGNORECASE)
        if name is None or url is None or url.group(1) in seen_font_urls:
            continue
        seen_font_urls.add(url.group(1))
        settings.fonts.append(
            FontConfig(
                id=f"font-{len(settings.fonts)}",
                name=name.group(1),
                url=url.group(1),
            )
        )

    body = (get_first_tag_content(content, "body") or "").strip()
    if not body:
        stripped = replace_self_closing(content, "email", False, lambda _: "")
        stripped = replace_self_closing(stripped, "mail", False, lambda _: "")
        stripped = re.sub(r"</(?:email|mail)>", "", stripped, flags=re.IGNORECASE)
        for tag in ("head", "title", "preview", "style"):
            stripped = strip_tag_pairs(stripped, tag)
        stripped = replace_self_closing(stripped, "font", False, lambda _: "")
        body = re.sub(r"</font>", "", stripped, flags=re.IGNORECASE).strip()

    result = ParsedEmailContent()
    result.body = body
    result.head_settings = settings
    return result
