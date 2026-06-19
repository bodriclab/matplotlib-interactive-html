# matplotlib-interactive-html

Generate responsive, self-contained HTML image maps from Matplotlib figures.

Repository: [github.com/bodriclab/matplotlib-interactive-html](https://github.com/bodriclab/matplotlib-interactive-html)

Each data point becomes a clickable hotspot that can open a linked file (image, video, HTML page, PDF, etc.) in a new browser tab or in an optional side preview panel.

**Requirements:** Python 3.9+, Matplotlib 3.5+

Install from PyPI as `matplotlib-interactive-html`, import as `matplotlib_interactive`.

## Installation

```bash
pip install matplotlib-interactive-html
```

From source (development):

```bash
pip install -e .
```

Use a virtual environment if your system Python is externally managed (PEP 668):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Development dependencies:

```bash
pip install -e ".[dev]"
playwright install chromium
```

## Quick start

```python
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from matplotlib_interactive import make_plot_interactive

fig, ax = plt.subplots(figsize=(8, 6))
x = [1, 2, 3]
y = [10, 20, 15]
labels = ["point_A.png", "point_B.png", "point_C.png"]

ax.plot(x, y, "o")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.grid(True, alpha=0.3)

html_path = make_plot_interactive(
    fig,
    ax,
    x,
    y,
    labels,
    "output/plot.html",
)

print(f"Saved: {html_path}")
```

**Open the HTML file by double-clicking it** in your file manager. No server is required for images.

Place linked files (`point_A.png`, etc.) in the **same folder** as the HTML file, or use relative paths from that folder.

## Classic mode (new tab)

By default (`iframe_preview=None`), each hotspot opens its linked file in a **new browser tab** (`target="_blank"`). No side panel is added to the page.

Plot zoom (main plot only): **Ctrl + mouse wheel** on the main graph to zoom, **double-click** to reset, **Shift + drag** or **middle-click drag** to pan when zoomed. Zoom is disabled inside the preview panel and when a plot is embedded in an iframe.

## Preview panel

Enable an in-page side panel instead of opening files in a new tab:

```python
from matplotlib_interactive import IframePreview, Theme, make_plot_interactive

make_plot_interactive(
    fig,
    ax,
    x,
    y,
    labels,
    "output/plot.html",
    iframe_preview=IframePreview(),
    theme=Theme(mode="auto"),
)
```

Features:

- Auto-sized layout: plot and preview panel share the viewport
- **Draggable splitter** between plot and panel (drag to resize)
- SVG hotspot markers: hidden at rest, shown on direct hover; selected point highlighted with accent ring and pulse
- Automatic media type detection (image, video, HTML, PDF)
- Panel header with filename, open-in-new-tab button, and close button
- Ctrl+click (Cmd+click on macOS) on a hotspot opens in a new tab

### Plot zoom

- **Ctrl + mouse wheel** over the **main plot** zooms in/out centered on the cursor (visual zoom on the PNG)
- Default zoom on page load: **100%** (fit to the plot area)
- Does not apply to the preview panel (image, video, iframe) or to plots embedded in an iframe
- **Double-click** the main plot to reset zoom
- **Shift + drag** or **middle-click drag** pans when zoomed in

### Resizable splitter

In auto layout mode (`IframePreview()` without explicit `width`/`height`), a vertical handle appears between the plot and the preview panel when a file is opened. Drag it to adjust how much space each area uses.

```python
IframePreview(
    initial_plot_ratio=0.8,  # initial plot width fraction (0.25–0.85)
    resizable=True,            # show draggable splitter (default)
)
```

Set `resizable=False` for a fixed 80/20 split without a drag handle.

## Supported media types

| Extension | Preview element |
|-----------|-----------------|
| `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg` | `<img>` |
| `.mp4`, `.webm`, `.ogg` | `<video controls>` |
| `.html`, `.htm` | `<iframe>` |
| `.pdf` | `<iframe>` |
| other | fallback download link |

## Opening generated files

### Local files (recommended for images)

1. Generate the HTML with `make_plot_interactive(...)`
2. Copy linked files next to the HTML if needed
3. **Double-click the `.html` file** to open it in your browser

Images work with the `file://` protocol.

### When HTTP may be needed

Some browsers block `file://` access for **videos** and **embedded HTML/PDF** in the preview panel. In that case only, use the optional local server below.

## Optional HTTP server

Only needed if your browser refuses videos or iframes when opening files locally:

```bash
matplotlib-interactive serve output/
# open http://127.0.0.1:8000/plot.html
```

If the command is not found, activate your virtual environment first or run:

```bash
python -m matplotlib_interactive.cli serve output/
```

Options: `--port`, `--host`, `--open`.

Equivalent without this package:

```bash
cd output && python3 -m http.server 8000
```

## API reference

### `make_plot_interactive`

```python
make_plot_interactive(
    fig,
    ax,
    x_data,
    y_data,
    labels,
    output_html_path,
    *,
    hotspot_radius_px=5,
    image_dpi=None,
    iframe_preview=None,
    theme=Theme(mode="auto"),
    show_hotspots=True,
)
```

| Parameter | Description |
|-----------|-------------|
| `fig` | Matplotlib `Figure` |
| `ax` | Matplotlib `Axes` for coordinate transforms |
| `x_data`, `y_data` | Point coordinates in data space |
| `labels` | One path or URL per point |
| `output_html_path` | Output HTML path; PNG saved alongside |
| `hotspot_radius_px` | Hotspot radius in pixels at native resolution |
| `image_dpi` | DPI for saved PNG (default: `fig.dpi`) |
| `iframe_preview` | Side panel configuration (`IframePreview`) |
| `theme` | Page theme (`Theme`) |
| `show_hotspots` | Show visible SVG hotspot markers (default: `True`) |

### `IframePreview`

| Attribute | Default | Description |
|-----------|---------|-------------|
| `width`, `height` | `None` | Fixed panel size; `None` enables auto layout |
| `plot_width` | `"80%"` | Max plot width when panel is closed |
| `margin` | `"16px"` | Layout margin in auto mode |
| `initial_plot_ratio` | `0.8` | Initial plot fraction when panel is open (0.25–0.85) |
| `resizable` | `True` | Show draggable splitter in auto layout |
| `left`, `top`, `right`, `bottom` | — | Position overrides for fixed-size mode |

### `Theme`

```python
Theme(mode="auto")   # follow system preference (default)
Theme(mode="light")
Theme(mode="dark")
```

### `detect_media_type`

```python
from matplotlib_interactive import detect_media_type

detect_media_type("clip.mp4")  # returns "video"
```

## Development

```bash
pytest tests/ -m "not browser"
pytest tests/ -m browser
```

See [`examples/demo.py`](examples/demo.py) for a full preview-panel example.

## Notes

- Use a non-interactive backend such as `Agg` in scripts and CI.
- The generated HTML and PNG are standalone files you can share as a folder.
- `show_hotspots` and `serve` are independent: hotspots are on by default; the HTTP server is optional.

## License

MIT License. See [LICENSE](LICENSE).
