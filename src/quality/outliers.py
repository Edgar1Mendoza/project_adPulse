def detect_outliers_iqr(df, column, multiplier=1.5):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return df[(df[column] < lower) | (df[column] > upper)]


def detect_outliers_percentile(df, column, threshold=0.99):
    cutoff = df[column].quantile(threshold)
    return df[df[column] > cutoff]
