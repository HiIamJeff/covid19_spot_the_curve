
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
from dash.dash import no_update
import dash_table
import math

from utils.plotting_utils import create_trend_line_infection_rate_7day_moving
from data_processing import df_case, infection_data, infection_data_moving, top10_df


# drop down list function
asia_country = ['Japan', 'Taiwan', 'South Korea', 'Singapore', 'Thailand', 'Philippines',
                'Vietnam', 'Indonesia', 'China', 'India']
euro_country = ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Czechia', 'Denmark',
                'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy',
                'Luxembourg', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom']
america_country = ['United States', 'Brazil', 'Mexico', 'Colombia', 'Argentina', 'Canada', 'Peru',
                   'Venezuela', 'Chile', 'Ecuador', 'Guatemala', 'Cuba']
meast_country = ['Egypt', 'Iran', 'Iraq', 'Israel', 'Qatar', 'Saudi Arabia', 'Syria', 'Turkey', 'Yemen']

country_list = asia_country + euro_country + america_country + meast_country
country_options = [dict(label=c, value=c) for c in country_list]
# e.g., [{'label': 'Japan', 'value': 'Japan'},{'label': 'Taiwan', 'value': 'Taiwan'}]

# multiple dropdown function
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
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'SPOT THE CURVE'

app.layout = html.Div([
    html.Div(className="row", children=[
        html.Div(className='four columns', children=[
            html.H2('Spot the Curve: COVID-19', style={'font-weight': 'bold', "margin-top": "10px", "margin-bottom": "2px"}),
            html.H6('Visualizing the Pressure of Healthcare', style={'color': '#6094B3', 'font-weight': 'bold', "margin-top": "1px", "margin-bottom": "0px"}),
            html.Div(['Made by ', html.A('Jeff Lu', href='https://www.linkedin.com/in/jefflu-chia-ching-lu/')], style={'font-style': 'italic', 'display': 'inline', "margin-bottom": "10px"}),
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
                 ' (Latest record is {})'.format(df_case.head().columns[-1])],
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

""" Note
If using dash code to plot, then use html.Div
If using plotly code to plot, then use dcc.Graph
p.s. they have different components so watch out (children vs figure)
"""

@app.callback(
    Output(component_id='output-graph', component_property='figure'),
    [Input('button', 'n_clicks')],
    [State(component_id='country_selection1', component_property='value'),
     State(component_id='country_selection2', component_property='value'),
     State(component_id='country_selection3', component_property='value'),
     State(component_id='country_selection4', component_property='value')]
)
def goplot2(button, country_selection1, country_selection2, country_selection3, country_selection4):
    """
    # State use for click action required!
    # if you want to change by input, then plotting should be in the def at the end ("input_data")
    # if you only want to show specific graph, then can plot it in the app.layout
    # the output's component_property was 'children'
    """
    # make sure it won't generate blank plot by itself and show error
    if not (country_selection1, country_selection2, country_selection3, country_selection4):
        return no_update  # This prevents the web run the function without any input
    else:
        output = create_trend_line_infection_rate_7day_moving(infection_data_moving,
                                                                country_selection1 + country_selection2
                                                                + country_selection3 + country_selection4,
                                                                '<b>Infection Rate Per Country (7-Day Rolling Average)</b>')
    return output

# n_clicks is required for click event
if __name__ == '__main__':
    app.run_server(debug=True)

""" note
# https://www.youtube.com/watch?v=5Cw4JumJTwo&t=1036s
# https://www.bloomberg.com/news/articles/2020-05-03/an-uneven-curve-flattening-with-manhattan-ahead-of-the-bronx
## NEW YORK CITY STATUS
# https://github.com/COVID19Tracking/covid-tracking-dash/blob/master/covid_tracking/app.py
# http://35.212.27.3:8050/
"""
