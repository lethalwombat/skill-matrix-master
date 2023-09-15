import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
from random import choice
from helpers_dash import (
    heading, card_tab,
    html_label, dash_table_interactive,
    dash_table_simple
)
from helpers_data import (
    df_renamer, df_dropper,
    df_persona_stream_cleaner, df_melt_ratings,
    df_top_n_skills, df_filter_multiple,
    df_filter_multiple_simple
)
from helpers_plotly import (
    radar_comparison
)

# app set-up
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = 'éxpose Skills Matrix'
server = app.server

# top heading
top_heading = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Br(),
            heading('exposé Skills Matrix'),
        ], width=12)
    ])
], fluid=True)

# load the data
df = (
    pd.read_excel('data/Expose_Skills_Matrix_Master_Current.xlsx', sheet_name='Ratings')
    .pipe(df_renamer)
    .pipe(df_dropper)
    .pipe(df_persona_stream_cleaner)
    .pipe(df_melt_ratings)
)

# get options for the selectors
get_selector_options = lambda col : sorted(df[col].unique().tolist())

options_technologies = get_selector_options('technology')
options_names = get_selector_options('consultant_name')
options_streams = sorted(df['persona_stream'].explode().unique().tolist())
options_categories = get_selector_options('platform_area_categories')

# comparison tab inputs
comparison_tab_inputs = dbc.Container([
    dbc.Stack([
        html_label('Consultant 1'),
        dcc.Dropdown(options_names, choice(options_names), searchable=True, clearable=False, id='input_consultant_1'),
        html_label('Consultant 2'),
        dcc.Dropdown(options_names, choice(options_names), searchable=True, clearable=False, id='input_consultant_2'),
        html_label('Persona Stream'),
        dcc.Dropdown(options_streams, id='input_persona_stream', multi=True),
        html_label('Platform, Area or Categories'),
        dcc.Dropdown(options_categories, searchable=True, multi=True, id='input_categories'),
        html_label('Number of Ratings'),
        dbc.Input(type='number', min=5, max=10, value=5, id='input_n_ratings')
    ], gap=1)    
], fluid=True)

# comparison tab graph
comparison_tab_graph = dbc.Container([
    html.Div([
        dcc.Graph(
            id='comparison_graph',
            config={
                'staticPlot' : True
            }
        )
    ], id='comparison_graph_hide')
], fluid=True)

# comparison tab
comparison_tab = dbc.Container([
    dbc.Row([
        dbc.Col([
            comparison_tab_inputs
        ], width=3),
        dbc.Col([
            comparison_tab_graph
        ], width=9)
    ])
], fluid=True)

# search tab inputs
search_tab_inputs = dbc.Container([
    dbc.Stack([
        html_label('Technology'),
        dcc.Dropdown(options_technologies, searchable=True, clearable=True, multi=True, id='input_technology'),
        html_label('Minimum Rating'),
        dbc.Input(type='number', min=1, max=5, value=1, id='input_min_rating')
    ], gap=1)
], fluid=True)

# search tab table
search_tab_table = dbc.Container([
    dbc.Stack([
        html_label('Results'),
        html.Br(),
        html.Div([], id='search_table')
    ])
], fluid=True)

# search tab table counts
search_tab_table_counts = dbc.Container([
    dbc.Stack([
        html_label('Summary'),
        html.Br(),
        html.Div([
        ], id='search_table_counts')
    ])
], fluid=True)

# search tab
search_tab = dbc.Container([
    dbc.Row([
        dbc.Col([
            search_tab_inputs
        ], width=3),
        dbc.Col([
            search_tab_table
        ], width=6),
        dbc.Col([
            search_tab_table_counts
        ], width=3)
    ])
], fluid=True)

# # skills graph
# test_graph = dcc.Graph(
#     id='my_graph',
#     config={
#         'displayModeBar': False,
#         'scrollZoom' : False,
#         'staticPlot' : True
#         },
#     # figure=px_radar()
# )

# application layout
app.layout = dbc.Container([
    top_heading,
    dbc.Tabs(
        [
            card_tab(label='Search', content=search_tab, id='tab_search'),
            card_tab(label='Profiles', content=comparison_tab, id='tab_comparison'),
        ])
], fluid=True)

# comparison graph
@app.callback(
    Output('comparison_graph', 'figure'),
    Output('comparison_graph_hide', 'style'),
    Input('input_consultant_1', 'value'),
    Input('input_consultant_2', 'value'),
    Input('input_persona_stream', 'value'),
    Input('input_categories', 'value'),
    Input('input_n_ratings', 'value'),
)
def update_graph(
    input_consultant_1_value, input_consultant_2_value, 
    input_persona_stream_value, input_categories_value,
    input_n_ratings_value
    ):
    df_out = (
        df
        .pipe(df_filter_multiple, input_persona_stream_value, 'persona_stream') # filter by persona stream
        .pipe(df_filter_multiple, input_categories_value, 'platform_area_categories') # filter by platform area categories
        .pipe(df_top_n_skills, [input_consultant_1_value, input_consultant_2_value], input_n_ratings_value) # filter by consultants
    )
    graph_style = {'display' : 'block'}
    # if nothing found or all ratings are 0, then don't show
    if any([
        df_out.shape[0] == 0,
        df_out['skill_rating'].max() == 0
    ]):
        graph_style = {'display' : 'none'}
    df_out = df_out.drop(columns='persona_stream') # delete after
    return \
        radar_comparison(df_out, 'skill_rating', 'technology', 'consultant_name', [input_consultant_1_value, input_consultant_2_value]),\
        graph_style
        
    
@app.callback(
    Output('search_table', 'children'),
    Output('search_table_counts', 'children'),
    Input('input_technology', 'value'),
    Input('input_min_rating', 'value'),
)
def update_table(
    input_technology_value, input_min_rating_value
):
    # prevent from deleting min rating
    if input_min_rating_value is None:
        input_min_rating_value = 1

    # handle None for the counts table
    if input_technology_value is None:
        input_technology_value = []

    df_out = (
        df
        .pipe(df_filter_multiple_simple, input_technology_value, 'technology')
        .query('skill_rating >= @input_min_rating_value')
        .sort_values(by=['technology', 'skill_rating', 'consultant_name'], ascending=[True, False, True])
        [['consultant_name', 'skill_rating', 'technology']]
        .rename(columns={'consultant_name' : 'Name', 'skill_rating' : 'Rating', 'technology' : 'Technology'})
    )

    # group by rating
    df_out_counts = pd.DataFrame({
        'Rating' : [f'{input_min_rating_value} or higher'],
        'Consultants' : [df_out['Name'].nunique()],
        # 'Technologies' : [''.join(input_technology_value)]
        })
    return dash_table_interactive(df_out), dash_table_simple(df_out_counts)

# @app.callback(
#     Output('my_graph', 'figure'),
#     Input('person_selector', 'value'),
#     Input('person_selector_2', 'value')
# )
# def update_graph(person_selector_value, person_select_value_2):
#     data = (
#         df
#         .query('platform_area_categories == @person_selector_value')
#         .query('consultant_name == @person_select_value_2')
#         .query('skill_rating > 0')
#     )
#     return px_radar(data, r='skill_rating', theta='technology')

# uncomment below for development and debugging
if __name__ == '__main__':
    app.run_server(port='8051', host='0.0.0.0', debug=True)
