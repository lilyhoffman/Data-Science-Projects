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
        html.H4('Baseball Team Comparison Dashboard'),
        dcc.Graph(id="graph", style={'width': '100vw', 'height': '60vh'}),

        html.P("Select Team 1:"),
        dcc.Dropdown(id='team1', options=api.get_teams_list(), value='PHI'),
        
        html.P("Select Team 2:"),
        dcc.Dropdown(id='team2', options=api.get_teams_list(), value= 'BOS'),
        
        html.P("Select Stat:"),
        dcc.Dropdown(id='stat', options=api.get_team_stat_list(), value="Wins"),

        html.P("Years:"),
        dcc.RangeSlider(id='year_range', 
                        min=1970, 
                        max=2015, 
                        step=10, 
                        marks={i: '{}'.format(i) for i in range(1970,2015,10)},
                        value=[1980, 2000]),
        
        

    ])



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