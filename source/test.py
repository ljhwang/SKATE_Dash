"""Test script for visualising GeoJSON line segments with scicolorscales."""

from typing import Any

from dash import Dash, html, dcc, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from style.scicolorscales import oleron, roma, tofino


#read in some test data
verbose_id = True  # set to False to hide ID annotations on plot

infile = 'test_data/meanlines.json'

print(f"Reading data from {infile}...")

with open(infile, 'r') as file:
    data = json.load(file)

# Convert JSON data to DataFrame
features = data['features']
df = pd.DataFrame([{
    'id': feature['id'],
    'geometry_type': feature['geometry']['type'],
    'coordinates': feature['geometry']['coordinates']
} for feature in features])

print(f"DataFrame shape: {df.shape}")
print(df.head())

# Choose a colorscale from scicolorscales
colorscale_segment = roma  # options: oleron, roma, tofino
selected_colorscale = colorscale_segment

def get_color_from_scale(value: float, colorscale: list[Any]) -> str:
    """Get a hex color from a colorscale based on a normalised value.

    Args:
        value: Normalised position in the colorscale, between 0 and 1.
        colorscale: List of (position, color) tuples defining the scale.

    Returns:
        The hex or rgb color string nearest to the given value.
    """
    # Find the two closest points in the colorscale
    for i, (pos, color) in enumerate(colorscale):
        if value <= pos:
            if i == 0:
                return color
            prev_pos, prev_color = colorscale[i - 1]
            # Linear interpolation between colors (simplified - just use nearest)
            return color if (value - prev_pos) < (pos - value) else prev_color
    return colorscale[-1][1]

fig = go.Figure()

# Normalize line IDs to 0-1 range for color mapping
num_lines = len(df)
line_ids = df['id'].values

# Add each line segment to the plot
for idx, row in df.iterrows():
    coords = row['coordinates']
    x_coords = [point[0] for point in coords]
    y_coords = [point[1] for point in coords]
    
    # find rightmost point to place annotation to the right
    max_x_idx = x_coords.index(max(x_coords))
    right_x = x_coords[max_x_idx]
    right_y = y_coords[max_x_idx]
    
    # Get color for this line based on its ID
    normalized_id = (row['id'] - line_ids.min()) / (line_ids.max() - line_ids.min() + 1)
    line_color = get_color_from_scale(normalized_id, selected_colorscale)
    
    fig.add_trace(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='lines+markers',            # show a marker so hover works at line ends as well
        name=f'ID {row["id"]}',        # use the ID directly in legend name
        hovertext=[f"ID: {row['id']}"] * len(x_coords),
        hoverinfo='text',
        line=dict(width=2, color=line_color)
    ))
    # add annotation to the right of the line segment (only if verbose_id is True)
    if verbose_id:
        fig.add_annotation(
            x=right_x,
            y=right_y,
            text=str(row['id']),
            showarrow=False,
            xanchor='left',
            xshift=5,
            font=dict(size=9, color='black')
        )

# Update layout
fig.update_layout(
    title='Line Segments from GeoJSON',
    xaxis_title='X Coordinate',
    yaxis_title='Y Coordinate',
    showlegend=True
)

# Initialize the app
app = Dash(__name__)


# App layout
app.layout = html.Div([
    html.H1('SKATE Dash - Line Segments Visualization'),
    dcc.Graph(figure=fig)
])


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
