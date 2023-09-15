import pandas as pd

# column mappers
# strick matching
COLUMN_MAPPER_STRICT = {
    'ID' : 'id',
    'Technology' : 'technology',
    'Persona Stream' : 'persona_stream',
    'Platform, Area or Categories' : 'platform_area_categories',
    'Relevance' : 'relevance',
}

# loose matching
COLUMN_MAPPER_LOOSE = {
    'Pure count of the number of consultants with ratings of 4 or 5' : 'pure_count_4_5',
    'Implementability (applicable to exposé workpackages and Solution delivery categories only)' : 'implementability'
}

# column renamer
def df_renamer(df):
    for old_name, new_name in COLUMN_MAPPER_STRICT.items():
        df = (
            df
            .rename(columns={old_name : new_name})
        )
    for old_name, new_name in COLUMN_MAPPER_LOOSE.items():
        for c in df.columns:
            if old_name.lower() in c.lower():
                df = (
                    df
                    .rename(columns={c : new_name})
                )
    return df
 
# column dropper
def df_dropper(df, after='implementability'):
    cols = list(df.columns)
    to_drop = cols[cols.index(after)+1:]
    df = (
        df
        .drop(columns=to_drop)
    )
    return df

# melt ratings
def df_melt_ratings(df, after_var='relevance', before_var='pure_count_4_5'):
    cols = list(df.columns)
    id_vars = cols[:cols.index(after_var)+1] + cols[cols.index(before_var):]
    value_vars = cols[cols.index(after_var)+1:cols.index(before_var)]
    df = (
        df
        .melt(id_vars=id_vars, value_vars=value_vars, var_name='consultant_name', value_name='skill_rating')
    )
    return df

# persona stream cleaner
def df_persona_stream_cleaner(df, col='persona_stream'):
    df[col] = (
        df[col]
        .str.split(',')
        .apply(lambda x : [i.strip() for i in x])
        .apply(lambda x : [i.title() for i in x])
        .apply(lambda x : sorted(x))
    )
    return df

# get top n skills for a list of consultants
def df_top_n_skills(df, consultants: list, top_n: int):

    # get the first comparison
    df_comparison = (
        df
        .query('consultant_name in @consultants')
        .sort_values(by=['consultant_name', 'skill_rating'], ascending=[True, False])
        .groupby('consultant_name')
        .head(top_n)
        .reset_index(drop=True)
    )

    # now we need to get all tech for the full comparison
    tech_list = df_comparison['technology'].unique().tolist()
    df_full_comparison = (
        df
        .query('consultant_name in @consultants')
        .query('technology in @tech_list')
        .reset_index(drop=True)
    )
    return df_full_comparison

# check is two lists have an element in common
common_elem = lambda x, y : any(i in x for i in y)

# filter by multiple selections, both input and target are lists
def df_filter_multiple(df, inputs: list, col: str):
    
    # nothing is selected
    if not isinstance(inputs, list) or len(inputs) == 0: 
        return df
    
    df = (
        df
        .assign(_temp=df[col].apply(lambda x : 1 if common_elem(x, inputs) else 0))
        .query('_temp == 1')
        .drop(columns='_temp')
    )
    return df

# filter by multiple selections, target is str
def df_filter_multiple_simple(df, inputs: list, col: str):
    
    # nothing is selected
    if not isinstance(inputs, list) or len(inputs) == 0: 
        return df
    
    df = (
        df
        .assign(_temp=df[col].apply(lambda x : 1 if x in inputs else 0))
        .query('_temp == 1')
        .drop(columns='_temp')
    )
    return df
