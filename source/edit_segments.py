"""Segment editing utilities for SKATE Dash.

Provides functions to add, erase, save, and render GeoJSON segment features
interactively from the Dash UI.
"""

import json
from typing import Optional

import plotly.graph_objects as go

import style.scicolorscales


def load_features(infile: str) -> list:
    """Load GeoJSON features from a FeatureCollection file.

    Args:
        infile: Path to the GeoJSON file.

    Returns:
        List of GeoJSON feature dicts.

    Raises:
        FileNotFoundError: If the file does not exist.
        KeyError: If the GeoJSON structure is missing the 'features' key.
    """
    with open(infile, 'r') as f:
        data = json.load(f)
    return data['features']


def add_segment(
    features: list,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
) -> list:
    """Add a new LineString segment to the features list.

    The new segment's id is one greater than the current maximum id,
    or 0 if there are no existing features.

    Args:
        features: Current list of GeoJSON feature dicts.
        x0: X coordinate of the start point (pixel space).
        y0: Y coordinate of the start point (pixel space).
        x1: X coordinate of the end point (pixel space).
        y1: Y coordinate of the end point (pixel space).

    Returns:
        New list with the new segment appended.
    """
    existing_ids = [f['id'] for f in features]
    next_id = max(existing_ids) + 1 if existing_ids else 0
    new_feature = {
        'type': 'Feature',
        'id': next_id,
        'geometry': {
            'type': 'LineString',
            'coordinates': [[x0, y0], [x1, y1]],
        },
        'properties': {},
    }
    return features + [new_feature]


def erase_segment_by_id(features: list, segment_id: int) -> list:
    """Remove a segment feature by its id.

    Args:
        features: Current list of GeoJSON feature dicts.
        segment_id: Id of the feature to remove.

    Returns:
        New list with the matching feature removed.
    """
    return [f for f in features if f['id'] != segment_id]


def save_segments(features: list, outfile: str) -> None:
    """Write segment features to a GeoJSON FeatureCollection file.

    Args:
        features: List of GeoJSON feature dicts to write.
        outfile: Destination file path.

    Raises:
        IOError: If the file cannot be written.
    """
    geojson = {
        'type': 'FeatureCollection',
        'features': features,
    }
    with open(outfile, 'w') as f:
        json.dump(geojson, f, indent=2)


def features_to_traces(
    features: list,
    colormap: str,
    flip_y: bool = False,
    image_height: Optional[int] = None,
    line_width: int = 2,
    opacity: float = 1.0,
    selected_ids: Optional[list] = None,
) -> list:
    """Convert GeoJSON segment features to a list of Plotly Scatter traces.

    Args:
        features: List of GeoJSON LineString feature dicts.
        colormap: Colormap name defined in style.scicolorscales.
        flip_y: If True, reflect y-coordinates: y_display = image_height - y.
        image_height: Height of the reference image in pixels.
        line_width: Base width of drawn lines in pixels.
        opacity: Line opacity (0–1).
        selected_ids: Ids of currently selected segments (highlighted
            with a fluorescent yellow dashed, thicker line).

    Returns:
        List of go.Scatter trace objects ready to add to a figure.
    """
    if not features:
        return []

    colorscale = style.scicolorscales.__dict__[colormap]
    ids = [f['id'] for f in features]
    id_min = min(ids)
    id_max = max(ids)

    traces = []
    for feature in features:
        fid = feature['id']
        coords = feature['geometry']['coordinates']
        x_coords = [p[0] for p in coords]
        y_coords = [p[1] for p in coords]

        if flip_y and image_height is not None:
            y_coords = [image_height - y for y in y_coords]

        normalized_id = (
            (fid - id_min) / (id_max - id_min + 1)
            if id_max > id_min
            else 0.5
        )
        stops = [s[0] for s in colorscale]
        color = colorscale[-1][1]
        for i, stop in enumerate(stops):
            if normalized_id <= stop:
                color = (
                    colorscale[i][1] if i > 0 else colorscale[0][1]
                )
                break

        SELECTED_COLOR = '#CCFF00'
        selected_set = set(selected_ids) if selected_ids else set()
        is_selected = fid in selected_set
        effective_color = SELECTED_COLOR if is_selected else color
        effective_width = line_width + 2 if is_selected else line_width
        line_dash = 'dash' if is_selected else 'solid'

        traces.append(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='lines+markers',
            name=f'Segment {fid}',
            customdata=[fid] * len(x_coords),
            hovertext=[f'Segment: {fid}'] * len(x_coords),
            hoverinfo='text',
            line=dict(
                width=effective_width,
                color=effective_color,
                dash=line_dash,
            ),
            marker=dict(size=6, opacity=0),
            opacity=opacity,
            showlegend=False,
        ))

    return traces
