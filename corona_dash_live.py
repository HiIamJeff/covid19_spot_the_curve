# https://www.youtube.com/watch?v=5Cw4JumJTwo&t=1036s
#### THIS IS FOR REAL ####
## IDEA: PLOT, DESCRIPTION
## TEMPLATE: https://dash-gallery.plotly.host/dash-financial-report/full-view
## https://github.com/plotly/dash-sample-apps/blob/master/apps/dash-financial-report/pages/overview.py

## official doc
## https://plotly.com/python/reference/
## https://dash.plotly.com/dash-html-components

## WORKING ON Heroku app!
## DEPLOY PROBLEM (SEEMS THAT matplotlib IS NOT SUPPORTED IN HEROKU)
## CHANGE COLOR SCALE TO PLOTLY (DON'T IMPORT matplotlib)
## https://plotly.com/python/builtin-colorscales/
## https://plotly.com/python/discrete-color/

# https://stackoverflow.com/questions/43697460/import-matplotlib-failing-on-heroku

# https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement
## CONSIDERING ADDING REAL DATE INTO TOOLTIP OF EACH POINT?

# https://stackoverflow.com/questions/53327572/how-do-i-highlight-an-entire-trace-upon-hover-in-plotly-for-python
# https://plotly.com/javascript/plotlyjs-events/
## HOVER AND HIGHLIGHT

# https://www.bloomberg.com/news/articles/2020-05-03/an-uneven-curve-flattening-with-manhattan-ahead-of-the-bronx
## NEW YORK CITY STATUS

# https://github.com/COVID19Tracking/covid-tracking-dash/blob/master/covid_tracking/app.py
# http://35.212.27.3:8050/
## COOL WAY TO DO THE SIMILAR THING. CAN LEARN MARKDOWN FROM THIS

# LAYER

# import requests
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import plotly_express as px
# from datetime import datetime
from dash.dash import no_update
import plotly.graph_objects as go
# import plotly.io as pio
import dash_table

# import matplotlib as mpl
# import matplotlib.pyplot as plt
# from bokeh import palettes
import math

## function for turning number into ordinal number
ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])

## Load the data
data_url_new = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
df = pd.read_csv(data_url_new)


# processing
def jhu_data_process_date(jhu_data):
    # fix the country name
    jhu_data['Country/Region'] = jhu_data['Country/Region'].replace({'Korea, South': 'South Korea',
                                                                     'Taiwan*': 'Taiwan', 'US': 'United States'})
    df_country = jhu_data.set_index('Country/Region')
    # special fix for different level rows
    df_country.insert(loc=1, column="Country_level", value=0)
    duplicated = ~df_country.index.duplicated(keep=False)
    df_country['Country_level'] = duplicated.astype(int)
    df_country['index col'] = df_country.index
    special_rows = df_country[df_country['Country_level'] == 0]
    #     special_rows = special_rows[-special_rows['Province/State'].str.contains(', ')] # special fix for US # no longer need!
    # build date index
    date_list = list(special_rows.columns)[4:-1]
    # sum up the value from lower level
    try:
        agg_special_rows = special_rows.pivot_table(values=date_list, index='index col', aggfunc=np.sum)[date_list]
        df_country2 = df_country[df_country['Country_level'] == 1].copy()
        df_country2.drop(['Province/State', 'Country_level', 'Lat', 'Long', 'index col'], axis=1, inplace=True)
        final_country_df = pd.concat([df_country2, agg_special_rows]).T
    except:
        df_country2 = df_country[df_country['Country_level'] == 1].copy()
        df_country2.drop(['Province/State', 'Country_level', 'Lat', 'Long', 'index col'], axis=1, inplace=True)
        final_country_df = df_country2.T
    final_country_df.index = pd.to_datetime(final_country_df.index)
    return final_country_df


def jhu_data_process_day(date_df):
    day_list = [list(date_df[c][date_df[c] > 0]) for c in date_df.columns]
    day_df = pd.DataFrame(day_list, index=list(date_df.columns)).T
    day_df.index += 1
    return day_df

def jhu_data_process_2day_specific(date_df, day_threshold):
    country_arrays = [np.array(date_df[c])[np.array(date_df[c]) > day_threshold] for c in date_df.columns]
    day_df = pd.DataFrame(country_arrays).T
    day_df.columns = list(date_df.columns)
    day_df.index += 1
    # calculate daily increase
    temp_df = day_df.diff(periods=1)
    series_list = [temp_df[c].shift(-1)[temp_df[c].shift(-1) > 0].reset_index(drop=True) for c in temp_df.columns]
    daily_increase_df = pd.DataFrame(series_list).T
    daily_increase_df.index = daily_increase_df.index + 1
    ## make the value into 2-day format
    list_list = [[(daily_increase_df[c][n] + daily_increase_df[c][n + 1])
                  for n in range(1, len(daily_increase_df)) if n % 2 == 1] for c in daily_increase_df.columns]
    avg_2day_increase_df = pd.DataFrame(list_list, index=list(daily_increase_df.columns)).T
    return avg_2day_increase_df

