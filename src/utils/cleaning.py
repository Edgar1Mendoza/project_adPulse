def strip_whitespace(df, columns):
    for column in columns:
        df[column] = df[column].str.strip()
    return df
