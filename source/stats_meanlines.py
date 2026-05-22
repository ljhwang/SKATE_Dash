def compute_all_meanline_stats(meanlines_df: pd.DataFrame):
    """
    Compute all statistics and figures for meanlines: slopes, distances at x=0, distances at xmax.
    Returns:
        slopes_df, slopes_fig, dist_df, dist_fig, dist_xmax_df, dist_xmax_fig
    """
    slopes_df = meanline_slopes(meanlines_df)
    slopes_fig = plot_slopes(slopes_df)
    dist_df = meanline_distances_at_x0(meanlines_df)
    dist_fig = plot_distances_at_x0(dist_df)
    dist_xmax_df = meanline_distances_at_xmax(meanlines_df)
    dist_xmax_fig = plot_distances_at_xmax(dist_xmax_df)
    return slopes_df, slopes_fig, dist_df, dist_fig, dist_xmax_df, dist_xmax_fig

def load_meanlines_dataframe(geojson_path: str) -> pd.DataFrame:
    """
    Load meanlines from a GeoJSON file into a DataFrame with columns: id, geometry_type, coordinates.
    Args:
        geojson_path: Path to the meanlines GeoJSON file.
    Returns:
        pd.DataFrame with columns: id, geometry_type, coordinates
    """
    import json
    with open(geojson_path, 'r') as f:
        meanlines_data = json.load(f)
    return pd.DataFrame([
        {
            'id': feature['id'],
            'geometry_type': feature['geometry']['type'],
            'coordinates': feature['geometry']['coordinates']
        }
        for feature in meanlines_data['features']
    ])

def meanline_distances_at_xmax(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the y-positions of each meanline at the right edge (max x for each line),
    then compute the distances between successive lines at that edge.
    Returns a DataFrame with columns: id, y_at_xmax, distance_to_next
    """
    y_at_xmax = []
    for idx, row in df.iterrows():
        coords = row['coordinates']
        x = np.array([pt[0] for pt in coords])
        y = np.array([pt[1] for pt in coords])
        if len(x) > 1:
            m, b = np.polyfit(x, y, 1)
            xmax = x.max()
            yx = m * xmax + b
        elif len(x) == 1:
            yx = y[0]
        else:
            yx = np.nan
        y_at_xmax.append({'id': row['id'], 'y_at_xmax': yx})
    y_df = pd.DataFrame(y_at_xmax).sort_values('y_at_xmax').reset_index(drop=True)
    y_df['distance_to_next'] = y_df['y_at_xmax'].shift(-1) - y_df['y_at_xmax']
    return y_df

def plot_distances_at_xmax(dist_df: pd.DataFrame) -> go.Figure:
    """
    Plot a histogram of the distances between successive meanlines at xmax.
    """
    valid_distances = dist_df['distance_to_next'].dropna()
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=valid_distances,
        marker_color='purple',
        name='Distance at xmax'
    ))
    mean_val = valid_distances.mean()
    median_val = valid_distances.median()
    fig.add_vline(x=mean_val, line_dash='dash', line_color='red', annotation_text=f"Mean: {mean_val:.2f}", annotation_position="top left")
    fig.add_vline(x=median_val, line_dash='dot', line_color='green', annotation_text=f"Median: {median_val:.2f}", annotation_position="top right")
    fig.update_layout(
        title='Histogram of Meanline Distances at xmax',
        xaxis_title='Distance',
        yaxis_title='Count',
        showlegend=False
    )
    return fig
def plot_distances_at_x0(dist_df: pd.DataFrame) -> go.Figure:
    """
    Plot a histogram of the distances between successive meanlines at x=0.
    """
    # Remove NaN (last distance is NaN)
    valid_distances = dist_df['distance_to_next'].dropna()
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=valid_distances,
        marker_color='orange',
        name='Distance at x=0'
    ))
    mean_val = valid_distances.mean()
    median_val = valid_distances.median()
    fig.add_vline(x=mean_val, line_dash='dash', line_color='red', annotation_text=f"Mean: {mean_val:.2f}", annotation_position="top left")
    fig.add_vline(x=median_val, line_dash='dot', line_color='green', annotation_text=f"Median: {median_val:.2f}", annotation_position="top right")
    fig.update_layout(
        title='Histogram of Meanline Distances at x=0',
        xaxis_title='Distance',
        yaxis_title='Count',
        showlegend=False
    )
    return fig
def meanline_distances_at_x0(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the y-positions of each meanline at x=0 (left edge),
    then compute the distances between successive lines at that edge.
    Returns a DataFrame with columns: id, y_at_x0, distance_to_next
    """
    y_at_x0 = []
    for idx, row in df.iterrows():
        coords = row['coordinates']
        x = np.array([pt[0] for pt in coords])
        y = np.array([pt[1] for pt in coords])
        # Interpolate/extrapolate to x=0 if possible
        if len(x) > 1:
            m, b = np.polyfit(x, y, 1)
            y0 = m * 0 + b
        elif len(x) == 1:
            y0 = y[0]
        else:
            y0 = np.nan
        y_at_x0.append({'id': row['id'], 'y_at_x0': y0})
    y_df = pd.DataFrame(y_at_x0).sort_values('y_at_x0').reset_index(drop=True)
    y_df['distance_to_next'] = y_df['y_at_x0'].shift(-1) - y_df['y_at_x0']
    return y_df



import pandas as pd
import numpy as np
import plotly.graph_objects as go

def meanline_slopes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the slope of each meanline in the DataFrame.
    Assumes 'coordinates' column contains a list of [x, y] pairs for each meanline.
    Returns a DataFrame with columns: id, slope
    """
    slopes = []
    for idx, row in df.iterrows():
        coords = row['coordinates']
        x = np.array([pt[0] for pt in coords])
        y = np.array([pt[1] for pt in coords])
        # Fit a line: y = m*x + b
        if len(x) > 1:
            m, _ = np.polyfit(x, y, 1)
        else:
            m = np.nan
        slopes.append({'id': row['id'], 'slope': m})
    return pd.DataFrame(slopes)

def plot_slopes(slopes_df: pd.DataFrame) -> go.Figure:
    """
    Plot a histogram of the meanline slopes.
    """
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=slopes_df['slope'],
        marker_color='royalblue',
        name='Slope'
    ))
    # Calculate mean and median
    mean_val = slopes_df['slope'].mean()
    median_val = slopes_df['slope'].median()
    # Add vertical lines for mean and median
    fig.add_vline(x=mean_val, line_dash='dash', line_color='red', annotation_text=f"Mean: {mean_val:.2f}", annotation_position="top left")
    fig.add_vline(x=median_val, line_dash='dot', line_color='green', annotation_text=f"Median: {median_val:.2f}", annotation_position="top right")
    fig.update_layout(
        title='Histogram of Meanline Slopes',
        xaxis_title='Slope',
        yaxis_title='Count',
        showlegend=False
    )
    return fig
