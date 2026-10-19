from dataclasses import dataclass


@dataclass(frozen=True)
class SevkOptions:
    """Connection settings for :class:`Sevk`."""

    base_url: str = "https://api.sevk.io"
    timeout: float = 30
