import plotly.express as px

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
def radar_single(df, value: str, variable: str):
    fig = px.line_polar(
        df, r=value, theta=variable, line_close=True, text=value
    )
    fig.update_traces(
        fill='toself',
        textposition='bottom center'
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
                # tickmode='array',
                # tickvals=[1, 2, 3, 4, 5],
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
