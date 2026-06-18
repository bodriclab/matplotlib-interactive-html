"""Theme configuration for generated HTML pages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ThemeMode = Literal["light", "dark", "auto"]


@dataclass
class Theme:
    """Color theme for the generated interactive plot page.

    Attributes:
        mode: ``"auto"`` follows the browser/OS preference, ``"light"`` or
            ``"dark"`` forces a specific theme.
    """

    mode: ThemeMode = "auto"


def build_theme_css(theme: Theme) -> str:
    """Build CSS variables and theme overrides."""
    auto_dark = """
        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #111318;
                --text: #e8e8e8;
                --surface: #1c1f26;
                --panel-bg: var(--surface);
                --panel-header-bg: var(--surface);
                --border: #2d3139;
                --accent: #60a5fa;
                --hotspot-fill: rgba(96, 165, 250, 0.2);
                --hotspot-stroke: #60a5fa;
                --shadow: 0 1px 2px rgba(0, 0, 0, 0.3), 0 8px 24px rgba(0, 0, 0, 0.5);
                --radius: 10px;
                --btn-hover: rgba(255, 255, 255, 0.08);
                --muted: #999999;
            }
        }"""

    forced_light = """
        body.theme-light {
            --bg: #f8f9fa;
            --text: #333333;
            --surface: #ffffff;
            --panel-bg: var(--surface);
            --panel-header-bg: var(--surface);
            --border: #e5e7eb;
            --accent: #2563eb;
            --hotspot-fill: rgba(59, 130, 246, 0.18);
            --hotspot-stroke: #3b82f6;
            --shadow: 0 1px 2px rgba(0, 0, 0, 0.06), 0 8px 24px rgba(0, 0, 0, 0.08);
            --radius: 10px;
            --btn-hover: rgba(0, 0, 0, 0.06);
            --muted: #777777;
        }"""

    forced_dark = """
        body.theme-dark {
            --bg: #111318;
            --text: #e8e8e8;
            --surface: #1c1f26;
            --panel-bg: var(--surface);
            --panel-header-bg: var(--surface);
            --border: #2d3139;
            --accent: #60a5fa;
            --hotspot-fill: rgba(96, 165, 250, 0.2);
            --hotspot-stroke: #60a5fa;
            --shadow: 0 1px 2px rgba(0, 0, 0, 0.3), 0 8px 24px rgba(0, 0, 0, 0.5);
            --radius: 10px;
            --btn-hover: rgba(255, 255, 255, 0.08);
            --muted: #999999;
        }"""

    base = """
        :root {
            --bg: #f8f9fa;
            --text: #333333;
            --surface: #ffffff;
            --panel-bg: var(--surface);
            --panel-header-bg: var(--surface);
            --border: #e5e7eb;
            --accent: #2563eb;
            --hotspot-fill: rgba(59, 130, 246, 0.18);
            --hotspot-stroke: #3b82f6;
            --shadow: 0 1px 2px rgba(0, 0, 0, 0.06), 0 8px 24px rgba(0, 0, 0, 0.08);
            --radius: 10px;
            --btn-hover: rgba(0, 0, 0, 0.06);
            --muted: #777777;
        }"""

    if theme.mode == "auto":
        return base + auto_dark
    if theme.mode == "dark":
        return base + forced_dark
    return base + forced_light


def body_theme_class(theme: Theme) -> str:
    """Return optional body CSS class for forced themes."""
    if theme.mode == "light":
        return " theme-light"
    if theme.mode == "dark":
        return " theme-dark"
    return ""