def jhu_data_process_7day_moving(date_df, day_threshold):
    country_arrays = [np.array(date_df[c])[np.array(date_df[c]) > day_threshold] for c in date_df.columns]
    day_df = pd.DataFrame(country_arrays).T
    day_df.columns = list(date_df.columns)
    day_df.index += 1
    # calculate daily increase
    temp_df = day_df.diff(periods=1)
    series_list = [temp_df[c].shift(-1)[temp_df[c].shift(-1) > 0].reset_index(drop=True) for c in temp_df.columns]
    daily_increase_df = pd.DataFrame(series_list).T
    daily_increase_df.index = daily_increase_df.index + 1
    return daily_increase_df.rolling(window=7).mean().shift(-6)


## Population data
# data_path = r'C:\Users\ADMIN\Desktop\Python\Project_Coronavirus (COVID-19)\COVID19_Spot_the_Curve'
# data_file = 'Country_Population.csv'
data_url_pop = 'https://raw.githubusercontent.com/HiIamJeff/COVID19_Spot_the_Curve/master/Country_Population.csv'

pop_data = pd.read_csv(data_url_pop)
# pop_data = pd.read_csv(data_path + '/' + data_file, usecols=['Country', 'Population'])
pop_df = pop_data.copy()
pop_df['Population'] = pop_df['Population'].str.replace(',', '').astype(int)
country_pop_dict = pop_df.set_index('Country').to_dict('dict')['Population']
# fix specific country name
country_pop_dict['Czechia'] = country_pop_dict.pop('Czech Republic (Czechia)', 'default_value_if_not_found')


def data_process_avg(complete_df):
    for c in list(complete_df.columns):
        try:
            complete_df[c] = round(complete_df[c] / country_pop_dict.get(c) * 1000000, 2)
        except:
            complete_df[c + '_no_pop_value'] = complete_df[c]
    return complete_df


## final dataset
infection_data = data_process_avg(jhu_data_process_2day_specific(jhu_data_process_date(df), 100))
# moving average
infection_data_moving = data_process_avg(jhu_data_process_7day_moving(jhu_data_process_date(df), 100))


## Top 10 countries
def top_country(complete_df, rank):
    top = complete_df.T.iloc[:, -1].sort_values(ascending=False)[
          0:30]  # some countries have inconsistent name so limit the number
    top_avg = {c: round(top[c] / country_pop_dict.get(c) * 1000000, 2) for c in top.index}
    return pd.Series(top_avg, name='Infection Rate').sort_values(ascending=False)[0:rank]


top10_df = pd.DataFrame(top_country(jhu_data_process_date(df), 20))[0:10].reset_index().rename(
    columns={'index': 'Country'})

###############

####  drop down list function

asia_country = ['Japan', 'Taiwan', 'South Korea', 'Singapore', 'Thailand', 'Philippines',
                'Vietnam', 'Indonesia', 'China', 'India']
euro_country = ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Czechia', 'Denmark',
                'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy',
                'Luxembourg', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom']
america_country = ['United States', 'Brazil', 'Mexico', 'Colombia', 'Argentina', 'Canada', 'Peru',
                   'Venezuela', 'Chile', 'Ecuador', 'Guatemala', 'Cuba']
meast_country = ['Egypt', 'Iran', 'Iraq', 'Israel', 'Qatar', 'Saudi Arabia', 'Syria', 'Turkey', 'Yemen']

country_list = asia_country + euro_country + america_country + meast_country

# create the option list
country_options = [dict(label=c, value=c) for c in country_list]
# [{'label': 'Japan', 'value': 'Japan'},{'label': 'Taiwan', 'value': 'Taiwan'}]

# dropdown_function = dcc.Dropdown(id='country_selection',
#     options=country_options,
#     multi=True,
#     value=['Japan', 'Taiwan', 'Thailand']
#     # className="dcc_control"
# )

## test multiple dropdown function
country_options1 = [dict(label=c, value=c) for c in sorted(asia_country)]
country_options2 = [dict(label=c, value=c) for c in sorted(euro_country)]
country_options3 = [dict(label=c, value=c) for c in sorted(america_country)]
country_options4 = [dict(label=c, value=c) for c in sorted(meast_country)]

