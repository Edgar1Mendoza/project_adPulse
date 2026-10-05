def assert_no_nulls(df, columns):
    for column in columns:
        null_rows = df[df[column].isna()]
        if len(null_rows) > 0:
            raise ValueError(
                f"{len(null_rows)} rows have null values in column {column}"
                f"{null_rows.index.tolist()}"
            )


def assert_no_duplicates(df, subset):
    duplicate_rows = df[df.duplicated(subset=subset, keep=False)]
    if len(duplicate_rows) > 0:
        raise ValueError(
            f"{len(duplicate_rows)} duplicate rows on {subset} : {duplicate_rows.index.tolist()}"
        )


def assert_min_rows(df, min_rows=1):
    if len(df) < min_rows:
        raise ValueError(f"Expected at least {min_rows} rows, got {len(df)}")


def assert_positive(df, columns):
    for column in columns:
        negative_rows = df[df[column] <= 0]
        if len(negative_rows) > 0:
            raise ValueError(
                f"{len(negative_rows)} rows with non-positive '{column}': "
                f"{negative_rows.index.tolist()}"
            )


def assert_columns_present(df, columns):
    missing_columns = [column for column in columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing expected columns: {missing_columns}")
