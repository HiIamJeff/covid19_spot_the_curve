
import plotly_express as px
import plotly.graph_objects as go
from utils.format_utils import ordinal


# 7-day moving average
def create_trend_line_infection_rate_7day_moving(df, country_list, title_name):
    fig = go.Figure()
    fig.layout.template = 'ggplot2'
    for c in country_list:
        fig.add_trace(go.Scatter(x=df[c].dropna().index, y=df[c].dropna().values,
                                 mode='lines',
                                 # line_shape='spline',
                                 name=c,
                                 # hoverinfo="y+name",
                                 hovertemplate='<b>%{y:.0f}</b> new cases out of 1M people',))
    fig.update_xaxes(title_text='1-Day (Start on the date with the 100th case in each country)')
    fig.update_yaxes(title_text='Increased Positive Cases per 1 million people')
    fig.update_layout(
        title={
            'text': title_name,
            'font': {'size': 22, 'family': 'Arial, sans-serif'},
            'y': 0.95,
            #         'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis={
            'tickmode': 'array',
            'ticks': 'outside',
            'tickcolor': '#F7FBFE',
            'title_standoff': 15,
            # 'tick0': 2, # seems not supporting for now
            # 'dtick': 2,
            'tickvals': [n for n in range(0, 264) if (n + 10) % 10 == 0],  # Infinite number
            'ticktext': [ordinal(n) for n in range(0, 264) if (n + 10) % 10 == 0],  # Infinite number
        },
        yaxis={'title_standoff': 5, 'ticks': 'outside', 'tickcolor': '#F7FBFE', 'gridcolor': '#EEEEEE'},
        xaxis_showgrid=False,
        paper_bgcolor='#F7FBFE',  # canvas color
        plot_bgcolor='#F7FBFE', # plot color #D8D991 #F6EEDF #FFF8DE
        hoverlabel={'namelength':-1},

    )
    # fig.update_layout(hovermode="y")

    # color
    color_n = len(country_list)
    # cm = plt.get_cmap('tab10')
    # for i, color in enumerate([mpl.colors.rgb2hex(cm(1. * i / color_n)) for i in range(color_n)]):
    cm = px.colors.qualitative.T10 # e.g. ['#4C78A8']
    for i, color in enumerate(cm[0:color_n]):
        fig['data'][i]['marker'].update({'color': color})
        fig['data'][i]['marker']['line'].update({'color': color})
    return fig



#### Legacy plotting function
# def create_trend_line_infection_rate_2day(df, country_list, title_name):
#     fig = go.Figure()
#     fig.layout.template = 'ggplot2'
#     for c in country_list:
#         fig.add_trace(go.Scatter(x=df[c].dropna().index, y=df[c].dropna().values,
#                                  mode='lines',
#                                  # line_shape='spline',
#                                  name=c,
#                                  # hoverinfo="y+name",
#                                  hovertemplate='<b>%{y:.0f}</b> new cases out of 1M people',))
#     fig.update_xaxes(title_text='2-Day (Start on the date with the 100th case in each country)')
#     fig.update_yaxes(title_text='Increased Positive Cases per 1 million people')
#     fig.update_layout(
#         title={
#             'text': title_name,
#             'font': {'size': 22, 'family': 'Arial, sans-serif'},
#             'y': 0.95,
#             #         'x':0.5,
#             'xanchor': 'center',
#             'yanchor': 'top'},
#         margin=dict(l=20, r=20, t=50, b=20),
#         xaxis={
#             'tickmode': 'array',
#             'ticks': 'outside',
#             'tickcolor': '#F7FBFE',
#             'title_standoff': 15,
#             # 'tick0': 2, # seems not supporting for now
#             # 'dtick': 2,
#             'tickvals': [n for n in range(0, 264) if (n + 2) % 2 == 0],  # Infinite number
#             'ticktext': [ordinal(n) for n in [n for n in range(2, 528) if (n + 2) % 4 == 0]],  # Infinite number
#         },
#         yaxis={'title_standoff': 5, 'ticks': 'outside', 'tickcolor': '#F7FBFE', 'gridcolor': '#EEEEEE'},
#         xaxis_showgrid=False,
#         paper_bgcolor='#F7FBFE',  # canvas color
#         plot_bgcolor='#F7FBFE', # plot color #D8D991 #F6EEDF #FFF8DE
#         hoverlabel={'namelength':-1},
#
#     )
#     # fig.update_layout(hovermode="y")
#     ## color
#
#     ## new
#     color_n = len(country_list)
#     # cm = plt.get_cmap('tab10')
#     # for i, color in enumerate([mpl.colors.rgb2hex(cm(1. * i / color_n)) for i in range(color_n)]):
#     cm = px.colors.qualitative.T10 # e.g. ['#4C78A8']
#     for i, color in enumerate(cm[0:color_n]):
#         fig['data'][i]['marker'].update({'color': color})
#         fig['data'][i]['marker']['line'].update({'color': color})
#     return fig