dropdown_function1 = dcc.Dropdown(id='country_selection1',
                                  options=country_options1,
                                  multi=True,
                                  value=['India'],
                                  placeholder="Asian Countries",
                                  # className="dcc_control"
                                  )

dropdown_function2 = dcc.Dropdown(id='country_selection2',
                                  options=country_options2,
                                  multi=True,
                                  value=['Italy', 'United Kingdom'],
                                  placeholder="European Countries",
                                  # className="dcc_control"
                                  )

dropdown_function3 = dcc.Dropdown(id='country_selection3',
                                  options=country_options3,
                                  multi=True,
                                  value=['United States'],
                                  placeholder="America Countries",
                                  # className="dcc_control"
                                  )

dropdown_function4 = dcc.Dropdown(id='country_selection4',
                                  options=country_options4,
                                  multi=True,
                                  value=[],
                                  placeholder="Middle East Countries",
                                  # className="dcc_control"
                                  )

####  Initiate the app
#### style setting
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'SPOT THE CURVE'

# in fact, html.Div() don't need children in my test
# original version
# app.layout = html.Div([
#     html.H1('TEST: This is a title'),
#     html.Div('This is some word'),
#     html.P(['Please select a country' + ':', dropdown_function]),
#     html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
#     dcc.Graph(id='output-graph', animate=None),
# ])

app.layout = html.Div([
    html.Div(className="row", children=[
        html.Div(className='four columns', children=[
            html.H2('Spot the Curve: COVID-19', style={'font-weight': 'bold', "margin-top": "10px", "margin-bottom": "2px"}),
            html.H6('Visualizing the Pressure of Healthcare', style={'color': '#6094B3', 'font-weight': 'bold', "margin-top": "1px", "margin-bottom": "0px"}),
            html.Div(['Made by ', html.A('Jeff Lu', href='https://www.linkedin.com/in/jefflu-chia-ching-lu/')], style={'font-style': 'italic', 'display': 'inline', "margin-bottom": "10px"}),
            # html.Br(),
            html.P(
                '''
                To understand the current pressure upon healthcare system in each country,  
                this app visualizes the latest confirmed cases of Coronavirus (COVID-19). 
                Pick the countries that you are interested in and see if you can spot the CURVE from them.
                ''',
                style={"margin-top": "10px"}),
            html.Header('Assumption and Plotting Detail', style={'font-weight': 'bold'}),
            html.P(
                '''
                Assuming the capacity of healthcare system is correlated to the population of the country 
                (and other health-resource-related data such as the number of hospital bed don't have consistency 
                across countries), I made the metric here as the “Infection Rate” (the number of confirmed cases per 
                1 million people) to showcase the curve.
                The number of daily increase is also aggregated into 7-day rolling average format to smooth trends. 
                '''
            ),
            html.P('Top 10 Highest-Infection-Rate Countries', style={'font-weight': 'bold'}),
            # test for new style
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in top10_df.columns],
                data=top10_df.to_dict('records'),
                fixed_columns={'headers': True, 'data': 1},
                style_as_list_view=True,
                style_cell={'backgroundColor': '#F7FBFE', 'padding': '5px', 'width': '50px'},
                style_header={
                    'backgroundColor': '#F7FBFE',
                    'fontWeight': 'bold',
                    'font-size': 16
                },
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'left'
                    } for c in ['Country']
                ],
            ),
        ]),
        html.Div(className='eight columns', children=[
            ## test multiple dropdown function
            # html.P(['Please pick a few countries (up to 10) and click submit:', dropdown_function]),
            html.P(['Pick countries from Asia, Europe, America or Middle East and generate the plot:',
                    dropdown_function1, ], style={"margin-top": "10px"}),
            html.P([dropdown_function2]),
            html.P([dropdown_function3]),
            html.P([dropdown_function4]),
            html.Button(id='button', n_clicks=0, children='Submit'),
            # html.Button(id='button2', n_clicks=0, children='7-Day Rolling Average', style={"margin-left": "10px"}),
            dcc.Graph(id='output-graph', animate=None),
            html.P(
                ['Data Source: ', html.A('Johns Hopkins University', href='https://github.com/CSSEGISandData/COVID-19'),
                 ' (Latest record is {})'.format(df.head().columns[-1])],
                style={'font-style': 'italic', 'display': 'inline', "margin-top": "10px"},
                # style={"margin-top": "10px"}
            ),
            html.Br([]),
            html.P(['Further Readings: ', html.A('Spot the Curve (Medium article)',
                                                 href='https://towardsdatascience.com/spot-the-curve-visualization-of-cases-data-on-coronavirus-8ec7cc1968d1?source=friends_link&sk=4f984ca1c1e4df9535b33d9ccab738ee'),
                    ', ', html.A('Coronavirus: Why You Must Act Now (Medium article)',
                                 href='https://medium.com/@tomaspueyo/coronavirus-act-today-or-people-will-die-f4d3d9cd99ca')], style={'font-style': 'italic', 'display': 'inline', "margin-top": "10px"}),
        ])
    ])
], style={'marginLeft': 20, 'marginRight': 20, 'marginTop': 20, 'marginBottom': 10,
          'backgroundColor': '#F7FBFE',
          'border': 'thin lightgrey dashed', 'padding': '5px 10px 5px 10px'}  # top right down left
)


