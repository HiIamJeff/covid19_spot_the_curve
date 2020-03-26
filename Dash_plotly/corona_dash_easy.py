# https://www.youtube.com/watch?v=5Cw4JumJTwo&t=1036s
#### THIS IS FOR THE TEST ####
## IDEA: Let users select specific country and status to showcase different barplots

import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly_express as px
import requests
import pandas as pd
from datetime import datetime
from dash.dash import no_update

# First use only 5 countries
country_slug_list = ['china', 'taiwan*', 'us', 'japan', 'italy']
status_list = ['confirmed', 'deaths']

# create the option list
country_options = [dict(label=c, value=c) for c in country_slug_list]

## Load the data
## This would call the API (https://covid19api.com/)
# country = 'china'
# country_name = 'china'
# status = 'confirmed'

# 'NoneType' object is not iterable # first ignore because this won't affect the function
## used in easy plot
# def country_status_df(country='us'):
#     response_country = requests.get('https://api.covid19api.com/total/country/{}/status/{}'.format(country, 'confirmed'))
#     country_data = response_country.json()
#     case_country = {datetime.strptime(d['Date'][:10], '%Y-%m-%d'): d['Cases'] for i,d in enumerate(country_data)}
#     day_count = {i + 1: case_country.get(c) for i, c in enumerate(case_country)}
#     df = pd.DataFrame(data=list(day_count.values()), index=list(day_count.keys()), columns=['cases'])
#     return df

#
def country_status_dict(country='us'):
    response_country = requests.get('https://api.covid19api.com/total/country/{}/status/{}'.format(country, 'confirmed'))
    country_data = response_country.json()
    # case_country = {datetime.strptime(d['Date'][:10], '%Y-%m-%d'): d['Cases'] for i,d in enumerate(country_data)}
    return {datetime.strptime(d['Date'][:10], '%Y-%m-%d'): d['Cases'] for i,d in enumerate(country_data)}

app = dash.Dash()

# app.layout = html.Div(children=[
#     html.Div(children='''
#         Symbol to graph:
#     '''),
#     dcc.Input(id='input', value='', type='text'),
#     html.Div(id='output-graph'),
# ])

# app.layout = html.Div(children=[
#     html.Div(children='''
#         123123123123123
#     '''),
#     html.P(['country' + ':', dcc.Dropdown(id='country', options=country_options)]),
#     html.Div(id='output-graph'),
# ])

# in fact, html.Div() don't need children in my test
# try dropdown()
app.layout = html.Div([
    html.H1('TEST: This is a title'),
    html.Div('This is some word'),
    html.P(['Please select a country' + ':', dcc.Dropdown(id='country_selection', options=country_options)]),
    dcc.Graph(id='output-graph'),
])
# original version

## If using dash code to plot, then use html.Div
## If using plotly code to plot, then use dcc.Graph
## p.s. they have different components so watch out (children vs figure)

### plotting function ###
country_pop = {'china': 1433783686, 'taiwan': 23773876, 'us': 329064917, 'japan': 126860301, 'italy': 60550075}
def avg_confirmed_bar_plot(case_country, country_name):
    day_count = {i+1: case_country.get(c) for i, c in enumerate(case_country)}
    first_date = list(case_country.keys())[0].strftime("%Y-%m-%d")
    df_dict = pd.DataFrame.from_dict(day_count, orient='index', columns=['Cases'])
    df_dict.reset_index(inplace=True)
    df_dict.rename(columns={'index': 'Day'}, inplace=True)
    df_dict['Infection rate (# of cases per 1M people)'] = df_dict['Cases']/country_pop.get(country_name)*1000000
    fig = px.bar(df_dict, x='Day', y='Infection rate (# of cases per 1M people)',
                  title = '# of Confirmed Cases in <b>' + country_name +'</b>')
    fig.update_xaxes(title_text='nth day ' + '(First recorded date is <b>{}</b>)'.format(first_date))
    fig.update_yaxes(title_text='Infection rate (# of cases per 1M people)')
    return fig

# the output's component_property was 'children'
@app.callback(
    Output(component_id='output-graph', component_property='figure'),
    [Input(component_id='country_selection', component_property='value')]
)

# if you want to change by input, then plotting should be in the def at the end ("input_data")
# if you only want to show specific graph, then can plot it in the app.layout

## This could work! (easy plot!)
# def update_value(country_selection):
#     # df = country_status_df(country_selection)
#     return dcc.Graph(
#         id='example-graph',
#         figure={
#             'data': [
#                 {'x': country_status_df(country_selection).index, 'y': country_status_df(country_selection)['cases'],
#                  'type': 'line', 'name': country_selection},
#             ],
#             'layout': {
#                 'title': country_selection
#             }
#         }
#     )

## try to plot the avg plot
def goplot(country_selection):
    if not country_selection:
        return no_update # This is prevent the web run the function without any input
    else:
        outputtt = avg_confirmed_bar_plot(country_status_dict(country_selection), country_selection)
        return outputtt

if __name__ == '__main__':
    app.run_server(debug=True)

## works! but have error message!
