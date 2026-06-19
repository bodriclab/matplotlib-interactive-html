"""HTML, CSS and JavaScript template builders."""

from __future__ import annotations

import html
import json
from typing import TYPE_CHECKING

from .media import detect_media_type
from .theme import Theme, body_theme_class, build_theme_css

if TYPE_CHECKING:
    from .exporter import IframePreview

_DEFAULT_CONTAINER_WIDTH = "65vw"

_HOTSPOT_OVERLAY_HTML = """<svg id="hotspot_overlay" class="hotspot-overlay" aria-hidden="true">
                <defs>
                    <filter id="hotspot-glow" x="-80%" y="-80%" width="260%" height="260%">
                        <feGaussianBlur in="SourceGraphic" stdDeviation="1.5" result="blur"/>
                        <feMerge>
                            <feMergeNode in="blur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>
            </svg>"""

PREVIEW_SPLITTER_HTML = """
    <div class="layout-splitter" id="layout_splitter" hidden aria-hidden="true" role="separator" aria-orientation="vertical" aria-label="Resize panels"></div>"""

PREVIEW_PANEL_HTML = """
    <aside class="{panel_class}" id="preview_panel">
        <div class="preview-header">
            <span class="preview-filename" id="preview_filename" title=""></span>
            <div class="preview-actions">
                <button type="button" id="preview_open_tab" title="Open in new tab" aria-label="Open in new tab">&#8599;</button>
                <button type="button" id="preview_close" title="Close panel" aria-label="Close panel">&times;</button>
            </div>
        </div>
        <div class="preview-frame-wrap" id="preview_frame_wrap">
            <img id="preview_image" class="preview-media" alt="Preview" hidden>
            <video id="preview_video" class="preview-media" controls hidden></video>
            <iframe id="preview_iframe" class="preview-media" title="Preview" hidden></iframe>
            <div id="preview_fallback" class="preview-media preview-fallback" hidden>
                <p>Preview not available for this file type.</p>
                <a id="preview_fallback_link" href="#" target="_blank" rel="noopener noreferrer">Open file</a>
            </div>
        </div>
    </aside>
</div>"""


def uses_auto_preview_layout(iframe_preview: IframePreview) -> bool:
    """Return whether the preview panel should auto-fill remaining space."""
    return iframe_preview.width is None and iframe_preview.height is None


def build_hotspot_areas(
    ax,
    x_data,
    y_data,
    labels,
    fig_height_px: float,
    hotspot_radius_px: int,
    *,
    iframe_preview: bool,
    scale_factor: float = 1.0,
) -> tuple[str, list[dict]]:
    """Build HTML area elements and hotspot metadata for SVG overlay."""
    zones: list[str] = []
    hotspots: list[dict] = []

    for index, (x_value, y_value, label) in enumerate(zip(x_data, y_data, labels)):
        px, py = ax.transData.transform((x_value, y_value))
        px_scaled = px * scale_factor
        py_scaled = py * scale_factor
        py_html = fig_height_px - py_scaled
        radius_scaled = max(1, round(hotspot_radius_px * scale_factor))
        coords = f"{round(px_scaled)},{round(py_html)},{radius_scaled}"
        safe_label = html.escape(str(label), quote=True)
        media_type = detect_media_type(label)

        hotspots.append(
            {
                "index": index,
                "src": str(label),
                "mediaType": media_type,
                "coords": coords,
            }
        )

        if iframe_preview:
            zones.append(
                f'                <area shape="circle" coords="{coords}" '
                f'data-coords="{coords}" href="#" class="preview-hotspot" '
                f'data-index="{index}" data-src="{safe_label}" '
                f'data-media-type="{media_type}" title="{safe_label}">\n'
            )
        else:
            zones.append(
                f'                <area shape="circle" coords="{coords}" '
                f'data-coords="{coords}" href="{safe_label}" target="_blank" '
                f'data-index="{index}" title="{safe_label}">\n'
            )

    return "".join(zones), hotspots


def _build_iframe_position_css(iframe_preview: IframePreview) -> str:
    if iframe_preview.left is not None:
        horizontal = f"left: {iframe_preview.left};"
    else:
        horizontal = f"right: {iframe_preview.right};"

    if iframe_preview.top is not None:
        vertical = f"top: {iframe_preview.top};"
    else:
        vertical = f"bottom: {iframe_preview.bottom};"

    return f"{horizontal}\n            {vertical}"


