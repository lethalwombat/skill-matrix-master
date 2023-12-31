import dash_bootstrap_components as dbc
from dash import html, dash_table, dcc
from random import choice

# color themes
COLOR_1 = '#800080'
COLOR_2 = '#D43E78'

# heading
heading = lambda x : html.H4(x, style={'color' : COLOR_1, 'text-align' : 'center'})

# label
html_label = lambda x : html.Label(x, style={'color' : COLOR_2, 'text-align' : 'right'})
html_label_center = lambda x : html.Label(x, style={'color' : COLOR_2, 'text-align' : 'center'})

# card tab wrapper
def card_tab(label='tab', id='id', content=html.Br()):
    return \
        dbc.Tab(
            dbc.Card(
            dbc.CardBody(
                content
            ), className='mt-3'
        ), label=label, id=id, active_label_style={'color' : COLOR_1})

# datatable wrapper
def dash_table_interactive(df):
        return dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns
            ],
            editable=False,
            sort_action='native')

# datatable wrapper simple
def dash_table_simple(df):
        return dash_table.DataTable(data=df.to_dict('records'))

# wrap text into paragraphs
def dash_text_wrapper(text: str, sep='\n\n'):    
    div_out = []
    text_list = text.split(sep)
    for par in text_list:
          div_out.append(html.P(par))
          div_out.append(html.Br())
    if len(div_out) > 0:
          return div_out[:-1]
    return div_out