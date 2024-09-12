import plotly.graph_objects as go
from itertools import combinations
import pandas as pd


def _code_mapping(df, columns):
    """Map labels in src and targ to ints"""
    # get distinct labels
    labels = []
    for column in columns:
        labels = sorted(set(labels + list(df[column])))
    
    # get integer codes
    codes = list(range(len(labels)))
    # created a label to code mapping
    lc_map = dict(zip(labels, codes))
    
    # sub names for codes in df
    for column in columns:
        df = df.replace({column: lc_map})
    
    return df, labels

def _stacked_df(df, combos):
    my_dfs = []
    for combo in combos:
        full_cols = list(combo) + ['counts']
        x = df[full_cols]
        x =  x.groupby(list(combo)).sum().reset_index()
        x.columns = ['src', 'targ', 'counts']
        my_dfs.append(x)
    stacked_df = pd.concat(my_dfs, axis=0)
    return stacked_df, stacked_df['counts']
    


def make_sankey(df, src, targ, *cols, vals=None, **kwargs):
    """_summary_

    Args:
        df (_type_): Input dataframe
        src (_type_): Source column of labels
        targ (_type_): Target column of labels
        vals (_type_): Thickness of the link for each row
    """
    columns = [src, targ] + list(cols)
    column_combos = list(combinations(columns, 2))
    if vals: 
        values = df[vals]
    else:
        values = [1] * len(df)
    df, labels = _code_mapping(df, columns)
    
    df, values = _stacked_df(df, column_combos)
    
    
    line_color = kwargs.get('line_color', 'black')
    width = kwargs.get('line_width', 0)
    link = {'source': df['src'], 'target': df['targ'], 'value': values, 'line':{'color': line_color, 'width': width}}
    node = {'label': labels}
    
    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)
    fig.show()
    
    