# style = {"margin-top": "80px"},

## If using dash code to plot, then use html.Div
## If using plotly code to plot, then use dcc.Graph
## p.s. they have different components so watch out (children vs figure)

### plotting function ###
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

## 7-day moving average
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
    ## color

    ## new
    color_n = len(country_list)
    # cm = plt.get_cmap('tab10')
    # for i, color in enumerate([mpl.colors.rgb2hex(cm(1. * i / color_n)) for i in range(color_n)]):
    cm = px.colors.qualitative.T10 # e.g. ['#4C78A8']
    for i, color in enumerate(cm[0:color_n]):
        fig['data'][i]['marker'].update({'color': color})
        fig['data'][i]['marker']['line'].update({'color': color})
    return fig



# the output's component_property was 'children'

# @app.callback(
#     Output(component_id='output-graph', component_property='figure'),
#     [Input('button1', 'n_clicks_timestamp')],
#     [State(component_id='country_selection1', component_property='value'),
#      State(component_id='country_selection2', component_property='value'),
#      State(component_id='country_selection3', component_property='value'),
#      State(component_id='country_selection4', component_property='value')]
# )
# # State use for click action required!
#
# # if you want to change by input, then plotting should be in the def at the end ("input_data")
# # if you only want to show specific graph, then can plot it in the app.layout
#
# ## Multiple dropdown list
# def goplot(button_1, country_selection1, country_selection2, country_selection3, country_selection4):
#     # make sure it won't generate blank plot by itself and show error
#     if not (country_selection1, country_selection2, country_selection3, country_selection4):
#         return no_update  # This is prevent the web run the function without any input
#     # elif button_1:
#     #     outputtt = create_trend_line_infection_rate_2day(infection_data, country_selection1 + country_selection2
#     #                                                      + country_selection3 + country_selection4,
#     #                                                      '<b>Infection Rate Per Country</b>')
#     else:
#         outputtt = create_trend_line_infection_rate_2day(infection_data, country_selection1 + country_selection2
#                                                          + country_selection3 + country_selection4,
#                                                          '<b>Infection Rate Per Country</b>')
#     return outputtt
        # return country_selection

#### test multiple buttons

@app.callback(
    Output(component_id='output-graph', component_property='figure'),
    # [Input('button1', 'n_clicks'), Input('button2', 'n_clicks')],
    [Input('button', 'n_clicks')],
    [State(component_id='country_selection1', component_property='value'),
     State(component_id='country_selection2', component_property='value'),
     State(component_id='country_selection3', component_property='value'),
     State(component_id='country_selection4', component_property='value')]
)
# State use for click action required!

# if you want to change by input, then plotting should be in the def at the end ("input_data")
# if you only want to show specific graph, then can plot it in the app.layout

## Multiple dropdown list
def goplot2(button, country_selection1, country_selection2, country_selection3, country_selection4):
    # make sure it won't generate blank plot by itself and show error
    if not (country_selection1, country_selection2, country_selection3, country_selection4):
        return no_update  # This is prevent the web run the function without any input
    # elif button_1 > button_2:
    #     outputtt = create_trend_line_infection_rate_2day(infection_data, country_selection1 + country_selection2
    #                                                      + country_selection3 + country_selection4,
    #                                                      '<b>Infection Rate Per Country (2-Day Aggregation)</b>')
    # elif button_2:
    #     outputtt = create_trend_line_infection_rate_7day_moving(infection_data_moving, country_selection1 + country_selection2
    #                                                        + country_selection3 + country_selection4,
    #                                                        '<b>Infection Rate Per Country (7-Day Rolling Average)</b>')
    else:
        outputtt = create_trend_line_infection_rate_7day_moving(infection_data_moving,
                                                                country_selection1 + country_selection2
                                                                + country_selection3 + country_selection4,
                                                                '<b>Infection Rate Per Country (7-Day Rolling Average)</b>')
        # return no_update
    return outputtt

# n_clicks is required for click event
if __name__ == '__main__':
    app.run_server(debug=True)
