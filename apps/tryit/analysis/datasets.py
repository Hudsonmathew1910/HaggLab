"""
Tables the calculation projects work on, loaded from datasets/ (see datasets/README.md).
"""
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[3] / 'datasets'

TABLES = {
    'retail-sales': {
        'label': 'Retail shop sales',
        'about': 'Sales lines from 4 shops and an online store, Apr 2025 to Sep 2026. One row per product in an order.',
        'load': lambda: pd.read_csv(DATA_DIR / 'insightdesk' / 'retail_sales.csv', parse_dates=['date']),
        'date': 'date', 'amount': 'revenue', 'place': 'store', 'item': 'product', 'order': 'order_id',
    },
    'cafe-orders': {
        'label': 'Cafe chain orders',
        'about': 'Daily item sales of a 3-outlet cafe chain, Oct 2025 to Sep 2026. One row per item per outlet per day.',
        'load': lambda: pd.read_excel(DATA_DIR / 'reportbot' / 'cafe_sales.xlsx', sheet_name='Transactions', parse_dates=['date']),
        'date': 'date', 'amount': 'revenue', 'place': 'outlet', 'item': 'item', 'order': None,
    },
}


@lru_cache(maxsize=None)
def table(key):
    return TABLES[key]['load']()


@lru_cache(maxsize=None)
def cafe_sheet(name):
    return pd.read_excel(DATA_DIR / 'reportbot' / 'cafe_sales.xlsx', sheet_name=name)


@lru_cache(maxsize=None)
def weekly_sales():
    return pd.read_csv(DATA_DIR / 'forecastboard' / 'weekly_sales.csv', parse_dates=['week_start'])


def schema(key):
    """A short description of a table for the AI: columns, types, examples and date range."""
    df = table(key)
    info = TABLES[key]
    lines = [f"Table `df`: {info['about']}", f'{len(df):,} rows.', 'Columns:']
    for col in df.columns:
        s = df[col]
        if pd.api.types.is_datetime64_any_dtype(s):
            lines.append(f'- {col} (date): {s.min():%Y-%m-%d} to {s.max():%Y-%m-%d}')
        elif pd.api.types.is_numeric_dtype(s):
            lines.append(f'- {col} (number): min {s.min():g}, max {s.max():g}')
        else:
            values = s.dropna().unique()
            sample = ', '.join(map(str, values[:8]))
            more = f' (+{len(values) - 8} more)' if len(values) > 8 else ''
            lines.append(f'- {col} (text, {len(values)} values): {sample}{more}')
    return '\n'.join(lines)
