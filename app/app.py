import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
from random import choice
from helpers_dash import (
    heading, card_tab,
    html_label, html_label_center,
)
from helpers_data import (
    df_renamer, df_dropper,
    df_persona_stream_cleaner, df_melt_ratings,
    df_top_n_skills, df_filter_multiple,
    df_filter_multiple_simple
)
from helpers_plotly import (
    radar_single, radar_comparison
)

# app set-up
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX, dbc_css])
app.title = 'éxpose Skills Matrix'
server = app.server

# wrapper to style dcc componenets as dbc
style_dbc = lambda x : dbc.Container(x, className='dbc', fluid=True)
get_container = lambda x : dbc.Container(x, fluid=True)

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
options_relevance = get_selector_options('relevance')


# capabilities tab inputs
capabilities_tab_inputs = style_dbc([
    dbc.Stack([
        html_label('Persona Stream'),
        dcc.Dropdown(options_streams, id='input_persona_stream_capability', placeholder='Select one or many...', multi=True, style={'font-size' : '14px'}),
        html_label('Platform, Area or Categories'),
        dcc.Dropdown(options_categories, searchable=True, placeholder='Select one or many...', multi=True, id='input_categories_capability', style={'font-size' : '14px'}),
        html_label('Relevance'),
        # dcc.Dropdown(options_relevance, multi=True, id='input_relevance'),
        dbc.Checklist(options=options_relevance, id='input_relevance', style={'font-size' : '14px'}),
        html_label_center('< Rating >'),        
        # dbc.Input(type='number', min=1, max=5, value=1, id='input_min_rating_capability'),
        dcc.RangeSlider(min=1, max=5, step=1, value=[1, 5], id='input_min_rating_capability'),
        html_label_center('< Frequent — Rare >'),          
        dcc.RangeSlider(min=0, step=1, marks=None, id='input_capability_graph_slider')
    ], gap=1)
])

# capabilities tab graph
capabilities_tab_graph = dbc.Container([
    html_label('Consultants'),
    html.Div([
        dcc.Graph(
            id='capability_graph',
            config={
                'staticPlot' : True
            }
        )
    ], id='capability_graph_hide'),
    html.Div([
        html.Br(),
        html.Label('No consultants found. Please adjust your selection criteria.')
    ], id='capability_no_one_found', style={'display' : 'none'}),
], fluid=True, style={'text-align' : 'center'})

# capabilities tab
capabilities_tab = dbc.Container([
    dbc.Row([
        dbc.Col([
            capabilities_tab_inputs
        ], width=3),
        dbc.Col([
            capabilities_tab_graph,
        ], width=9)
    ])
], fluid=True)

# search tab inputs
search_tab_inputs = style_dbc([
    dbc.Stack([
        html_label('Technology'),
        dcc.Dropdown(options_technologies, searchable=True, clearable=True, placeholder='Select one or many...', multi=True, id='input_technology', style={'font-size' : '12px'}),
        html_label_center('< Rating >'),
        dcc.RangeSlider(min=1, max=5, step=1, value=[1, 5], id='input_min_rating_search')
    ], gap=1)
])

# search tab table
search_tab_table = dbc.Container([
    dbc.Stack([
        # html_label('Results'),
        html.Br(),
        html.Div([], id='search_table')
    ])
], fluid=True)

