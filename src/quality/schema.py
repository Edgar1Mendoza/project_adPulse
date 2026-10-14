def detect_new_columns(df, expected_columns):
    actual_columns = set(df.columns)
    expected = set(expected_columns)
    new_columns = actual_columns - expected
    return list(new_columns)
