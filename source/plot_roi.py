"""Reads a GeoJSON file of ROIs and returns a Plotly figure for SKATE Dash visualization."""

from typing import Optional
from PIL import Image
import pandas as pd
import json
import plotly.graph_objects as go
import style.scicolorscales

def proi(
    infile: str,
    colormap: str = 'acton',  # Default colormap, not used for boxes but for future
    verbose: bool = False,
    line_width: int = 2,
    line_dash: str = 'solid',
    opacity: float = 1.0,
    show_markers: bool = False,
    flip_y: bool = False,
    image_height: int = None
) -> go.Figure:
    """
    Load GeoJSON ROI data and return a Plotly figure with box shapes.
    Args:
        infile: Path to the GeoJSON file containing ROI features (Polygon or bbox).
        colormap: Name of a colorscale (not used for boxes, but for future).
        verbose: If True, annotate each ROI with its ID.
    Returns:
        Plotly Figure object for ROIs.
    """
    print(f"ROI: {infile}, Colormap: {colormap}, Verbose: {verbose}")
    try:
        with open(infile, 'r') as file:
            print(f"Reading data from {infile}...")
            data = json.load(file)
        # Support both FeatureCollection and single Feature
        if 'features' in data:
            features = data['features']
        else:
            features = [data]
        df = pd.DataFrame([{
            'id': feature.get('id', 0),
            'geometry_type': feature['geometry']['type'],
            'coordinates': feature['geometry']['coordinates']
        } for feature in features])
        all_x = [point[0] for row in df['coordinates'] for point in (row[0] if isinstance(row[0], list) else row)]
        all_y = [point[1] for row in df['coordinates'] for point in (row[0] if isinstance(row[0], list) else row)]
        extent = (min(all_x), max(all_x), min(all_y), max(all_y))
        img_width = img_height = None
        fig = go.Figure()
        # ROI layer (draw as boxes)
        for idx, row in df.iterrows():
            coords = row['coordinates']
            # Handle Polygon or bbox (GeoJSON Polygons are [ [ [x1, y1], [x2, y2], ... ] ])
            if row['geometry_type'] == 'Polygon':
                poly = coords[0]  # Outer ring
                x_coords = [p[0] for p in poly] + [poly[0][0]]
                y_coords = [p[1] for p in poly] + [poly[0][1]]
                if flip_y and image_height is not None:
                    y_coords = [image_height - y for y in y_coords]
                mode = 'lines+markers' if show_markers else 'lines'
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode=mode,
                    name=f'ROI {row["id"]}',
                    line=dict(width=line_width, color='red', dash=line_dash),
                    opacity=opacity,
                    showlegend=False
                ))
                if verbose:
                    centroid_x = sum(x_coords[:-1]) / len(x_coords[:-1])
                    centroid_y = sum(y_coords[:-1]) / len(y_coords[:-1])
                    if flip_y and image_height is not None:
                        centroid_y = image_height - centroid_y
                    fig.add_annotation(
                        x=centroid_x,
                        y=centroid_y,
                        text=str(row['id']),
                        showarrow=False,
                        font={"size": 9, "color": "red"}
                    )
        # Flip y-axis range if needed
        y_range = [extent[2], extent[3]]
        if flip_y and image_height is not None:
            y_range = [image_height - extent[2], image_height - extent[3]]
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
