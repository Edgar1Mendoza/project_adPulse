def strip_whitespace(df, columns):
    for column in columns:
        df[column] = df[column].str.strip()
    return df


def drop_exact_duplicates(df):
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    return df, removed
