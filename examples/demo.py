"""Generate a demo interactive plot in the current directory."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from matplotlib_interactive import IframePreview, Theme, make_plot_interactive

fig, ax = plt.subplots(figsize=(8, 6))
x = [1, 2, 3]
y = [10, 20, 15]
labels = ["media/a.png", "media/b.png", "media/clip.mp4"]

ax.plot(x, y, "o")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.grid(True, alpha=0.3)

path = make_plot_interactive(
    fig,
    ax,
    x,
    y,
    labels,
    "plot.html",
    iframe_preview=IframePreview(),
    theme=Theme(mode="auto"),
)
print(f"Saved: {path}")