def _shared_preview_css() -> str:
    return """
        .preview-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            padding: 10px 12px;
            font: 600 13px/1.4 system-ui, -apple-system, sans-serif;
            color: var(--text);
            background: var(--panel-header-bg);
            border-bottom: 1px solid var(--border);
            user-select: none;
        }
        .preview-filename {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            flex: 1 1 auto;
            min-width: 0;
            color: var(--muted);
            font-weight: 600;
        }
        .preview-actions {
            display: flex;
            gap: 4px;
            flex: 0 0 auto;
        }
        .preview-actions button {
            width: 28px;
            height: 28px;
            border: none;
            border-radius: 6px;
            background: transparent;
            color: var(--muted);
            cursor: pointer;
            font-size: 16px;
            line-height: 1;
            padding: 0;
            transition: background-color 0.15s ease, color 0.15s ease;
        }
        .preview-actions button:hover {
            background: var(--btn-hover);
            color: var(--text);
        }
        .preview-frame-wrap {
            flex: 1 1 auto;
            min-height: 0;
            position: relative;
            background-color: var(--bg);
            display: flex;
            align-items: stretch;
            justify-content: center;
            padding: 12px;
            box-sizing: border-box;
        }
        .preview-media {
            width: 100%;
            height: 100%;
            border: none;
            display: block;
            object-fit: contain;
            background-color: transparent;
        }
        #preview_image {
            max-height: 100%;
            height: auto;
        }
        .preview-media[hidden] {
            display: none !important;
        }
        .preview-fallback {
            padding: 20px;
            text-align: center;
            color: var(--text);
        }
        .preview-fallback a {
            color: var(--accent);
        }"""


def _hotspot_css(show_hotspots: bool) -> str:
    if not show_hotspots:
        return ""
    return """
        @keyframes hotspotAppear {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes hotspotHaloPulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.6; }
        }
        @keyframes hotspotRingPulse {
            0%, 100% { stroke-opacity: 1; }
            50% { stroke-opacity: 0.55; }
        }
        .plot-surface {
            position: relative;
            overflow: hidden;
            width: 100%;
        }
        .hotspot-overlay {
            position: absolute;
            top: 0;
            left: 0;
            pointer-events: none;
            overflow: visible;
        }
        .hotspot-marker {
            opacity: 0;
            pointer-events: all;
            cursor: pointer;
            transition: opacity 0.2s ease;
        }
        .hotspot-marker:not(.active):hover {
            opacity: 0.65;
        }
        .hotspot-halo {
            fill: var(--hotspot-fill);
            stroke: none;
            opacity: 0;
            transition: opacity 0.2s ease;
        }
        .hotspot-marker:not(.active):hover .hotspot-halo {
            opacity: 0.45;
        }
        .hotspot-marker.active .hotspot-halo {
            opacity: 1;
        }
        .hotspot-ring {
            fill: none;
            stroke: var(--hotspot-stroke);
            stroke-width: 2;
            filter: url(#hotspot-glow);
        }
        .hotspot-marker.active .hotspot-ring {
            stroke: var(--accent);
            stroke-width: 2.5;
        }
        .hotspot-marker.active {
            opacity: 1;
            animation: hotspotAppear 0.25s ease-out;
        }
        .hotspot-marker.active .hotspot-halo {
            animation: hotspotHaloPulse 2.5s ease-in-out infinite;
        }
        .hotspot-marker.active .hotspot-ring {
            animation: hotspotRingPulse 2.5s ease-in-out infinite;
        }
        @media (prefers-reduced-motion: reduce) {
            .hotspot-marker.active,
            .hotspot-marker.active .hotspot-halo,
            .hotspot-marker.active .hotspot-ring {
                animation: none;
            }
        }"""