# search tab table counts
search_tab_table_counts = dbc.Container([
    dbc.Stack([
        # html_label('Summary'),
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

# comparison tab inputs
comparison_tab_inputs = style_dbc([
    dbc.Stack([
        html_label('Profile 1'),
        dcc.Dropdown(options_names, choice(options_names), searchable=True, clearable=False, id='input_consultant_1', style={'font-size' : '14px'}),
        html_label('Profile 2'),
        dcc.Dropdown(options_names, choice(options_names), searchable=True, clearable=False, id='input_consultant_2', style={'font-size' : '14px'}),
        html_label('Persona Stream'),
        dcc.Dropdown(options_streams, id='input_persona_stream', placeholder='Select one or many...', multi=True, style={'font-size' : '14px'}),
        html_label('Platform, Area or Categories'),
        dcc.Dropdown(options_categories, searchable=True, multi=True, placeholder='Select one or many...', id='input_categories', style={'font-size' : '14px'}),
        html_label_center('Show Ratings'),
        dcc.Slider(min=5, max=10, step=1, value=7, id='input_n_ratings')
    ], gap=1)    
])

# comparison tab graph
comparison_tab_graph = dbc.Container([
    html_label('Ratings'),
    html.Div([
        dcc.Graph(
            id='comparison_graph',
            config={
                'staticPlot' : True
            }
        )
    ], id='comparison_graph_hide'),
    html.Div([
        html.Br(),
        html.Label('No ratings found. Please adjust your selection criteria')
    ], id='comparison_no_one_found', style={'display' : 'block'})
], fluid=True, style={'text-align' : 'center'})

# comparison tab
comparison_tab = dbc.Container([
    dbc.Row([
        dbc.Col([
            comparison_tab_inputs
        ], width=3),
        dbc.Col([
            comparison_tab_graph
        ], width=9),
        # html.H2(id='tester')
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
            card_tab(label='Capabilities', content=capabilities_tab, id='tab_capabilities'),
            card_tab(label='Search', content=search_tab, id='tab_search'),
            card_tab(label='Profiles', content=comparison_tab, id='tab_comparison'),
        ])
], fluid=True)

# capability graph rangslider min and max values
@app.callback(
    Output('input_capability_graph_slider', 'max'),
    Output('input_capability_graph_slider', 'value'),
    Input('input_persona_stream_capability', 'value'),
    Input('input_categories_capability', 'value'),
    Input('input_relevance', 'value'),
    Input('input_min_rating_capability', 'value')
)
def update_slider_max(
    input_persona_stream_capability_value, input_categories_capability_value,
    input_relevance_value, input_min_rating_capability_value,
):
    min_rating = input_min_rating_capability_value[0]
    max_rating = input_min_rating_capability_value[1]
    df_out = (
        df
        .pipe(df_filter_multiple, input_persona_stream_capability_value, 'persona_stream') # filter by persona stream
        .pipe(df_filter_multiple_simple, input_categories_capability_value, 'platform_area_categories') # filter by platform area categories
        .pipe(df_filter_multiple_simple, input_relevance_value, 'relevance') # filter by relevance
        .query('skill_rating >= @min_rating') # filter by min rating
        .query('skill_rating <= @max_rating') # filter by max rating
        .groupby(['technology'])['id'].count().reset_index()
        )
    return df_out.shape[0], [0, min(df_out.shape[0], 15)]

# capabilities graph
@app.callback(
    Output('capability_graph', 'figure'),
    Output('capability_graph_hide', 'style'),
    Output('capability_no_one_found', 'style'),
    Input('input_persona_stream_capability', 'value'),
    Input('input_categories_capability', 'value'),
    Input('input_relevance', 'value'),
    Input('input_min_rating_capability', 'value'),
    Input('input_capability_graph_slider', 'value')
)
def update_capability_graph(
    input_persona_stream_capability_value, input_categories_capability_value,
    input_relevance_value, input_min_rating_capability_value,
    input_capability_graph_slider_value
):
    min_rating = input_min_rating_capability_value[0]
    max_rating = input_min_rating_capability_value[1]
    df_out = (
        df
        .pipe(df_filter_multiple, input_persona_stream_capability_value, 'persona_stream') # filter by persona stream
        .pipe(df_filter_multiple_simple, input_categories_capability_value, 'platform_area_categories') # filter by platform area categories
        .pipe(df_filter_multiple_simple, input_relevance_value, 'relevance') # filter by relevance
        .query('skill_rating >= @min_rating') # filter by min rating
        .query('skill_rating <= @max_rating') # filter by max rating
        .groupby(['technology'])['id'].count().reset_index()
        .rename(columns={'id' : 'rating_counts'})
        .sort_values(by='rating_counts', ascending=False)
        .iloc[input_capability_graph_slider_value[0]:input_capability_graph_slider_value[1]]
        )
    
    # adapt the scale according to counts
    scale, fill_color = [0, 10], '#e6cce6' # light purple

    # render graph
    fig = radar_single(df_out, 'rating_counts', 'technology', range_r=scale, fill_color=fill_color)

    # if nothing found, then don't show and return here
    if any([
        df_out.shape[0] == 0,
    ]):
        return fig, {'display' : 'none'}, {'display' : 'block'}

    max_counts = df_out['rating_counts'].max()
    if max_counts > 10:
        scale, fill_color = [0, 25], '#c080c0' # darker purple
    if max_counts > 25:
        scale, fill_color = [0, 55], '#800080' # same as COLOR_1
    
    # re-draw the graph
    fig = radar_single(df_out, 'rating_counts', 'technology', range_r=scale, fill_color=fill_color)

    return fig, {'display' : 'block'}, {'display' : 'none'}

# comparison graph
@app.callback(
    Output('comparison_graph', 'figure'),
    Output('comparison_graph_hide', 'style'),
    Output('comparison_no_one_found', 'style'),
    # Output('tester', 'children'), # delete after
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
        .pipe(df_filter_multiple_simple, input_categories_value, 'platform_area_categories') # filter by platform area categories
        .pipe(df_top_n_skills, [input_consultant_1_value, input_consultant_2_value], input_n_ratings_value) # filter by consultants
        [['skill_rating', 'technology', 'consultant_name']]
    )

    # render graph
    fig = radar_comparison(df_out, 'skill_rating', 'technology', 'consultant_name', [input_consultant_1_value, input_consultant_2_value])

    # if nothing found or all ratings are 0, then don't show
    if any([
        df_out.shape[0] == 0,
        df_out['skill_rating'].max() == 0
    ]):
        return fig, {'display' : 'none'}, {'display' : 'block'}

    return fig, {'display' : 'block'}, {'display' : 'none'}
    
@app.callback(
    Output('search_table', 'children'),
    Output('search_table_counts', 'children'),
    Input('input_technology', 'value'),
    Input('input_min_rating_search', 'value'),
)
def update_table(
    input_technology_value, input_min_rating_search_value
):
    min_rating, max_rating = input_min_rating_search_value[0], input_min_rating_search_value[1]

    # handle None for the counts table
    if input_technology_value is None:
        input_technology_value = []

    df_out = (
        df
        .pipe(df_filter_multiple_simple, input_technology_value, 'technology')
        .query('skill_rating >= @min_rating')
        .query('skill_rating <= @max_rating')
        .sort_values(by=['technology', 'skill_rating', 'consultant_name'], ascending=[True, False, True])
        [['consultant_name', 'skill_rating', 'technology']]
        .rename(columns={'consultant_name' : 'Name', 'skill_rating' : 'Rating', 'technology' : 'Technology'})
    )

    # group by rating
    df_out_counts = pd.DataFrame({
        'Rating' : [f'between {min_rating} and {max_rating}'],
        'Consultants' : [df_out['Name'].nunique()],
        # 'Technologies' : [''.join(input_technology_value)]
        })
    # return dash_table_interactive(df_out), dash_table_simple(df_out_counts)
    return\
        dbc.Table.from_dataframe(df_out, striped=True, bordered=True, size='sm'),\
        dbc.Table.from_dataframe(df_out_counts, bordered=True, size='sm')

# uncomment below for development and debugging
if __name__ == '__main__':
    app.run_server(port='8051', host='0.0.0.0', debug=True)
