import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State, callback_context
from helpers_data import (
    df_renamer, df_dropper,
    df_persona_stream_cleaner, df_melt_ratings
)
from helpers_plotly import (
    px_radar
)

# app set-up
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = 'expose skills matrix'
server = app.server

# load the data
df = (
    pd.read_excel('data/Expose_Skills_Matrix_Master_Current.xlsx', sheet_name='Ratings')
    .pipe(df_renamer)
    .pipe(df_dropper)
    .pipe(df_persona_stream_cleaner)
    .pipe(df_melt_ratings)
)

print(df.head())

# dropdowns
person_selector = dbc.Select(id='person_selector', options=df['platform_area_categories'].unique())
person_selector_2 = dbc.Select(id='person_selector_2', options=df['consultant_name'].unique())

# skills graph
test_graph = dcc.Graph(
    id='my_graph',
    config={
        'displayModeBar': False,
        'scrollZoom' : False,
        'staticPlot' : True
        },
    # figure=px_radar()
)


# application layout
app.layout = dbc.Container([
    test_graph,
    person_selector,
    person_selector_2
], fluid=True)

@app.callback(
    Output('my_graph', 'figure'),
    Input('person_selector', 'value'),
    Input('person_selector_2', 'value')
)
def update_graph(person_selector_value, person_select_value_2):
    data = (
        df
        .query('platform_area_categories == @person_selector_value')
        .query('consultant_name == @person_select_value_2')
        .query('skill_rating > 0')
    )
    return px_radar(data, r='skill_rating', theta='technology')

# uncomment below for development and debugging
if __name__ == '__main__':
    app.run_server(port='8051', host='0.0.0.0', debug=True)