def build_auto_preview_css(iframe_preview: IframePreview) -> str:
    margin = iframe_preview.margin
    plot_width = iframe_preview.plot_width

    return f"""
        body.iframe-preview-mode {{
            overflow: hidden;
            display: block;
            width: 100vw;
            height: 100vh;
            max-width: 100vw;
            max-height: 100vh;
            min-height: 0;
        }}
        body.iframe-preview-mode .layout {{
            display: grid;
            width: 100vw;
            height: 100vh;
            padding: {margin};
            box-sizing: border-box;
            gap: {margin};
        }}
        body.iframe-preview-mode:not(.preview-active) .layout {{
            grid-template-columns: 1fr;
            place-items: center;
        }}
        body.iframe-preview-mode:not(.preview-active) .container {{
            width: min({plot_width}, 100%);
            height: 100%;
            max-height: 100%;
        }}
        body.iframe-preview-mode.preview-active .layout {{
            display: flex;
            flex-direction: row;
            align-items: stretch;
            gap: 12px;
        }}
        body.iframe-preview-mode.preview-active .container {{
            flex: 0 0 var(--plot-width, 80%);
            min-width: 25%;
            max-width: 85%;
            width: auto;
            height: 100%;
        }}
        .layout-splitter {{
            display: none;
            width: 6px;
            flex-shrink: 0;
            cursor: col-resize;
            background: var(--border);
            border-radius: 3px;
            margin: 0;
            align-self: stretch;
        }}
        .layout-splitter:not([hidden]) {{
            display: block;
        }}
        .layout-splitter:hover,
        .layout-splitter.dragging {{
            background: var(--accent);
        }}
        body.iframe-preview-mode.preview-active .preview-panel {{
            flex: 1 1 0;
            min-width: 180px;
        }}
        body.iframe-preview-mode .container {{
            position: relative;
            min-width: 0;
            min-height: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        body.iframe-preview-mode .plot-surface {{
            position: relative;
            width: 100%;
            height: 100%;
            min-width: 0;
            min-height: 0;
            overflow: hidden;
        }}
        body.iframe-preview-mode.preview-active .container {{
            width: auto;
            height: 100%;
        }}
        body.iframe-preview-mode #plot_image {{
            position: absolute;
            max-width: none;
            max-height: none;
            object-fit: fill;
            display: block;
            border: none;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            background: var(--surface);
        }}
        .preview-panel {{
            display: none;
            min-width: 0;
            min-height: 0;
            height: 100%;
            flex-direction: column;
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow);
            background-color: var(--panel-bg);
        }}
        .preview-panel.visible {{
            display: flex;
        }}
        {_shared_preview_css()}"""


def build_fixed_preview_css(iframe_preview: IframePreview, container_width: str) -> str:
    position_css = _build_iframe_position_css(iframe_preview)
    width = iframe_preview.width or "320px"
    height = iframe_preview.height or "240px"

    return f"""
        body.iframe-preview-mode {{
            overflow: hidden;
            display: block;
            width: 100vw;
            height: 100vh;
            max-width: 100vw;
            max-height: 100vh;
            min-height: 0;
        }}
        body.iframe-preview-mode .container {{
            position: relative;
            width: min({container_width}, calc(100vw - 40px));
            height: calc(100vh - 40px);
            max-width: min({container_width}, calc(100vw - 40px));
            max-height: calc(100vh - 40px);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        body.iframe-preview-mode #plot_image {{
            position: absolute;
            max-width: none;
            max-height: none;
            object-fit: fill;
            display: block;
            border: none;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            background: var(--surface);
        }}
        .preview-panel-fixed {{
            position: fixed;
            z-index: 10;
            width: {width};
            {position_css}
            display: none;
            flex-direction: column;
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow);
            background-color: var(--panel-bg);
        }}
        .preview-panel-fixed.visible {{
            display: flex;
        }}
        .preview-panel-fixed .preview-frame-wrap {{
            height: {height};
        }}
        {_shared_preview_css()}"""


