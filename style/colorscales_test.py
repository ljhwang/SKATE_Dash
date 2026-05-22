"""Test heatmap rendering using scicolorscales.

Run inside the dash_app_env so plotly is available:
    conda activate dash_app_env && python colorscales_test.py
"""

import numpy as np
import plotly.graph_objects as go
from style.scicolorscales import oleron, roma, tofino

# generate some sample data
z = np.random.rand(10, 10)

fig = go.Figure(data=go.Heatmap(z=z, colorscale=oleron))
fig.update_layout(title='Test heatmap with scicolorscales')

# if you want to upload to plotly cloud (deprecated API), comment out the line below
# py.plot(fig, filename='colorscale-test')

fig.show()  # open in browser / renderer

