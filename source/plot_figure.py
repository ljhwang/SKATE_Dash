"""Builds the main Dash figure layout and interactive features for SKATE Dash."""


from typing import Optional
from dash import Dash, html, dcc, Input, Output, State, no_update
import plotly.graph_objects as go
from PIL import Image
import numpy as np

import source.edit_segments as edit_segments


def plot_figure_app(
    image: Optional[Image.Image],
    meanlines_fig: go.Figure,
    segments_fig: go.Figure,
    roi_fig: go.Figure,
    app_title: str = 'SKATE Dash - Visualization',
    display_scale: float = 1.0,
    flip_y: bool = False,
    image_opacity: float = 1.0,
    slopes_fig: go.Figure = None,
    dist_fig: go.Figure = None,
    dist_xmax_fig: go.Figure = None,
    segments_infile: Optional[str] = None,
    segments_colormap: str = 'broc',
    segments_flip_y: bool = False,
    segments_image_height: Optional[int] = None,
    segments_line_width: int = 2,
    segments_opacity: float = 1.0,
):
    """
    Create and run a Dash app with the given image and meanlines figure.
    Adds layout and interactive features (checkboxes for layers).

    Args:
        image: PIL Image for the background (optional).
        meanlines_fig: Plotly Figure for meanlines.
        app_title: Title for the Dash app.
        segments_infile: Path to the segments GeoJSON file for editing.
        segments_colormap: Colormap name for segment rendering.
        segments_flip_y: If True, reflect segment y-coordinates.
        segments_image_height: Image height in pixels for y-flip.
        segments_line_width: Base line width for segments.
        segments_opacity: Opacity for segment traces.
    """
    app = Dash(__name__, assets_folder='../asset')

    # Layer keys must match those in plot_meanlines.py


    LAYER_IMAGE = "image"
    LAYER_MEANLINES = "meanlines"
    LAYER_SEGMENTS = "segments"
    LAYER_ROI = "roi"
    ALL_LAYERS = [
        {"label": "Seismogram", "value": LAYER_IMAGE},
        {"label": "Mean Lines", "value": LAYER_MEANLINES},
        {"label": "Segments", "value": LAYER_SEGMENTS},
        {"label": "ROI", "value": LAYER_ROI},
    ]
    default_layers = [layer["value"] for layer in ALL_LAYERS]

    # Do not scale traces; plot in original image pixel coordinates
    meanlines_traces = list(meanlines_fig.data)
    segments_traces = list(segments_fig.data)
    roi_traces = list(roi_fig.data)
    # Set axis ranges to match image pixel grid
    if image is not None:
        orig_width, orig_height = image.size
    else:
        orig_width = 800
        orig_height = 600
    # For display, scale the image, but axes always match original pixel grid
    width = int(orig_width * display_scale)
    height = int(orig_height * display_scale)
    xaxis_range = [0, orig_width]
    yaxis_range = [orig_height, 0] if flip_y else [0, orig_height]

    # Convert PIL image to numpy array for plotly
    def pil_to_uri(pil_img):
        import io, base64
        buf = io.BytesIO()
        pil_img.save(buf, format='PNG')
        data = base64.b64encode(buf.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{data}"

    # Load initial segment features for the editing store
    initial_features = None
    if segments_infile is not None:
        try:
            initial_features = edit_segments.load_features(
                segments_infile
            )
        except (FileNotFoundError, KeyError) as e:
            print(
                f"Warning: Could not load segments for editing: {e}"
            )
            initial_features = []

    # Try to get the image file name if available
    image_filename = getattr(image, 'filename', None)
    if image_filename is not None:
        import os
        image_filename = os.path.basename(image_filename)
    else:
        image_filename = 'No image loaded'

    app.layout = html.Div([
        html.H1(app_title),
        html.Div([
            html.H1(f"Image file: {image_filename}", style={'fontSize': '22px', 'fontWeight': 'bold', 'marginBottom': '20px'}),
            html.Label('Layers:', style={'fontWeight': 'bold'}),
            dcc.Checklist(
                id='layer-toggle',
                options=ALL_LAYERS,
                value=default_layers,
                inline=True,
                style={'marginBottom': '10px'}
            ),
            html.Label(
                'Image Opacity:',
                style={'fontWeight': 'bold'}
            ),
            html.Div(
                dcc.Slider(
                    id='image-opacity-slider',
                    min=0.0,
                    max=1.0,
                    step=0.05,
                    value=image_opacity,
                    marks={0: '0', 0.5: '0.5', 1: '1'},
                    tooltip={
                        'placement': 'bottom',
                        'always_visible': True
                    },
                ),
                style={'width': '300px', 'marginBottom': '10px'}
            ),
            html.Label(
                'Edit Segments:',
                style={'fontWeight': 'bold'}
            ),
            dcc.RadioItems(
                id='edit-mode',
                options=[
                    {'label': 'View', 'value': 'view'},
                    {'label': 'Draw Segment', 'value': 'draw'},
                    {'label': 'Erase Segment', 'value': 'erase'},
                ],
                value='view',
                inline=True,
                style={'marginBottom': '5px'},
            ),
            html.Div([
                html.Button(
                    'Erase Selected',
                    id='erase-btn',
                    style={'marginRight': '10px'},
                ),
                html.Button('Save Segments', id='save-btn'),
            ], style={'marginBottom': '5px'}),
            html.Div(
                id='edit-status',
                style={'color': 'green', 'marginBottom': '10px'}
            ),
        ]),
        dcc.Store(id='segments-store', data=initial_features),
        dcc.Store(id='selected-segment-ids', data=[]),
        dcc.Store(id='cursor-dummy'),
        dcc.Graph(
            id='main-graph',
            config={
                'modeBarButtonsToAdd': [
                    'drawline', 'select2d', 'lasso2d'
                ]
            },
            className='',
        ),
        html.Div([
            html.Div([
                dcc.Graph(id='slopes-graph', figure=slopes_fig, style={"width": "400px", "display": "inline-block", "verticalAlign": "top"}) if slopes_fig is not None else None
            ], style={"display": "inline-block", "verticalAlign": "top"}),
            html.Div([
                dcc.Graph(id='dist-graph', figure=dist_fig, style={"width": "400px", "display": "inline-block", "verticalAlign": "top"}) if dist_fig is not None else None
            ], style={"display": "inline-block", "verticalAlign": "top", "marginLeft": "40px"}),
            html.Div([
                dcc.Graph(id='dist-xmax-graph', figure=dist_xmax_fig, style={"width": "400px", "display": "inline-block", "verticalAlign": "top"}) if dist_xmax_fig is not None else None
            ], style={"display": "inline-block", "verticalAlign": "top", "marginLeft": "40px"})
        ], style={"width": "100%", "textAlign": "left"})
    ])

    app.clientside_callback(
        """
        function(editMode) {
            var cursor = (editMode === 'erase')
                ? "url('/assets/cursor-erase.svg') 0 0, default"
                : '';
            var graph = document.getElementById('main-graph');
            if (!graph) return null;
            var layers = graph.querySelectorAll('.drag');
            layers.forEach(function(el) {
                el.style.cursor = cursor;
            });
            return null;
        }
        """,
        Output('cursor-dummy', 'data'),
        Input('edit-mode', 'value'),
    )

    @app.callback(
        Output('main-graph', 'figure'),
        Input('layer-toggle', 'value'),
        Input('image-opacity-slider', 'value'),
        Input('segments-store', 'data'),
        Input('selected-segment-ids', 'data'),
        Input('edit-mode', 'value'),
    )
    def update_layers(
        active_layers,
        opacity,
        seg_features,
        selected_ids,
        edit_mode,
    ):
        fig = go.Figure()
        # Add background image if selected
        if LAYER_IMAGE in active_layers and image is not None:
            # Resize image for display_scale
            scaled_img = image.resize((width, height)) if display_scale != 1.0 else image
            fig.add_layout_image(dict(
                source=pil_to_uri(scaled_img),
                xref="x",
                yref="y",
                x=xaxis_range[0] if xaxis_range else 0,
                y=yaxis_range[1] if yaxis_range else 0,
                sizex=(xaxis_range[1] - xaxis_range[0]) if xaxis_range else 1,
                sizey=(yaxis_range[1] - yaxis_range[0]) if yaxis_range else 1,
                sizing="stretch",
                opacity=opacity,
                layer="below"
            ))
        # Add meanlines traces if selected
        if LAYER_MEANLINES in active_layers:
            for trace in meanlines_traces:
                fig.add_trace(trace)
        # Add segments traces if selected
        if LAYER_SEGMENTS in active_layers:
            if initial_features is not None:
                for trace in edit_segments.features_to_traces(
                    seg_features or [],
                    colormap=segments_colormap,
                    flip_y=segments_flip_y,
                    image_height=segments_image_height,
                    line_width=segments_line_width,
                    opacity=segments_opacity,
                    selected_ids=selected_ids,
                ):
                    fig.add_trace(trace)
            else:
                for trace in segments_traces:
                    fig.add_trace(trace)
        # Add ROI traces if selected
        if LAYER_ROI in active_layers:
            for trace in roi_traces:
                fig.add_trace(trace)
        dragmode_map = {
            'draw': 'drawline',
            'erase': 'pan',
        }
        dragmode = dragmode_map.get(edit_mode, 'pan')
        fig.update_layout(
            autosize=False,
            width=width,
            height=height,
            dragmode=dragmode,
            uirevision='main-graph',
            xaxis=dict(
                range=xaxis_range if xaxis_range else None,
                title='X (pixels)'
            ),
            yaxis=dict(
                range=yaxis_range if yaxis_range else None,
                title='Y (pixels)'
            ),
        )
        return fig

    @app.callback(
        Output('segments-store', 'data', allow_duplicate=True),
        Input('main-graph', 'relayoutData'),
        State('edit-mode', 'value'),
        State('segments-store', 'data'),
        prevent_initial_call=True,
    )
    def process_drawing(
        relayout_data: dict,
        edit_mode: str,
        features: list,
    ) -> list:
        """Convert a newly drawn line shape into a GeoJSON segment.

        Args:
            relayout_data: Graph relayout event data.
            edit_mode: Current edit mode value.
            features: Current segment features in the store.

        Returns:
            Updated features list, or no_update if nothing was drawn.
        """
        if edit_mode != 'draw' or not relayout_data:
            return no_update
        shapes = relayout_data.get('shapes')
        if not shapes:
            return no_update
        new_features = list(features) if features else []
        for shape in shapes:
            if shape.get('type') != 'line':
                continue
            x0 = shape['x0']
            y0 = shape['y0']
            x1 = shape['x1']
            y1 = shape['y1']
            if segments_flip_y and segments_image_height is not None:
                y0 = segments_image_height - y0
                y1 = segments_image_height - y1
            new_features = edit_segments.add_segment(
                new_features, x0, y0, x1, y1
            )
        return new_features

    @app.callback(
        Output('selected-segment-ids', 'data',
               allow_duplicate=True),
        Input('main-graph', 'selectedData'),
        State('edit-mode', 'value'),
        State('selected-segment-ids', 'data'),
        prevent_initial_call=True,
    )
    def update_selection_from_box(
        selected_data: dict,
        edit_mode: str,
        selected_ids: list,
    ) -> list:
        """Add all segment ids within a box/lasso selection.

        Args:
            selected_data: Graph selectedData event.
            edit_mode: Current edit mode value.
            selected_ids: Currently selected segment ids.

        Returns:
            Updated selected ids list, or no_update.
        """
        if edit_mode != 'erase':
            return no_update
        if not selected_data:
            return no_update
        points = selected_data.get('points', [])
        new_ids = [
            int(p['customdata'])
            for p in points
            if p.get('customdata') is not None
        ]
        current = list(selected_ids) if selected_ids else []
        merged = list(set(current) | set(new_ids))
        return merged

    @app.callback(
        Output('selected-segment-ids', 'data'),
        Input('main-graph', 'clickData'),
        State('edit-mode', 'value'),
        State('selected-segment-ids', 'data'),
        prevent_initial_call=True,
    )
    def update_selection(
        click_data: dict,
        edit_mode: str,
        selected_ids: list,
    ) -> object:
        """Toggle a segment's selection when clicked in erase mode.

        Args:
            click_data: Graph click event data.
            edit_mode: Current edit mode value.
            selected_ids: Currently selected segment ids.

        Returns:
            Updated selected ids list, or no_update.
        """
        if edit_mode != 'erase' or not click_data:
            return no_update
        points = click_data.get('points', [])
        if not points:
            return no_update
        segment_id = points[0].get('customdata')
        if segment_id is None:
            return no_update
        fid = int(segment_id)
        current = list(selected_ids) if selected_ids else []
        if fid in current:
            current.remove(fid)
        else:
            current.append(fid)
        return current

    @app.callback(
        Output('segments-store', 'data', allow_duplicate=True),
        Output('selected-segment-ids', 'data', allow_duplicate=True),
        Input('erase-btn', 'n_clicks'),
        State('selected-segment-ids', 'data'),
        State('segments-store', 'data'),
        prevent_initial_call=True,
    )
    def erase_segment_callback(
        n_clicks: int,
        selected_ids: list,
        features: list,
    ) -> tuple:
        """Remove all selected segments from the store.

        Args:
            n_clicks: Number of times the erase button has been clicked.
            selected_ids: Ids of the currently selected segments.
            features: Current segment features in the store.

        Returns:
            Updated features list and cleared selection, or no_update.
        """
        if not n_clicks or not selected_ids or not features:
            return no_update, no_update
        new_features = features
        for fid in selected_ids:
            new_features = edit_segments.erase_segment_by_id(
                new_features, fid
            )
        return new_features, []

    @app.callback(
        Output('edit-status', 'children'),
        Input('save-btn', 'n_clicks'),
        State('segments-store', 'data'),
        prevent_initial_call=True,
    )
    def save_segments_callback(
        n_clicks: int,
        features: list,
    ) -> str:
        """Write current segment features to disk.

        Args:
            n_clicks: Number of times the save button has been clicked.
            features: Current segment features in the store.

        Returns:
            Status message string.
        """
        if not n_clicks or not segments_infile:
            return no_update
        saved = features or []
        edit_segments.save_segments(saved, segments_infile)
        return f'Saved {len(saved)} segments to {segments_infile}'

    app.run(debug=True, use_reloader=False)