def build_resize_map_js(
    fig_width_px: int,
    fig_height_px: int,
    hotspots: list[dict],
    *,
    show_hotspots: bool,
    iframe_preview: bool,
) -> str:
    hotspots_json = json.dumps(hotspots)
    svg_block = ""
    if show_hotspots:
        svg_block = f"""
            const overlay = document.getElementById('hotspot_overlay');
            const hotspotData = {hotspots_json};
            if (overlay) {{
                overlay.style.left = `${{offsetX}}px`;
                overlay.style.top = `${{offsetY}}px`;
                overlay.style.width = `${{effectiveWidth}}px`;
                overlay.style.height = `${{effectiveHeight}}px`;
                overlay.setAttribute('viewBox', `0 0 ${{NATURAL_WIDTH}} ${{NATURAL_HEIGHT}}`);
                overlay.setAttribute('width', effectiveWidth);
                overlay.setAttribute('height', effectiveHeight);

                if (overlay.querySelectorAll('.hotspot-marker').length !== hotspotData.length) {{
                    overlay.querySelectorAll('.hotspot-marker').forEach((marker) => marker.remove());
                    hotspotData.forEach((hotspot) => {{
                        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                        marker.classList.add('hotspot-marker');
                        marker.dataset.index = String(hotspot.index);
                        marker.dataset.src = hotspot.src;
                        marker.dataset.mediaType = hotspot.mediaType;

                        const halo = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                        halo.classList.add('hotspot-halo');

                        const ring = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                        ring.classList.add('hotspot-ring');

                        marker.appendChild(halo);
                        marker.appendChild(ring);
                        overlay.appendChild(marker);
                    }});
                }}

                overlay.querySelectorAll('.hotspot-marker').forEach((marker, index) => {{
                    const originalCoords = hotspotData[index].coords.split(',');
                    const cx = originalCoords[0];
                    const cy = originalCoords[1];
                    const radius = Number(originalCoords[2]);
                    const halo = marker.querySelector('.hotspot-halo');
                    const ring = marker.querySelector('.hotspot-ring');
                    halo.setAttribute('cx', cx);
                    halo.setAttribute('cy', cy);
                    halo.setAttribute('r', String(radius * 1.65));
                    ring.setAttribute('cx', cx);
                    ring.setAttribute('cy', cy);
                    ring.setAttribute('r', String(radius));
                }});
            }}"""

    return f"""
        const HOTSPOT_DATA = {hotspots_json};
        const NATURAL_WIDTH = {fig_width_px};
        const NATURAL_HEIGHT = {fig_height_px};
        const plotZoom = {{ level: 1, panX: 0, panY: 0 }};
        window.plotZoom = plotZoom;
        const ZOOM_MIN = 1;
        const ZOOM_MAX = 10;
        const ZOOM_STEP = 1.1;
        let hotspotInteractionsReady = false;
        let plotZoomInteractionsReady = false;
        let panState = null;

        function getPlotSurface() {{
            return document.getElementById('main_plot_surface');
        }}

        function isEmbeddedPreview() {{
            return window.self !== window.top;
        }}

        function computeBaseLayout(surface) {{
            let containerWidth = surface.clientWidth;
            let containerHeight = surface.clientHeight;
            if (!containerWidth) {{
                return null;
            }}
            if (!containerHeight) {{
                containerHeight = Math.round(containerWidth * NATURAL_HEIGHT / NATURAL_WIDTH);
            }}

            const scale = Math.min(
                containerWidth / NATURAL_WIDTH,
                containerHeight / NATURAL_HEIGHT
            );
            const renderedWidth = NATURAL_WIDTH * scale;
            const renderedHeight = NATURAL_HEIGHT * scale;
            const offsetX = (containerWidth - renderedWidth) / 2;
            const offsetY = (containerHeight - renderedHeight) / 2;
            return {{
                scale,
                offsetX,
                offsetY,
                renderedWidth,
                renderedHeight,
                containerWidth,
                containerHeight,
            }};
        }}

        function computePlotLayout(surface) {{
            const base = computeBaseLayout(surface);
            if (!base) {{
                return null;
            }}

            const effectiveScale = base.scale * plotZoom.level;
            const effectiveWidth = NATURAL_WIDTH * effectiveScale;
            const effectiveHeight = NATURAL_HEIGHT * effectiveScale;
            const offsetX = base.offsetX + plotZoom.panX;
            const offsetY = base.offsetY + plotZoom.panY;
            return {{
                ...base,
                effectiveScale,
                effectiveWidth,
                effectiveHeight,
                offsetX,
                offsetY,
            }};
        }}

        function clampPan(layout) {{
            if (plotZoom.level <= ZOOM_MIN) {{
                plotZoom.panX = 0;
                plotZoom.panY = 0;
                return;
            }}

            const minLeft = layout.containerWidth - layout.effectiveWidth;
            const maxLeft = 0;
            const minTop = layout.containerHeight - layout.effectiveHeight;
            const maxTop = 0;
            const clampedLeft = Math.max(minLeft, Math.min(maxLeft, layout.offsetX));
            const clampedTop = Math.max(minTop, Math.min(maxTop, layout.offsetY));
            plotZoom.panX += clampedLeft - layout.offsetX;
            plotZoom.panY += clampedTop - layout.offsetY;
        }}

        function applyPlotLayout() {{
            const surface = getPlotSurface();
            const img = document.getElementById('plot_image');
            if (!surface || !img) {{
                return;
            }}

            let layout = computePlotLayout(surface);
            if (!layout) {{
                return;
            }}

            clampPan(layout);
            layout = computePlotLayout(surface);
            if (!layout) {{
                return;
            }}

            const {{
                effectiveScale,
                effectiveWidth,
                effectiveHeight,
                offsetX,
                offsetY,
            }} = layout;

            img.style.position = 'absolute';
            img.style.left = `${{offsetX}}px`;
            img.style.top = `${{offsetY}}px`;
            img.style.width = `${{effectiveWidth}}px`;
            img.style.height = `${{effectiveHeight}}px`;

            const map = document.getElementsByName('plot_map')[0];
            if (map) {{
                const areas = map.getElementsByTagName('area');
                for (const area of areas) {{
                    const originalCoords = area.getAttribute('data-coords').split(',');
                    const x = Number(originalCoords[0]) * effectiveScale + offsetX;
                    const y = Number(originalCoords[1]) * effectiveScale + offsetY;
                    const radius = Number(originalCoords[2]) * effectiveScale;
                    area.coords = `${{Math.round(x)}},${{Math.round(y)}},${{Math.round(radius)}}`;
                }}
            }}
            {svg_block}
        }}

        function resizeMap() {{
            applyPlotLayout();
        }}

        function zoomAt(clientX, clientY, deltaY) {{
            const surface = getPlotSurface();
            if (!surface) {{
                return;
            }}

            const layout = computePlotLayout(surface);
            if (!layout) {{
                return;
            }}

            const rect = surface.getBoundingClientRect();
            const mx = clientX - rect.left;
            const my = clientY - rect.top;
            const ix = (mx - layout.offsetX) / layout.effectiveScale;
            const iy = (my - layout.offsetY) / layout.effectiveScale;
            const factor = deltaY < 0 ? ZOOM_STEP : 1 / ZOOM_STEP;
            const newLevel = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, plotZoom.level * factor));
            if (newLevel === plotZoom.level) {{
                return;
            }}

            plotZoom.level = newLevel;
            if (plotZoom.level === ZOOM_MIN) {{
                plotZoom.panX = 0;
                plotZoom.panY = 0;
            }} else {{
                const base = computeBaseLayout(surface);
                if (!base) {{
                    return;
                }}
                const newEffectiveScale = base.scale * plotZoom.level;
                plotZoom.panX = mx - base.offsetX - ix * newEffectiveScale;
                plotZoom.panY = my - base.offsetY - iy * newEffectiveScale;
            }}
            applyPlotLayout();
        }}

        function resetZoom() {{
            plotZoom.level = ZOOM_MIN;
            plotZoom.panX = 0;
            plotZoom.panY = 0;
            applyPlotLayout();
        }}

        function blockPreviewPanelWheel() {{
            const previewPanel = document.getElementById('preview_panel');
            if (!previewPanel) {{
                return;
            }}
            previewPanel.addEventListener('wheel', (event) => {{
                if (event.ctrlKey) {{
                    event.stopPropagation();
                }}
            }}, {{ capture: true }});
        }}

        function setupPlotZoomInteractions() {{
            if (plotZoomInteractionsReady || isEmbeddedPreview()) {{
                return;
            }}
            const surface = getPlotSurface();
            if (!surface) {{
                return;
            }}
            plotZoomInteractionsReady = true;
            blockPreviewPanelWheel();

            surface.addEventListener('wheel', (event) => {{
                if (!event.ctrlKey || !surface.contains(event.target)) {{
                    return;
                }}
                event.preventDefault();
                zoomAt(event.clientX, event.clientY, event.deltaY);
            }}, {{ passive: false }});

            surface.addEventListener('dblclick', (event) => {{
                event.preventDefault();
                resetZoom();
            }});

            surface.addEventListener('mousedown', (event) => {{
                const canPan = plotZoom.level > ZOOM_MIN
                    && (event.button === 1 || (event.button === 0 && event.shiftKey));
                if (!canPan) {{
                    return;
                }}
                event.preventDefault();
                panState = {{
                    startX: event.clientX,
                    startY: event.clientY,
                    panX: plotZoom.panX,
                    panY: plotZoom.panY,
                }};
                surface.classList.add('panning');
            }});

            window.addEventListener('mousemove', (event) => {{
                if (!panState) {{
                    return;
                }}
                plotZoom.panX = panState.panX + (event.clientX - panState.startX);
                plotZoom.panY = panState.panY + (event.clientY - panState.startY);
                applyPlotLayout();
            }});

            const endPan = () => {{
                if (!panState) {{
                    return;
                }}
                panState = null;
                surface.classList.remove('panning');
            }};
            window.addEventListener('mouseup', endPan);
            window.addEventListener('blur', endPan);
        }}

        function initMap() {{
            const img = document.getElementById('plot_image');
            const run = () => requestAnimationFrame(() => {{
                resetZoom();
                applyPlotLayout();
                setupPlotZoomInteractions();
                if (!hotspotInteractionsReady && typeof setupHotspotInteractions === 'function') {{
                    hotspotInteractionsReady = true;
                    setupHotspotInteractions();
                }}
            }});

            if (img.complete && img.naturalWidth > 0) {{
                run();
            }} else {{
                img.addEventListener('load', run, {{ once: true }});
            }}
        }}

        window.addEventListener('load', initMap);
        window.addEventListener('resize', resizeMap);

        if (typeof ResizeObserver !== 'undefined') {{
            window.addEventListener('load', () => {{
                const surface = getPlotSurface();
                if (!surface) {{
                    return;
                }}
                const observer = new ResizeObserver(() => resizeMap());
                observer.observe(surface);
            }});
        }}"""


