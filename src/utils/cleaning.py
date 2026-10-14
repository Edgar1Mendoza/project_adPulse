import pandas as pd


def strip_whitespace(df, columns):
    for column in columns:
        df[column] = df[column].str.strip()
    return df


def drop_exact_duplicates(df):
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    return df, removed


def filter_future_dates(df, column):
    today = pd.Timestamp.now().normalize()
    before = len(df)
    df = df[df[column] <= today]
    removed = before - len(df)
    return df, removed
