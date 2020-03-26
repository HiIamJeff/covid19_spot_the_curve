# https://www.youtube.com/watch?v=5Cw4JumJTwo&t=1036s
#### THIS IS FOR THE TEST ####
## IDEA: Let users select specific country and status to showcase different barplots

import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import plotly_express as px
import requests
import pandas as pd
from datetime import datetime

# First use only 5 countries

country_slug_list = ['china', 'taiwan*', 'us', 'japan', 'italy']
status_list = ['confirmed', 'deaths']

# create the option list
country_options = [dict(label=c, value=c) for c in country_slug_list]


## Load the data
## This would call the API (https://covid19api.com/)

country = 'china'
country_name = 'china'
status = 'confirmed'

def country_status_dict(country):
    response_country = requests.get('https://api.covid19api.com/total/country/{}/status/{}'.format(country, 'confirmed'))
    country_data = response_country.json()
    case_country = {datetime.strptime(d['Date'][:10], '%Y-%m-%d'): d['Cases'] for i,d in enumerate(country_data)}
    return case_country

# def avg_confirmed_bar_plot(case_country, country_name):
#     day_count = {i+1: case_country.get(c) for i, c in enumerate(case_country)}
#     first_date = list(case_country.keys())[0].strftime("%Y-%m-%d")
#     df_dict = pd.DataFrame.from_dict(day_count, orient='index', columns=['Cases'])
#     df_dict.reset_index(inplace=True)
#     df_dict.rename(columns={'index': 'Day'}, inplace=True)
#     df_dict['Infection rate (# of cases per 1M people)'] = df_dict['Cases']/country_pop.get(country_name)*1000000
#     fig = px.bar(df_dict, x='Day', y='Infection rate (# of cases per 1M people)',
#                   title = '# of Confirmed Cases in <b>' + country_name +'</b>')
#     fig.update_xaxes(title_text='nth day ' + '(First recorded date is <b>{}</b>)'.format(first_date))
#     fig.update_yaxes(title_text='Infection rate (# of cases per 1M people)')
#     return fig

# def total_plot(country_name):
#     return avg_confirmed_bar_plot(country_status_dict(country), country_name)


# col_options = [dict(label=x, value=x) for x in tips.columns]
# dimensions = ['Country']

country_slug_list = ['china', 'taiwan*', 'us', 'japan', 'italy']
# status_list = ['confirmed', 'deaths']


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('CORONA: bar plot for each country test1'),
    html.Div(
        [html.P(['Country' + ':', dcc.Dropdown(id='Country', options=country_options)])], ),
    dcc.Graph(id='graph', figure=px.bar()),
])


@app.callback(Output('graph', 'figure'), [Input('Country', 'value')])
def cb(Country): # The parameters in this function should be the property
    day_count = {i + 1: country_status_dict(country).get(c) for i, c in enumerate(country_status_dict(country))}
    df = pd.DataFrame(data=list(day_count.values()), index=list(day_count.keys()), columns=['cases'])
    fig = px.bar(df)
    return day_count


app.run_server(debug=True)
