"""
ReportBot: the weekly / monthly / quarterly report.

All numbers are calculated here with pandas. Hero's AI only writes the short summary, from those
numbers, and the summary is shown separately from the table. If the AI is unavailable, the report
is still returned with the numbers.
"""
import json

import pandas as pd

from .. import hero_client, system_prompts, trace
from . import datasets

PERIOD_DAYS = {'last-week': 7, 'last-month': None, 'last-quarter': None}
PERIOD_LABEL = {'last-week': 'Last week', 'last-month': 'Last month', 'last-quarter': 'Last quarter'}

SUMMARY_RULES = system_prompts.REPORT_SUMMARY


def period_bounds(df, date_col, period):
    """Return (start, end, prev_start, prev_end) for the last complete period in the data."""
    last = df[date_col].max().normalize()
    if period == 'last-week':
        end = last - pd.Timedelta(days=last.weekday() + 1)  # last complete Sunday
        start = end - pd.Timedelta(days=6)
        return start, end, start - pd.Timedelta(days=7), start - pd.Timedelta(days=1)
    months = 1 if period == 'last-month' else 3
    month_end = last + pd.offsets.MonthEnd(0)
    end = last if last == month_end else last - pd.offsets.MonthEnd(1)
    start = (end - pd.DateOffset(months=months - 1)).replace(day=1)
    prev_end = start - pd.Timedelta(days=1)
    prev_start = (prev_end - pd.DateOffset(months=months - 1)).replace(day=1)
    return start, end, prev_start, prev_end


def pct(now, before):
    """Change as text, e.g. '+11.8%'. Empty when there is nothing to compare with."""
    return f'{float((now - before) / before * 100):+.1f}%' if before else ''


def money(value):
    return f'{value:,.0f}'


def build(table_key, period):
    info = datasets.TABLES[table_key]
    df = datasets.table(table_key)
    d, amt, place, item = info['date'], info['amount'], info['place'], info['item']
    start, end, p_start, p_end = period_bounds(df, d, period)
    cur = df[(df[d] >= start) & (df[d] <= end)]
    prev = df[(df[d] >= p_start) & (df[d] <= p_end)]

    revenue, prev_revenue = cur[amt].sum(), prev[amt].sum()
    rows = [['Revenue', money(revenue), money(prev_revenue), pct(revenue, prev_revenue)]]
    if info['order']:
        orders, prev_orders = cur[info['order']].nunique(), prev[info['order']].nunique()
        rows.append(['Orders', f'{orders:,}', f'{prev_orders:,}', pct(orders, prev_orders)])
        rows.append(['Average order value', f'{revenue / orders:,.2f}' if orders else '-',
                     f'{prev_revenue / prev_orders:,.2f}' if prev_orders else '-',
                     pct(revenue / orders, prev_revenue / prev_orders) if orders and prev_orders else ''])
    qty_col = 'quantity'
    rows.append(['Items sold', f'{cur[qty_col].sum():,}', f'{prev[qty_col].sum():,}', pct(cur[qty_col].sum(), prev[qty_col].sum())])

    by_place = cur.groupby(place)[amt].sum().sort_values(ascending=False)
    prev_place = prev.groupby(place)[amt].sum()
    for name, value in by_place.items():
        rows.append([f'{place.title()}: {name}', money(value), money(prev_place.get(name, 0)), pct(value, prev_place.get(name, 0))])
    top_items = cur.groupby(item)[amt].sum().sort_values(ascending=False).head(3)
    for rank, (name, value) in enumerate(top_items.items(), 1):
        rows.append([f'Top item {rank}: {name}', money(value), '', ''])

    if table_key == 'cafe-orders' and period != 'last-week':
        months = pd.period_range(start, end, freq='M').strftime('%Y-%m')
        targets = datasets.cafe_sheet('Targets')
        expenses = datasets.cafe_sheet('Expenses')
        target = targets[targets.month.isin(months)].revenue_target.sum()
        cost = expenses[expenses.month.isin(months)].amount.sum()
        if target:
            rows.append(['Revenue vs target', f'{revenue / target * 100:.1f}%', '', ''])
        if cost:
            rows.append(['Expenses', money(cost), '', ''])
            rows.append(['Profit (revenue - expenses)', money(revenue - cost), '', ''])

    table = {'columns': ['Measure', f'{start:%d %b} - {end:%d %b %Y}', f'{p_start:%d %b} - {p_end:%d %b %Y}', 'Change %'],
             'rows': rows}
    trace.show('2. Step A: Python (pandas) calculated the report from the data file', table)
    trace.show('3. Step B: AI writes the summary from these numbers only')
    try:
        reply = hero_client.parse_reply(hero_client.chat([
            {'role': 'system', 'content': SUMMARY_RULES},
            {'role': 'user', 'content': f"Business: {info['about']}\nReport: {PERIOD_LABEL[period]}\n{json.dumps(table)}"},
        ], temperature=0.3))
        text = reply.get('text', '')
    except hero_client.NotConnected:
        text = 'The written summary is not available right now. The numbers below are complete.'
    return {
        'text': text,
        'table': table,
        'source': f"{PERIOD_LABEL[period]} report from {info['label']}. Numbers calculated with pandas; summary written by AI.",
    }
