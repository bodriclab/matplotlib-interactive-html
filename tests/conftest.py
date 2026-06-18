"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest
from PIL import Image

from matplotlib_interactive import IframePreview, Theme, make_plot_interactive


@pytest.fixture
def sample_plot():
    fig, ax = plt.subplots(figsize=(8, 6))
    x = [1, 2, 3]
    y = [10, 20, 15]
    ax.plot(x, y, "o")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return fig, ax, x, y


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    Image.new("RGB", (120, 90), color=(180, 200, 255)).save(media_dir / "a.png")
    Image.new("RGB", (120, 90), color=(255, 200, 180)).save(media_dir / "b.png")
    (media_dir / "page.html").write_text("<html><body><p>test</p></body></html>", encoding="utf-8")
    (media_dir / "clip.mp4").write_bytes(_minimal_mp4())
    return tmp_path


def _minimal_mp4() -> bytes:
    # Minimal valid MP4 container (ftyp + mdat) for browser src assignment tests.
    return (
        b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41"
        b"\x00\x00\x00\x08mdat"
    )


@pytest.fixture
def classic_html(sample_plot, output_dir):
    fig, ax, x, y = sample_plot
    labels = ["media/a.png", "media/b.png", "media/page.html"]
    path = make_plot_interactive(fig, ax, x, y, labels, output_dir / "classic.html")
    return path


@pytest.fixture
def preview_html(sample_plot, output_dir):
    fig, ax, x, y = sample_plot
    labels = ["media/a.png", "media/b.png", "media/clip.mp4"]
    path = make_plot_interactive(
        fig,
        ax,
        x,
        y,
        labels,
        output_dir / "preview.html",
        iframe_preview=IframePreview(),
        theme=Theme(mode="auto"),
    )
    return path
