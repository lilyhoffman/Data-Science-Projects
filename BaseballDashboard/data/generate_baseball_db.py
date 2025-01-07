"""
File: generate_baseball_db.py
Description: script to take csv files and turn them into tables in the baseball.db file
"""

import sqlite3
import pandas as pd

def load_data(table, csv, db,types:dict=None):
    """ Loads data into a new or exisiting table in the given db file

    Args:
        table (string): table name to load data into
        csv (string): csv file path that contains the table data
        db (string): path to .db file
        types (dict?): optional arg that allows passing of column types as a dict
    """
    conn = sqlite3.connect(db)
    
    data_df = pd.read_csv(csv)
    data_df.to_sql(table, conn, if_exists='append', index=False, dtype=types)
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # load_data('teams', 'Teams.csv', 'baseball.db')
    # load_data('teams_franchises', 'TeamsFranchises.csv', 'baseball.db', {'franchID': 'TEXT PRIMARY KEY'})
    load_data('team_columns_mapping', 'team_columns_key.csv', 'baseball.db')