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
