"""Reads a GeoJSON file of segments and returns a Plotly figure for SKATE Dash visualization."""

from typing import Optional
from PIL import Image
import pandas as pd
import json
import plotly.graph_objects as go
import style.scicolorscales

def psegments(
    infile: str,
    colormap: str,
    verbose: bool,
    line_width: int = 2,
    line_dash: str = 'solid',
    opacity: float = 1.0,
    show_markers: bool = False,
    flip_y: bool = False,
    image_height: int = None
) -> go.Figure:
    """
    Load GeoJSON segment data and return a Plotly figure.
    Args:
        infile: Path to the GeoJSON file containing segment features.
        colormap: Name of a colorscale defined in style.scicolorscales.
        verbose: If True, annotate each segment with its ID.
    Returns:
        Plotly Figure object for segments.
    """
    print(f"Segments: {infile}, Colormap: {colormap}, Verbose: {verbose}")
    try:
        with open(infile, 'r') as file:
            print(f"Reading data from {infile}...")
            data = json.load(file)
        features = data['features']
        df = pd.DataFrame([{
            'id': feature['id'],
            'geometry_type': feature['geometry']['type'],
            'coordinates': feature['geometry']['coordinates']
        } for feature in features])
        print(f"DataFrame shape: {df.shape}")
        print(df.head())
        all_x = [point[0] for row in df['coordinates'] for point in row]
        all_y = [point[1] for row in df['coordinates'] for point in row]
        extent = (min(all_x), max(all_x), min(all_y), max(all_y))
        # Use image_height for y flipping if provided
        orig_height = image_height
        img_width = img_height = None
        LAYER_IMAGE = "image"
        LAYER_SEGMENTS = "segments"
        default_layers = [LAYER_IMAGE, LAYER_SEGMENTS]
        fig = go.Figure()
        # Segments layer
        line_ids = df['id'].values
        annotations = []
        for idx, row in df.iterrows():
            coords = row['coordinates']
            x_coords = [point[0] for point in coords]
            y_coords = [point[1] for point in coords]
            if flip_y and orig_height is not None:
                # Flip y based on image height: y' = orig_height - y
                y_coords = [orig_height - y for y in y_coords]
            max_x_idx = x_coords.index(max(x_coords))
            right_x = x_coords[max_x_idx]
            right_y = y_coords[max_x_idx]
            normalized_id = (
                (row['id'] - line_ids.min()) /
                (line_ids.max() - line_ids.min() + 1)
            )
            # Interpolate color from colorscale (list of [float, color])
            colorscale = style.scicolorscales.__dict__[colormap]
            stops = [stop[0] for stop in colorscale]
            for i, stop in enumerate(stops):
                if normalized_id <= stop:
                    if i == 0:
                        color = colorscale[0][1]
                    else:
                        color = colorscale[i][1]
                    break
            else:
                color = colorscale[-1][1]
            mode = 'lines+markers' if show_markers else 'lines'
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode=mode,
                name=f'Segment {row["id"]}',
                hovertext=[f"Segment: {row['id']}"] * len(x_coords),
                hoverinfo='text',
                line=dict(width=line_width, color=color, dash=line_dash),
                opacity=opacity,
                showlegend=False
            ))
            if verbose and len(df) < 200:
                annotations.append(dict(
                    x=right_x,
                    y=right_y,
                    text=str(row['id']),
                    showarrow=False,
                    xanchor='left',
                    xshift=5,
                    font={"size": 9, "color": "black"}
                ))
        if annotations:
            fig.update_layout(annotations=annotations)
        # Flip y-axis range if needed
        y_range = [extent[2], extent[3]]
        if flip_y and orig_height is not None:
            y_range = [orig_height - extent[2], orig_height - extent[3]]
        fig.update_layout(
            autosize=False,
            width=img_width,
            height=img_height,
            xaxis=dict(range=[extent[0], extent[1]]),
            yaxis=dict(range=y_range),
            xaxis_title='X Coordinate',
            yaxis_title='Y Coordinate',
            showlegend=False
        )
        return fig
    except FileNotFoundError:
        print("File does not exist.")
        return go.Figure()
    except IOError:
        print("File exists but is not accessible.")
        return go.Figure()
