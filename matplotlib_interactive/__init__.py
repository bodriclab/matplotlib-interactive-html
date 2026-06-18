"""Generate responsive HTML image maps from Matplotlib figures."""

from ._version import __version__
from .exporter import IframePreview, make_plot_interactive
from .media import detect_media_type
from .theme import Theme

__all__ = [
    "IframePreview",
    "Theme",
    "__version__",
    "detect_media_type",
    "make_plot_interactive",
]
