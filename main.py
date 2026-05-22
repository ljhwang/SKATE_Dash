"""Entry point for the SKATE Dash application. Loads config and renders plots."""


import yaml
import source.plot_image as plot_image
import source.plot_meanlines as plot_meanlines
import source.stats_meanlines as stats_meanlines
import source.plot_figure as plot_figure
import source.plot_segments as plot_segments
import source.plot_roi as plot_roi
import os
import sys

# Use a bootstrap theme for better styling 
# https://www.dash-bootstrap-components.com/docs/quickstart/

# app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN])

try:
    with open("config.yml", 'r') as file:
        config_data = yaml.safe_load(file)
        print("Config data loaded from config.yml:")
        print(config_data)
        print("Checking for input files...")

        # List of required input files
        input_files = [
            config_data['image']['infile'],
            config_data['meanlines']['infile'],
            config_data.get('segment', {}).get('infile'),
            # config_data.get('intersections', {}).get('infile'),
        ]

        missing_files = [f for f in input_files if not (f and os.path.exists(f))]
        if missing_files:
            print(f"Error: The following input files do not exist: {missing_files}")
            sys.exit(1)

#Create the image layer and the meanlines layer (and segments, roi, etc.) and pass to the plot_figure function to create the Dash app
        image = plot_image.pimage(
            infile=config_data['image']['infile']
        )

        meanlines_fig = plot_meanlines.pmeanlines(
            infile=config_data['meanlines']['infile'],
            colormap=config_data['meanlines']['colormap'],
            verbose=config_data['meanlines']['verbose'],
            line_width=config_data['meanlines'].get('line_width', 2),
            line_dash=config_data['meanlines'].get('line_dash', 'solid'),
            opacity=config_data['meanlines'].get('opacity', 1.0),
            show_markers=config_data['meanlines'].get('show_markers', True),
            flip_y=config_data['meanlines'].get('flip_y', False),
            image_height=image.size[1] if image is not None else None
        )
    
        # Load meanlines as DataFrame and compute all stats/figures
        meanlines_df = stats_meanlines.load_meanlines_dataframe(config_data['meanlines']['infile'])
        slopes_df, slopes_fig, dist_df, dist_fig, dist_xmax_df, dist_xmax_fig = stats_meanlines.compute_all_meanline_stats(meanlines_df)

        segments_fig = plot_segments.psegments(
            infile=config_data['segment']['infile'],
            colormap=config_data['segment']['colormap'],
            verbose=config_data['segment']['verbose'],
            line_width=config_data['segment'].get('line_width', 2),
            line_dash=config_data['segment'].get('line_dash', 'solid'),
            opacity=config_data['segment'].get('opacity', 1.0),
            show_markers=config_data['segment'].get('show_markers', False),
            flip_y=config_data['segment'].get('flip_y', False),
            image_height=image.size[1] if image is not None else None
        )

        roi_fig = plot_roi.proi(
            infile=config_data['roi']['infile'],
            line_width=config_data['roi'].get('line_width', 2),
            line_dash=config_data['roi'].get('line_dash', 'solid'),
            opacity=config_data['roi'].get('opacity', 1.0),
            show_markers=config_data['roi'].get('show_markers', False),
            flip_y=config_data['roi'].get('flip_y', False),
            image_height=image.size[1] if image is not None else None
        )

        # Scale the image to fit the plot into a browser window. True fix would be to use flex boxes.
        display_scale = config_data['image'].get('display_scale', 1.0)
        image_opacity = config_data['image'].get('opacity', 1.0)
        plot_figure.plot_figure_app(
            image=image,
            meanlines_fig=meanlines_fig,
            segments_fig=segments_fig,
            roi_fig=roi_fig,
            app_title='SKATE Dash - Visualization',
            display_scale=display_scale,
            image_opacity=image_opacity,
            slopes_fig=slopes_fig,
            dist_fig=dist_fig,
            dist_xmax_fig=dist_xmax_fig,
            segments_infile=config_data['segment']['infile'],
            segments_colormap=config_data['segment']['colormap'],
            segments_flip_y=config_data['segment'].get(
                'flip_y', False
            ),
            segments_image_height=(
                image.size[1] if image is not None else None
            ),
            segments_line_width=config_data['segment'].get(
                'line_width', 2
            ),
            segments_opacity=config_data['segment'].get(
                'opacity', 1.0
            ),
        )

except FileNotFoundError:
    print("The YAML file does not exist.")
except IOError:
    print("The file exists but is not accessible.") # Handles permission issues etc.
