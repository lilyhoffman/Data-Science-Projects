"""
File: baseball_api.py
Description: API for accessing data from the baseball db
"""

import pandas as pd
import sqlite3


class BaseballApi:
    con = None
    
    @staticmethod
    def connect(dbfile):
        """ make a connection """
        BaseballApi.con = sqlite3.connect(dbfile, check_same_thread=False)
    
    @staticmethod
    def execute(query):
        return pd.read_sql_query(query, BaseballApi.con)
    
    @staticmethod
    def get_team_stat_list():
        """ Returns a list of the possible team statistics 

        Returns:
            list: list of statistics column names
        """
        query = "SELECT value from team_columns_mapping"
        df = BaseballApi.execute(query)
        return list(df.Value)
    
    @staticmethod
    def get_yearly_stat(stat_value, team1, team2, year_range):
        """
        Returns: 
            pd.DataFrame: data table of each teams given stat for each year in the range of _year_range_
        """
        stat_key = BaseballApi.get_teams_stat_key(stat_value)
        
        query = f"""
        SELECT
            t.yearID as year,
            {stat_key} as '{stat_key}',
            t.teamID as teams
        FROM teams t 
        WHERE t.yearID <= {year_range[1]} AND t.yearID >= {year_range[0]}
        AND t.teamID in ('{team1}', '{team2}')
        """
        df = BaseballApi.execute(query)
        return df.pivot(index='year', columns='teams', values=f'{stat_key}').reset_index()
    
    @staticmethod
    def get_teams_list():
        """
        Returns:
            list: a list of all team three-letter abbreviations
        """
        query = """
        SELECT 
        DISTINCT
            f.franchID,
            f.franchName
        FROM teams t JOIN teams_franchises f ON t.teamID = f.franchID
        WHERE yearID > 1970
        """
        df = BaseballApi.execute(query)
        return list(df.franchID)
    
    @staticmethod
    def get_teams_stat_key(stat_value):
        
        query = f"SELECT Key FROM team_columns_mapping WHERE value like '{stat_value}'"
        df = BaseballApi.execute(query)
        return df.Key[0]


if __name__ == '__main__':
    api = BaseballApi()
    api.connect('data/baseball.db')
    
    print(api.get_teams_stat_key('Runs scored'))