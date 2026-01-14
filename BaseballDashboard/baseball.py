"""
File: baseball.py

Description: A database-driven dashboard
for visualizing baseball pitching data over the years.

"""


from baseball_api import BaseballApi
from dash import Dash, dcc, html, Input, Output
import plotly.express as px



def main():


    # initialize the API
    api = BaseballApi()
    api.connect("data/baseball.db")

    # create the dash app
    app = Dash(__name__)

    # Create the layout
    app.layout = html.Div([
        html.H2('⚾ Baseball Team Comparison Dashboard', style={'textAlign': 'center', 'marginBottom': '30px'}),

        dcc.Graph(id="graph", style={'width': '100%', 'height': '60vh'}),

        html.Div([
            html.Div([
                html.Label("Select Team 1:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='team1', options=api.get_teams_list(), value='PHI')
            ], style={'width': '48%', 'paddingRight': '10px'}),

            html.Div([
                html.Label("Select Team 2:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='team2', options=api.get_teams_list(), value='BOS')
            ], style={'width': '48%', 'paddingLeft': '10px'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

        html.Div([
            html.Label("Select Stat:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(id='stat', options=api.get_team_stat_list(), value="Wins")
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Label("Years:", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='year_range',
                min=1970,
                max=2015,
                step=1,
                marks={i: str(i) for i in range(1970, 2016, 10)},
                value=[1980, 2000]
            )
        ]),
    ], style={'maxWidth': '900px', 'margin': 'auto', 'padding': '20px'})



    @app.callback(
        Output("graph", "figure"),
        Input("year_range", "value"),
        Input("stat", "value"),
        Input("team1", "value"),
        Input("team2", "value"),
        
    )
    def display_graph(year_range, stat, team1, team2):
        data = api.get_yearly_stat(stat, team1, team2, year_range)
        fig = px.line(data, x="year", 
                      y=[team1,team2], 
                      title= f'{stat} over Years',
                      labels= {'value': stat,
                               'year': 'Year',
                               'variable': 'Teams'})
        return fig

    # runs server
    app.run_server(debug=True)



main()