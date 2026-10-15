import pandas as pd


def coerce_numeric(df, columns, dtype):
    before_nulls = df[columns].isna().sum()
    df[columns] = pd.to_numeric(df[columns], errors="coerce").astype(dtype)
    after_nulls = df[columns].isna().sum()
    return df, after_nulls - before_nulls


def coerce_datetime(df, columns, format):
    before_nulls = df[columns].isna().sum()
    df[columns] = pd.to_datetime(df[columns], format=format, errors="coerce")
    after_nulls = df[columns].isna().sum()
    return df, after_nulls - before_nulls


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
