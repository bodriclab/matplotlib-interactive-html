"""Unit tests for export and media detection."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from matplotlib_interactive import IframePreview, Theme, detect_media_type, make_plot_interactive
from matplotlib_interactive.media import detect_media_type as detect_media_type_fn


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("image.png", "image"),
        ("photo.JPG", "image"),
        ("clip.mp4", "video"),
        ("movie.webm", "video"),
        ("index.html", "html"),
        ("doc.pdf", "pdf"),
        ("data.csv", "unknown"),
    ],
)
def test_detect_media_type(path, expected):
    assert detect_media_type(path) == expected
    assert detect_media_type_fn(path) == expected


def test_export_contains_svg_and_theme(preview_html):
    content = preview_html.read_text(encoding="utf-8")
    assert "hotspot_overlay" in content
    assert "hotspot-marker" in content
    assert "hotspot-glow" in content
    assert "--accent:" in content
    assert "preview_video" in content
    assert "preview_image" in content
    assert "preview_close" in content
    assert 'data-media-type="image"' in content
    assert 'data-media-type="video"' in content
    assert "layout-splitter" in content
    assert "initSplitter" in content
    assert "--plot-width:" in content
    assert 'data-resizable="true"' in content


def test_invalid_initial_plot_ratio_raises(sample_plot, output_dir):
    fig, ax, x, y = sample_plot
    with pytest.raises(ValueError, match="initial_plot_ratio"):
        make_plot_interactive(
            fig,
            ax,
            x[:1],
            y[:1],
            ["media/a.png"],
            output_dir / "bad.html",
            iframe_preview=IframePreview(initial_plot_ratio=0.1),
        )


def test_classic_mode_uses_target_blank(classic_html):
    content = classic_html.read_text(encoding="utf-8")
    assert 'target="_blank"' in content
    assert 'id="preview_panel"' not in content


def test_forced_dark_theme(sample_plot, output_dir):
    fig, ax, x, y = sample_plot
    path = make_plot_interactive(
        fig,
        ax,
        x[:1],
        y[:1],
        ["media/a.png"],
        output_dir / "dark.html",
        iframe_preview=IframePreview(),
        theme=Theme(mode="dark"),
    )
    content = path.read_text(encoding="utf-8")
    assert "theme-dark" in content
    assert "iframe-preview-mode" in content