def build_classic_hotspot_js() -> str:
    """Build JavaScript for classic new-tab mode with SVG hotspot clicks."""
    return """
        function setupHotspotInteractions() {
            const overlay = document.getElementById('hotspot_overlay');
            if (overlay) {
                overlay.addEventListener('click', (event) => {
                    const marker = event.target.closest('.hotspot-marker');
                    if (!marker) {
                        return;
                    }
                    event.preventDefault();
                    window.open(marker.dataset.src, '_blank', 'noopener,noreferrer');
                });
            }
        }"""


def build_preview_js(auto_layout: bool, *, resizable: bool = True) -> str:
    """Build JavaScript for side-panel preview mode."""
    body_active_class = (
        "document.body.classList.add('preview-active');"
        if auto_layout
        else ""
    )
    body_inactive_class = (
        "document.body.classList.remove('preview-active');"
        if auto_layout
        else ""
    )

    splitter_js = ""
    if auto_layout and resizable:
        splitter_show = """
            const splitter = document.getElementById('layout_splitter');
            if (splitter) {
                splitter.hidden = false;
                splitter.setAttribute('aria-hidden', 'false');
            }
            initSplitter();"""
        splitter_hide = """
            const splitter = document.getElementById('layout_splitter');
            if (splitter) {
                splitter.hidden = true;
                splitter.setAttribute('aria-hidden', 'true');
            }"""
        splitter_js = f"""
        let splitterInitialized = false;

        function initSplitter() {{
            if (splitterInitialized) {{
                return;
            }}
            const splitter = document.getElementById('layout_splitter');
            const layout = document.querySelector('.layout');
            if (!splitter || !layout || layout.dataset.resizable !== 'true') {{
                return;
            }}
            splitterInitialized = true;
            let dragging = false;

            splitter.addEventListener('mousedown', (event) => {{
                dragging = true;
                splitter.classList.add('dragging');
                document.body.style.userSelect = 'none';
                event.preventDefault();
            }});

            window.addEventListener('mousemove', (event) => {{
                if (!dragging) {{
                    return;
                }}
                const rect = layout.getBoundingClientRect();
                const ratio = (event.clientX - rect.left) / rect.width;
                const clamped = Math.min(0.85, Math.max(0.25, ratio));
                layout.style.setProperty('--plot-width', `${{(clamped * 100).toFixed(2)}}%`);
                resizeMap();
            }});

            window.addEventListener('mouseup', () => {{
                if (!dragging) {{
                    return;
                }}
                dragging = false;
                splitter.classList.remove('dragging');
                document.body.style.userSelect = '';
                resizeMap();
            }});
        }}"""
        open_splitter = splitter_show
        close_splitter = splitter_hide
    else:
        splitter_js = ""
        open_splitter = ""
        close_splitter = ""

    return f"""
        let currentPreviewUrl = null;
        let currentPreviewIndex = null;
        let previewControlsBound = false;
        {splitter_js}

        function basename(path) {{
            const parts = path.split(/[\\\\/]/);
            return parts[parts.length - 1] || path;
        }}

        function hideAllPreviewMedia() {{
            document.querySelectorAll('.preview-media').forEach((element) => {{
                element.hidden = true;
            }});
        }}

        function openPreviewInNewTab() {{
            if (currentPreviewUrl) {{
                window.open(currentPreviewUrl, '_blank', 'noopener,noreferrer');
            }}
        }}

        function setActiveHotspot(index) {{
            document.querySelectorAll('.hotspot-marker').forEach((marker) => {{
                marker.classList.toggle('active', Number(marker.dataset.index) === index);
            }});
        }}

        function attachIframeClickHandler(iframe) {{
            iframe.addEventListener('load', () => {{
                try {{
                    iframe.contentWindow.document.addEventListener('click', (event) => {{
                        event.preventDefault();
                        openPreviewInNewTab();
                    }});
                    iframe.contentWindow.document.body.style.cursor = 'pointer';
                }} catch (error) {{
                    // Ignore cross-origin documents that cannot be accessed.
                }}
            }});
        }}

        function showPreviewMedia(url, mediaType) {{
            const image = document.getElementById('preview_image');
            const video = document.getElementById('preview_video');
            const iframe = document.getElementById('preview_iframe');
            const fallback = document.getElementById('preview_fallback');
            const fallbackLink = document.getElementById('preview_fallback_link');

            hideAllPreviewMedia();
            video.pause();

            if (mediaType === 'image') {{
                image.src = url;
                image.hidden = false;
                image.style.cursor = 'pointer';
                image.onclick = openPreviewInNewTab;
                return;
            }}
            if (mediaType === 'video') {{
                video.src = url;
                video.hidden = false;
                video.load();
                return;
            }}
            if (mediaType === 'html' || mediaType === 'pdf') {{
                iframe.src = url;
                iframe.hidden = false;
                return;
            }}

            fallback.hidden = false;
            fallbackLink.href = url;
            fallbackLink.textContent = basename(url);
        }}

        function handleHotspotClick(event, src, mediaType, index) {{
            event.preventDefault();
            if (event.ctrlKey || event.metaKey) {{
                window.open(src, '_blank', 'noopener,noreferrer');
                return;
            }}
            openPreview(src, mediaType, index);
        }}

        function openPreview(url, mediaType, index) {{
            const panel = document.getElementById('preview_panel');
            const filename = document.getElementById('preview_filename');
            const iframe = document.getElementById('preview_iframe');

            currentPreviewUrl = url;
            currentPreviewIndex = index;
            filename.textContent = basename(url);
            filename.title = url;
            showPreviewMedia(url, mediaType);
            panel.classList.add('visible');
            setActiveHotspot(index);
            attachIframeClickHandler(iframe);
            {open_splitter}
            {body_active_class}
            requestAnimationFrame(() => {{
                requestAnimationFrame(resizeMap);
            }});
        }}

        function closePreview() {{
            const panel = document.getElementById('preview_panel');
            const video = document.getElementById('preview_video');
            const iframe = document.getElementById('preview_iframe');

            panel.classList.remove('visible');
            video.pause();
            iframe.src = 'about:blank';
            hideAllPreviewMedia();
            currentPreviewUrl = null;
            currentPreviewIndex = null;
            setActiveHotspot(-1);
            {close_splitter}
            {body_inactive_class}
            requestAnimationFrame(resizeMap);
        }}

        function bindPreviewControls() {{
            if (previewControlsBound) {{
                return;
            }}
            previewControlsBound = true;
            document.getElementById('preview_open_tab').addEventListener('click', openPreviewInNewTab);
            document.getElementById('preview_close').addEventListener('click', closePreview);
        }}

        function setupHotspotInteractions() {{
            bindPreviewControls();

            const overlay = document.getElementById('hotspot_overlay');
            if (overlay) {{
                overlay.addEventListener('click', (event) => {{
                    const marker = event.target.closest('.hotspot-marker');
                    if (!marker) {{
                        return;
                    }}
                    handleHotspotClick(
                        event,
                        marker.dataset.src,
                        marker.dataset.mediaType,
                        Number(marker.dataset.index)
                    );
                }});
            }}

            document.querySelectorAll('area.preview-hotspot').forEach((area) => {{
                area.addEventListener('click', (event) => {{
                    handleHotspotClick(
                        event,
                        area.dataset.src,
                        area.dataset.mediaType,
                        Number(area.dataset.index)
                    );
                }});
            }});
        }}"""


