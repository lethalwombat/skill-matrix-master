import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State, callback_context

# app set-up
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = 'eMAS template builder'
server = app.server

# application layout
app.layout = dbc.Container([
    html.H1('hello world')
], fluid=True)

# uncomment below for development and debugging
if __name__ == '__main__':
    app.run_server(port='8051', host='0.0.0.0', debug=True)
