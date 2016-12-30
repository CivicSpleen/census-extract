"""Utilities for working with Census Data

Copyright (c) 2015 Civic Knowledge. This file is licensed under the terms of
the Revised BSD License, included in this distribution as LICENSE.txt

"""

def col_map(schema_df):
    
    """Returns a column map, from census colum ids to column titles, given a pandas Dataframe
    created from the schema csv file for a table. ie: 
    
    schema_df = pandas.read_csv('http://extracts.census.civicknowledge.com/2014/5/140_tract/b01001-schema.csv')
    """
    
    col_map = {}

    new_titles = []
    last_heading = ''

    for col_id, col_title in schema_df.loc[8:][['name','description']].values.tolist():
        if col_id.endswith('m90'):
            continue

        if col_title.endswith(':'):
            col_title = col_title.strip(':')
            col_map[col_id] = col_title
            last_heading = col_title
        else:
            col_map[col_id] = last_heading+' '+col_title
    
    # Now, add back in entries for the margins
    for k, v in col_map.items():
        col_map[k+'_m90'] = 'Margin for '+v
        
    return col_map