def build_html_page(
    title: str,
    image_filename: str,
    zones_html: str,
    hotspots: list[dict],
    fig_width_px: int,
    fig_height_px: int,
    *,
    iframe_preview: IframePreview | None = None,
    theme: Theme | None = None,
    show_hotspots: bool = True,
) -> str:
    """Build the full responsive HTML page."""
    if theme is None:
        theme = Theme()

    safe_title = html.escape(title, quote=True)
    safe_image_filename = html.escape(image_filename, quote=True)

    container_width = (
        iframe_preview.plot_width
        if iframe_preview is not None
        else _DEFAULT_CONTAINER_WIDTH
    )

    preview_css = ""
    preview_js = ""
    body_classes = body_theme_class(theme)
    layout_open = ""
    layout_close = ""
    svg_overlay = ""

    if show_hotspots:
        svg_overlay = _HOTSPOT_OVERLAY_HTML

    container_css = f"""
        body {{
            margin: 0;
            padding: 0;
            background-color: var(--bg);
            color: var(--text);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{
            position: relative;
            width: {container_width};
            max-width: 1600px;
        }}
        body:not(.iframe-preview-mode) .plot-surface {{
            aspect-ratio: {fig_width_px} / {fig_height_px};
        }}
        #plot_image {{
            position: absolute;
            display: block;
            border: none;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            background: var(--surface);
        }}
        .plot-surface.panning {{
            cursor: grabbing;
        }}
        .plot-surface.panning .hotspot-marker {{
            cursor: grabbing;
        }}
        {_hotspot_css(show_hotspots)}"""

    if iframe_preview is not None:
        body_classes += " iframe-preview-mode"
        auto_layout = uses_auto_preview_layout(iframe_preview)

        if auto_layout:
            preview_css = build_auto_preview_css(iframe_preview)
            panel_class = "preview-panel"
            plot_pct = iframe_preview.initial_plot_ratio * 100
            resizable_attr = "true" if iframe_preview.resizable else "false"
            layout_open = (
                f'<div class="layout" style="--plot-width: {plot_pct:.2f}%;" '
                f'data-resizable="{resizable_attr}">'
            )
            splitter_html = (
                PREVIEW_SPLITTER_HTML if iframe_preview.resizable else ""
            )
            layout_close = splitter_html + PREVIEW_PANEL_HTML.format(
                panel_class=panel_class
            )
            preview_js = build_preview_js(
                auto_layout, resizable=iframe_preview.resizable
            )
        else:
            preview_css = build_fixed_preview_css(iframe_preview, container_width)
            panel_class = "preview-panel-fixed"
            layout_open = '<div class="layout">'
            layout_close = PREVIEW_PANEL_HTML.format(panel_class=panel_class)
            preview_js = build_preview_js(auto_layout, resizable=False)
    elif show_hotspots:
        preview_js = build_classic_hotspot_js()

    theme_css = build_theme_css(theme)
    resize_js = build_resize_map_js(
        fig_width_px,
        fig_height_px,
        hotspots,
        show_hotspots=show_hotspots,
        iframe_preview=iframe_preview is not None,
    )

    body_class_attr = f' class="{body_classes.strip()}"' if body_classes.strip() else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="color-scheme" content="light dark">
    <title>{safe_title}</title>
    <style>
        {theme_css}
        {container_css}
        {preview_css}
    </style>
</head>
<body{body_class_attr}>
    {layout_open}
    <div class="container">
        <div class="plot-surface" id="main_plot_surface">
            <img src="./{safe_image_filename}" usemap="#plot_map" id="plot_image" alt="{safe_title}">
            {svg_overlay}
            <map name="plot_map">
{zones_html}
            </map>
        </div>
    </div>{layout_close}

    <script>
        {resize_js}
        {preview_js}
    </script>
</body>
</html>
"""
