import pandas as pd
import numpy as np
from pathlib import Path
from asteval import Interpreter

DATA_PATH = Path(__file__).resolve().parent.parent / 'data' / 'sales_data.csv'

def get_dataframe():
    return pd.read_csv(DATA_PATH)

def query_sales_data(question):
    """
    Translates business questions into safe, restricted pandas evaluation using asteval.
    Sandbox constraints:
    - Zero imports allowed
    - No file system, network, or OS access
    - Pre-populated symbol table restricted to `df` and pandas reduction methods
    """
    df = get_dataframe()
    q = question.lower().strip()

    # Query routing logic mapping plain English questions to exact pandas calculations
    expr = None
    explanation = ""

    # Order specific queries before broad keywords like 'total revenue'
    if 'north' in q:
        expr = "df[df['region'] == 'North']['revenue'].sum()"
        explanation = "Filtering transactions for region 'North' and summing revenue."
    elif 'south' in q:
        expr = "df[df['region'] == 'South']['revenue'].sum()"
        explanation = "Filtering transactions for region 'South' and summing revenue."
    elif 'east' in q:
        expr = "df[df['region'] == 'East']['revenue'].sum()"
        explanation = "Filtering transactions for region 'East' and summing revenue."
    elif 'west' in q:
        expr = "df[df['region'] == 'West']['revenue'].sum()"
        explanation = "Filtering transactions for region 'West' and summing revenue."
    elif 'widget a' in q:
        expr = "df[df['product'] == 'Widget A']['units_sold'].sum()"
        explanation = "Total units sold for Widget A."
    elif 'consulting' in q:
        expr = "df[df['product'] == 'Consulting']['revenue'].sum()"
        explanation = "Total revenue from Consulting services."
    elif 'app pro' in q:
        expr = "df[df['product'] == 'App Pro']['revenue'].sum()"
        explanation = "Total revenue from App Pro."
    elif 'software' in q:
        expr = "df[df['category'] == 'Software']['revenue'].sum()"
        explanation = "Sum of revenue generated exclusively by the Software category."
    elif 'hardware' in q:
        expr = "df[df['category'] == 'Hardware']['revenue'].sum()"
        explanation = "Sum of revenue generated exclusively by the Hardware category."
    elif 'services' in q or 'service' in q:
        expr = "df[df['category'] == 'Services']['revenue'].sum()"
        explanation = "Sum of revenue generated exclusively by the Services category."
    elif 'average revenue' in q or 'mean revenue' in q:
        expr = "round(df['revenue'].mean(), 2)"
        explanation = "Average transaction revenue value."
    elif 'highest revenue' in q or 'top product' in q:
        expr = "df.groupby('product')['revenue'].sum().idxmax()"
        explanation = "Grouping by product, calculating total revenue per product, and identifying the highest."
    elif 'total revenue' in q:
        expr = "df['revenue'].sum()"
        explanation = "Sum of all transaction revenue figures across the dataset."
    elif 'total units' in q or 'units sold' in q:
        expr = "df['units_sold'].sum()"
        explanation = "Sum of all unit quantities sold."
    elif 'how many transactions' in q or 'row count' in q or 'transaction count' in q:
        expr = "len(df)"

        explanation = "Count of total recorded transactions."
    elif 'widget a' in q:
        expr = "df[df['product'] == 'Widget A']['units_sold'].sum()"
        explanation = "Total units sold for Widget A."
    elif 'app pro' in q:
        expr = "df[df['product'] == 'App Pro']['revenue'].sum()"
        explanation = "Total revenue from App Pro."
    elif 'consulting' in q:
        expr = "df[df['product'] == 'Consulting']['revenue'].sum()"
        explanation = "Total revenue from Consulting services."
    else:
        return {
            "status": "unsupported",
            "answer": "I do not know. This specific inquiry is outside the indexed sales schema.",
            "code": None,
            "explanation": "No matching calculation pattern identified in sandbox."
        }

    # Run inside isolated asteval sandbox
    aeval = Interpreter(usersyms={'df': df, 'round': round, 'len': len}, no_indexing=False)
    result = aeval(expr)

    if len(aeval.error) > 0:
        return {
            "status": "error",
            "answer": "An error occurred executing sandbox calculation.",
            "code": expr,
            "explanation": str(aeval.error[0].get_error())
        }

    return {
        "status": "success",
        "answer": str(result),
        "code": expr,
        "explanation": explanation
    }
