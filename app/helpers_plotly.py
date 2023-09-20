import plotly.express as px
import plotly
import plotly.graph_objs as go
from random import choices

# color themes
COLOR_1 = '#800080'
COLOR_2 = '#66B3BA'
COLOR_3 = '#DC156B'

# comparison radar chart
def radar_comparison(df, value: str, variable: str, group_col, groups: str):
    group_color_map = {
        groups[0] : COLOR_1,
        groups[1] : COLOR_2
    }  
    # order in which the legend is displayed
    _order = {
        group_col : [groups[0], groups[1]]
    }

    fig = px.line_polar(
        df, r=value, theta=variable, line_close=True, color=group_col, category_orders=_order, color_discrete_map=group_color_map, range_r=[0, 5]
    )
    fig.update_traces(
        fill='toself'
    )
    fig.update_layout(
        showlegend=True,
        legend_x=100,
        legend_y=0,
        legend_title_text='',
        polar = dict(
            bgcolor='white',
            hole=0.03,
            angularaxis = dict(
                # linecolor='red',
                # categoryorder = 'total descending',
                showgrid=True,
                gridcolor='lightgrey',
                griddash='2px',
            ),
            radialaxis = dict(
                angle=160,
                tickangle=160,
                tickmode='array',
                tickvals=[1, 2, 3, 4, 5],
                tickfont= dict(
                    color=COLOR_3,
                    size=15
                ),
                showline=False,
                # showticklabels = False,
            ),            
        )
    )
    return fig

# single radar chart
def radar_single(df, value: str, variable: str, range_r: list, fill_color: str):
    fig = px.line_polar(
        df, r=value, theta=variable, line_close=True, text=value, range_r=range_r, color_discrete_sequence=[fill_color]
    )
    fig.update_traces(
        fill='toself',
        textposition='bottom left',
        textfont=dict(
            color=COLOR_3,
            size=12
        )
     )
    fig.update_layout(
        polar = dict(
            bgcolor='white',
            hole=0.03,
            angularaxis = dict(
                showgrid=True,
                gridcolor='lightgrey',
                griddash='2px',
            ),
            radialaxis = dict(
                angle=160,
                tickangle=160,
                tickmode='array',
                tickvals=[i for i in range(0, 70, 10)],
                tickfont= dict(
                    color=COLOR_3,
                    size=15
                ),
                showline=False,
                showticklabels=False
            ),            
        )
    )

    return fig

# word cloud
def word_cloud(df):
    space_multiplier = 10
    n_records = df.shape[0]
    axes_space = n_records * space_multiplier

    data = go.Scatter(
        x=choices(range(space_multiplier, axes_space-space_multiplier), k=n_records),
        y=[i for i in range(space_multiplier, axes_space, space_multiplier)],
        # y=choices(range(space_multiplier, axes_space-space_multiplier), k=n_records),
        mode='text',
        text=df['word'].tolist(), 
        marker={
            'opacity': 0.3
            },
        textfont={
            # 'size': df['frequency'].tolist(),
            'size': df['text_size'].tolist(),
            'color': [COLOR_1 for i in range(df.shape[0])]
            }
        )
    layout = go.Layout(
        {
            'xaxis': {
                'visible' : False
                },
            'yaxis': {
                'visible' : False
                },
            'plot_bgcolor' : 'white',
            'autosize' : True,
            # 'width' : 600,
            'height' : 200,            
            'margin' : {
                'l' : 0,
                'r' : 0,
                't' : 0,
                'b' : 0
            }
        }
    )
    fig = go.Figure(data=[data], layout=layout)
    fig.update_layout(xaxis_range=[1, axes_space], yaxis_range=[1, axes_space])
    return fig
