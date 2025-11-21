import pandas as pd


def safe_na_datetime(item: pd.Series):
    """SQLAlchemy cannot process pd.NaT as None.
    Returns None when the value is pd.NaT (or pd.Na)"""
    return item.apply(lambda value: None if pd.isna(value) else value)
