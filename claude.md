# SKATE Dash — Project Context for Claude

## Project Overview

SKATE Dash is an interactive seismic data visualization dashboard built with Plotly and Dash. It displays seismogram images (PNG) as a background layer with overlaid GeoJSON features — meanlines, segments, and regions of interest (ROIs) — that can be toggled on/off in the browser UI. A statistics panel computes and visualizes slope and y-position distributions for meanlines.

## Tech Stack

- **Language:** Python 3.8
- **Web framework:** Dash (Plotly)
- **Visualization:** Plotly
- **Data:** Pandas, PyYAML, GeoJSON
- **Image processing:** Pillow (PIL)
- **UI components:** dash-bootstrap-components
- **Colormaps:** Fabio Crameri scientific colormaps (bundled in `style/scicolorscales.py`)
- **Environment manager:** Conda (`dash_app_env`)

## How to Run

```bash
conda activate dash_app_env
python main.py
```

Opens at `http://127.0.0.1:8050/`.

`app.py` is a minimal standalone test app for verifying the Dash setup.

## Project Structure

```
SKATE dash/
├── main.py               # Entry point — loads config, wires data + layout
├── app.py                # Minimal Dash smoke test
├── config.yml            # All data paths, colormaps, and layer properties
├── source/
│   ├── plot_figure.py    # Main dashboard layout + layer toggle callbacks
│   ├── plot_image.py     # Loads background seismogram PNG via PIL
│   ├── plot_meanlines.py # Renders GeoJSON meanlines with colormaps
│   ├── plot_segments.py  # Renders GeoJSON segments with ID-based coloring
│   ├── plot_roi.py       # Renders GeoJSON ROI polygons
│   ├── stats_meanlines.py# Computes slopes, y-distances; generates histograms
│   └── test.py           # Development scratch file
├── style/
│   ├── scicolorscales.py # Fabio Crameri colormap library
│   └── colorscales_test.py
├── test_data/
│   ├── meanlines.json
│   ├── segments.json
│   ├── roi.json
│   └── intersections.json
└── asset/                # Static assets (seismogram images, etc.)
```

## Configuration

All data paths and visual styling live in `config.yml`. Key fields:

```yaml
image:
  infile: path/to/seismogram.png
  display_scale: 0.2   # browser display scaling
  opacity: 0.5
meanlines:
  infile: test_data/meanlines.json
  colormap: roma       # scientific colormap name
  line_width: 2
  flip_y: true         # reflect y-coordinates to match image origin
  opacity: 1.0
segment:
  infile: test_data/segments.json
  colormap: broc
roi:
  infile: test_data/roi.json
  colormap: cork
```

## Data Formats

All vector data is **GeoJSON**:

- **Meanlines / Segments:** `LineString` features with pixel coordinates
- **ROI:** `Polygon` feature defining a rectangular region
- Feature `id` fields are used for coloring and identification

Example feature:
```json
{
  "type": "Feature",
  "id": 0,
  "geometry": {
    "type": "LineString",
    "coordinates": [[0, 1112], [8654, 1112]]
  },
  "properties": {}
}
```

## Architecture Notes

- **Layered rendering:** background image → meanlines → segments → ROI; each layer is independently toggleable via a UI checklist
- **Config-driven:** no hardcoded paths or styles; everything flows from `config.yml`
- **Coordinate system:** pixel-based; optional y-axis flip via `flip_y: true` in config to match image origin
- **Statistics:** meanline slopes computed via `numpy.polyfit`; y-position distributions analyzed at x=0 and at the rightmost x; results shown as interactive Plotly histograms

## Code Conventions

Defined in `.github/instructions/code-style.instructions.md` and applied to all `*.py` files:

- **PEP 8** — 4-space indentation, 79-character line limit
- **Type hints** required on all function parameters and return values
- **Google-style docstrings** for all public modules, classes, and functions
- **Naming:** `snake_case` for functions/variables, `CamelCase` for classes, `UPPER_CASE` for constants
- **Imports:** stdlib → third-party → local, no wildcard imports
- **Strings:** f-strings only
- **Exceptions:** always catch specific exception types, never bare `except:`
- **Defaults:** no mutable default arguments; use `None` and assign inside the function
