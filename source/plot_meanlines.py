"""Reads a GeoJSON file of line segments and visualises them in a Dash app.

Each line segment is coloured based on its ID using a selected colorscale
from scicolorscales. An optional background image can be rendered beneath
the line traces. Layer visibility is controlled via a checklist in the UI.
"""

from typing import Any, Optional

from dash import Dash, html, dcc, Input, Output
from PIL import Image
import pandas as pd
import json
import plotly.graph_objects as go
import style.scicolorscales


def _build_figure(
    df: pd.DataFrame,
    colormap: str,
    verbose: bool,
    extent: tuple[float, float, float, float],
    img_width: Optional[int] = None,
    img_height: Optional[int] = None,
    line_width: int = 2,
    line_dash: str = 'solid',
    opacity: float = 1.0,
    show_markers: bool = True,
    flip_y: bool = False,
    image_height: int = None,
) -> go.Figure:
    """Build a Plotly figure for the given active layers.

    Args:
        df: DataFrame of line segment features.
        colormap: Name of a colorscale in style.scicolorscales.
        verbose: If True, annotate each line with its ID.
        extent: (x_min, x_max, y_min, y_max) coordinate bounds.
        img_width: Pixel width of the source image.
        img_height: Pixel height of the source image.

    Returns:
        A Plotly Figure with the requested layers rendered.
    """
    fig = go.Figure()
    x_min, x_max, y_min, y_max = extent

    # Only plot mean lines (background handled elsewhere)
    line_ids = df['id'].values
    for idx, row in df.iterrows():
        coords = row['coordinates']
        x_coords = [point[0] for point in coords]
        y_coords = [point[1] for point in coords]
        if flip_y and image_height is not None:
            y_coords = [image_height - y for y in y_coords]

        max_x_idx = x_coords.index(max(x_coords))
        right_x = x_coords[max_x_idx]
        right_y = y_coords[max_x_idx]

        normalized_id = (
            (row['id'] - line_ids.min())
            / (line_ids.max() - line_ids.min() + 1)
        )
        line_color = get_color_from_scale(
            normalized_id,
            style.scicolorscales.__dict__[colormap]
        )

        mode = 'lines+markers' if show_markers else 'lines'
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode=mode,
            name=f'ID {row["id"]}',
            hovertext=[f"ID: {row['id']}"] * len(x_coords),
            hoverinfo='text',
            line=dict(width=line_width, color=line_color, dash=line_dash),
            opacity=opacity,
            showlegend=False
        ))

        if verbose:
            fig.add_annotation(
                x=right_x,
                y=right_y,
                text=str(row['id']),
                showarrow=False,
                xanchor='left',
                xshift=5,
                font=dict(size=9, color='black')
            )

    # Flip y-axis range if needed
    y_range = [y_min, y_max]
    if flip_y and image_height is not None:
        y_range = [image_height - y_min, image_height - y_max]
    fig.update_layout(
        autosize=False,
        width=img_width,
        height=img_height,
        xaxis=dict(range=[x_min, x_max]),
        yaxis=dict(range=y_range),
        xaxis_title='X Coordinate',
        yaxis_title='Y Coordinate',
        showlegend=True
    )

    return fig


def pmeanlines(
    infile: str,
    colormap: str,
    verbose: bool,
    line_width: int = 2,
    line_dash: str = 'solid',
    opacity: float = 1.0,
    show_markers: bool = True,
    flip_y: bool = False,
    image_height: int = None
) -> go.Figure:
    """Load GeoJSON line segments and return a Plotly figure.

    Args:
        infile: Path to the GeoJSON file containing line segment features.
        colormap: Name of a colorscale defined in style.scicolorscales.
        verbose: If True, annotate each line with its ID.

    Returns:
        Plotly Figure object for meanlines.
    """
    print(f"Meanlines: {infile}, Colormap: {colormap}, Verbose: {verbose}")

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

        # Compute coordinate extent once
        all_x: list[float] = [
            point[0]
            for row in df['coordinates']
            for point in row
        ]
        all_y: list[float] = [
            point[1]
            for row in df['coordinates']
            for point in row
        ]
        extent = (min(all_x), max(all_x), min(all_y), max(all_y))

        img_width = img_height = None

        # Build and return the figure (only mean lines)
        fig = _build_figure(
            df=df,
            colormap=colormap,
            verbose=verbose,
            extent=extent,
            img_width=img_width,
            img_height=img_height,
            line_width=line_width,
            line_dash=line_dash,
            opacity=opacity,
            show_markers=show_markers,
            flip_y=flip_y,
            image_height=image_height
        )
        return fig

    except FileNotFoundError:
        print("File does not exist.")
        return go.Figure()

    except IOError:
        print("File exists but is not accessible.")
        return go.Figure()


def get_color_from_scale(value: float, colorscale: list[Any]) -> str:
    """Get a hex color from a colorscale based on a normalised value.

    Args:
        value: Normalised position in the colorscale, between 0 and 1.
        colorscale: List of (position, color) tuples defining the scale.

    Returns:
        The hex or rgb color string nearest to the given value.
    """
    for i, (pos, color) in enumerate(colorscale):
        if value <= pos:
            if i == 0:
                return color
            prev_pos, prev_color = colorscale[i - 1]
            return color if (value - prev_pos) < (pos - value) else prev_color
    return colorscale[-1][1]


if __name__ == "__main__":
    print("Executing directly")
    pmeanlines(
        infile="test_data/meanlines.json",
        colormap="roma",
        verbose=True
    )
