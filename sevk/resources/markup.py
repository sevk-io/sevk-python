from typing import List

from ..markup import extract_variables as markup_extract_variables
from ..markup import render as markup_render


class Markup:
    """Markup resource for rendering and variable extraction"""

    def render(self, markup: str) -> str:
        """Convert sevk markup into complete, email-compatible HTML."""
        return markup_render(markup)

    def extract_variables(self, markup: str) -> List[str]:
        """Return each unique template variable referenced by the markup."""
        return markup_extract_variables(markup)
