"""Export Matplotlib figures as responsive HTML image maps."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, Union

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .templates import build_hotspot_areas, build_html_page
from .theme import Theme

PathLike = Union[str, Path]

_DEFAULT_HOTSPOT_RADIUS_PX = 10
_DEFAULT_PREVIEW_MARGIN = "16px"


@dataclass
class IframePreview:
    """Configuration for in-page preview on hotspot click.

    When passed to :func:`make_plot_interactive`, hotspots open linked resources
    in a side panel instead of a new browser tab. By default, the panel fills the
    remaining viewport space next to the plot without overlapping it.

    Attributes:
        width: CSS width of the preview panel. ``None`` auto-sizes the panel to
            use all remaining horizontal space beside the plot.
        height: CSS height of the preview panel. ``None`` stretches the panel to
            the available viewport height.
        right: CSS right offset for fixed-position mode.
        bottom: CSS bottom offset for fixed-position mode.
        left: Optional CSS left offset for fixed-position mode.
        top: Optional CSS top offset for fixed-position mode.
        plot_width: CSS maximum width of the plot container when preview mode is
            active. The plot uses at most this width and shrinks further if
            needed to stay within the viewport.
        margin: CSS margin around the layout in auto-size mode.
        initial_plot_ratio: Initial width fraction for the plot area in auto
            layout (0.25 to 0.85). The user can drag the splitter to adjust.
        resizable: Whether to show a draggable splitter between plot and panel
            in auto layout mode.
    """

    width: str | None = None
    height: str | None = None
    right: str = "16px"
    bottom: str = "16px"
    left: str | None = None
    top: str | None = None
    plot_width: str = "80%"
    margin: str = _DEFAULT_PREVIEW_MARGIN
    initial_plot_ratio: float = 0.8
    resizable: bool = True


def make_plot_interactive(
    fig: Figure,
    ax: Axes,
    x_data: Sequence[float],
    y_data: Sequence[float],
    labels: Sequence[str],
    output_html_path: PathLike,
    *,
    hotspot_radius_px: int = _DEFAULT_HOTSPOT_RADIUS_PX,
    image_dpi: int | None = None,
    iframe_preview: IframePreview | None = None,
    theme: Theme | None = None,
    show_hotspots: bool = True,
) -> Path:
    """Export a Matplotlib figure as a responsive HTML image map.

    The function saves the figure as a PNG next to the HTML file, then builds an
    HTML page with clickable circular hotspots aligned on the provided data
    points. Hotspot coordinates are recalculated in JavaScript when the browser
    window is resized, so the map stays aligned with the displayed image.

    Args:
        fig: Matplotlib figure containing the plot.
        ax: Axes object used to transform data coordinates into pixel positions.
        x_data: X coordinates of the interactive points, in data space.
        y_data: Y coordinates of the interactive points, in data space.
        labels: One path or URL per point. Used as the hotspot ``title``. In
            classic mode (no ``iframe_preview``), each label is the link
            target opened in a new tab. With ``iframe_preview``, each label is
            the file path shown in the side panel.
        output_html_path: Destination path for the generated HTML file. The
            companion PNG is written alongside it, using the same stem and a
            ``.png`` extension.
        hotspot_radius_px: Radius of each circular hotspot, in pixels at native
            figure resolution.
        image_dpi: DPI used when saving the PNG. Defaults to ``fig.dpi``.
        iframe_preview: When set, linked resources open in a side panel on the
            page instead of a new browser tab.
        theme: Color theme for the generated page. Defaults to auto (system).
        show_hotspots: Whether to render visible SVG hotspot markers.

    Returns:
        Path to the generated HTML file.

    Raises:
        ValueError: If ``x_data``, ``y_data``, and ``labels`` do not have the
            same length, or if ``hotspot_radius_px`` is not positive.
    """
    if not (len(x_data) == len(y_data) == len(labels)):
        raise ValueError(
            "x_data, y_data, and labels must have the same length "
            f"(got {len(x_data)}, {len(y_data)}, and {len(labels)})."
        )
    if hotspot_radius_px <= 0:
        raise ValueError("hotspot_radius_px must be a positive integer.")
    if iframe_preview is not None and not (
        0.25 <= iframe_preview.initial_plot_ratio <= 0.85
    ):
        raise ValueError("initial_plot_ratio must be between 0.25 and 0.85.")

    output_html_path = Path(output_html_path)
    output_html_path.parent.mkdir(parents=True, exist_ok=True)

    dpi = image_dpi if image_dpi is not None else fig.dpi

    fig.canvas.draw()

    fig_width_px, fig_height_px = fig.get_size_inches() * dpi
    fig_width_px = round(fig_width_px)
    fig_height_px = round(fig_height_px)
    zones_html, hotspots = build_hotspot_areas(
        ax=ax,
        x_data=x_data,
        y_data=y_data,
        labels=labels,
        fig_height_px=fig_height_px,
        hotspot_radius_px=hotspot_radius_px,
        iframe_preview=iframe_preview is not None,
    )

    image_path = output_html_path.with_suffix(".png")
    fig.savefig(image_path, dpi=dpi)

    html_content = build_html_page(
        title=output_html_path.stem,
        image_filename=image_path.name,
        zones_html=zones_html,
        hotspots=hotspots,
        fig_width_px=int(fig_width_px),
        fig_height_px=int(fig_height_px),
        iframe_preview=iframe_preview,
        theme=theme,
        show_hotspots=show_hotspots,
    )

    output_html_path.write_text(html_content, encoding="utf-8")
    return output_html_path
