"""
ForecastBoard: forecast weekly demand and say how accurate the forecast is.

Two methods are tested on the last 12 known weeks (a "backtest"):
- Recent average: the mean of the last 8 weeks (the simple baseline).
- Seasonal: the same week last year, scaled by this year's growth.
The method with the lower backtest error is used. The range shown is the forecast plus or minus
that error. Hero's AI explains the result in plain words; if it is unavailable the numbers still show.
"""
import json

import numpy as np
import pandas as pd

from .. import hero_client, system_prompts, trace
from . import datasets

BACKTEST_WEEKS = 12

EXPLAIN_RULES = system_prompts.FORECAST_EXPLAIN


def series(category):
    df = datasets.weekly_sales()
    if category != 'all':
        df = df[df.category == category]
    return df.groupby('week_start').units_sold.sum().sort_index()


def recent_average(history, horizon):
    return np.repeat(history.iloc[-8:].mean(), horizon)


def seasonal(history, horizon):
    recent = history.iloc[-12:].sum()
    year_ago = history.iloc[-64:-52].sum()
    growth = recent / year_ago if year_ago else 1.0
    start = len(history) - 52
    return np.array([history.iloc[start + i] * growth for i in range(horizon)])


METHODS = {'Recent average': recent_average, 'Seasonal (same week last year x growth)': seasonal}


def mape(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    return float(np.mean(np.abs(actual - predicted) / np.maximum(actual, 1)) * 100)


def build(category, weeks):
    s = series(category)
    train, test = s.iloc[:-BACKTEST_WEEKS], s.iloc[-BACKTEST_WEEKS:]
    errors = {name: mape(test.values, fn(train, BACKTEST_WEEKS)) for name, fn in METHODS.items()}
    best = min(errors, key=errors.get)
    error = max(errors[best], 5.0)
    forecast = METHODS[best](s, weeks)

    last_week = s.index[-1]
    rows = []
    for i, value in enumerate(forecast, 1):
        week = last_week + pd.Timedelta(weeks=i)
        year_ago = s.get(week - pd.Timedelta(weeks=52))
        rows.append([f'{week:%Y-%m-%d}', int(round(value)), int(round(value * (1 - error / 100))), int(round(value * (1 + error / 100))),
                     int(year_ago) if year_ago is not None else None])
    table = {'columns': ['Week starting', 'Forecast units', 'Low', 'High', 'Same week last year'], 'rows': rows}
    method_table = [[name, f'{err:.1f}%', 'Used' if name == best else ''] for name, err in errors.items()]

    label = 'all categories' if category == 'all' else category
    facts = {'category': label, 'weeks_ahead': weeks, 'method_used': best, 'backtest_error_pct': {k: round(v, 1) for k, v in errors.items()},
             'forecast_total': int(sum(forecast)), 'same_weeks_last_year_total': int(sum(r[4] or 0 for r in rows)),
             'last_8_weeks_average': round(float(s.iloc[-8:].mean()))}
    trace.show('2. Step A: Python tested the forecast methods and made the forecast', {'errors_pct': facts['backtest_error_pct'], 'used': best, 'rows': rows})
    trace.show('3. Step B: AI explains the forecast from these facts only', facts)
    try:
        reply = hero_client.parse_reply(hero_client.chat([
            {'role': 'system', 'content': EXPLAIN_RULES},
            {'role': 'user', 'content': json.dumps(facts)},
        ], temperature=0.3))
        text = reply.get('text', '')
    except hero_client.NotConnected:
        text = (f'Expected about {facts["forecast_total"]:,} units over the next {weeks} weeks for {label}. '
                f'Method: {best}, which was off by {errors[best]:.1f}% on the last {BACKTEST_WEEKS} known weeks.')
    return {
        'text': text,
        'labels': [f'Method: {best}', f'Backtest error: {errors[best]:.1f}%'],
        'table': table,
        'items': [{'title': name, 'meta': f'Error on the last {BACKTEST_WEEKS} weeks: {err}{" (used)" if used else ""}'}
                  for name, err, used in method_table],
        'source': 'Weekly sales history, Jan 2024 to Sep 2026. Forecast calculated with Python; explanation written by AI.',
    }
