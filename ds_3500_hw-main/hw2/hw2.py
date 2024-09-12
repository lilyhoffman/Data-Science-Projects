import pandas as pd
import sankey as sk


def create_df(data):
    # json_data = json.loads(json_file)
    df = pd.read_json(data).dropna()
    filtered_df = df[['DisplayName', 'Nationality', 'Gender', 'BeginDate']]
    filtered_df = filtered_df[filtered_df.BeginDate != 0]
    filtered_df['Decade'] = filtered_df['BeginDate'].round(-1)
    filtered_df = filtered_df.astype({'Decade': str})
    
   
    return filtered_df


def create_grouped_df(df, groups: list, threshold):
    grouped_df = df.groupby(groups).size().reset_index(name='counts')
    grouped_df = grouped_df[grouped_df['counts'] > threshold]
    return grouped_df
    


if __name__ == '__main__':
    raw_df = create_df('data/artists.json')
    nat_decade_data = create_grouped_df(raw_df, ['Nationality', 'Decade'], 20)
    
    gender_nat_data = create_grouped_df(raw_df, ['Gender', 'Nationality'], 20)
    
    decade_gender_data = create_grouped_df(raw_df, ['Decade', 'Gender'], 20)
    sk.make_sankey(nat_decade_data, 'Nationality', 'Decade', vals='counts')
    
    sk.make_sankey(gender_nat_data, 'Gender', 'Nationality', vals='counts')
    
    sk.make_sankey(decade_gender_data, 'Decade', 'Gender', vals='counts')
    
    kitchen_sink = create_grouped_df(raw_df, ['Decade', 'Gender', 'Nationality'], 20)
    
    sk.make_sankey(kitchen_sink, 'Nationality', 'Decade', 'Gender', vals='counts')
    
    
    


