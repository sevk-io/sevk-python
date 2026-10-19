from typing import List


class FontConfig:
    def __init__(self, id: str = "", name: str = "", url: str = ""):
        self.id = id
        self.name = name
        self.url = url


class EmailHeadSettings:
    def __init__(self) -> None:
        self.title = ""
        self.preview_text = ""
        self.styles = ""
        self.fonts: List[FontConfig] = []
        self.lang = ""
        self.dir = ""


class ParsedEmailContent:
    def __init__(self) -> None:
        self.body = ""
        self.head_settings = EmailHeadSettings()
