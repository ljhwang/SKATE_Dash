"""Use this app to get your local host URL and port number for testing your plotly figures in a Dash app."""

from dash import Dash, html

app = Dash()

# Requires Dash 2.17.0 or later
app.layout = [html.Div(children='Hello World')]

if __name__ == '__main__':
    app.run(debug=True)
