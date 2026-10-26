"""
Runs AI-written pandas code in a separate, short-lived Python process.

Started by sandbox.run() as:  python -I sandbox_runner.py   (JSON job on stdin, JSON result on stdout)

Layers of protection:
1. check_code(): the code is parsed and refused if it imports, defines functions or classes,
   touches names or attributes starting with "_", or calls file/network methods (to_csv, read_*, ...).
2. asteval runs it with only `df`, a small `pd` and `np` toolbox, and no open(), eval() or import.
3. This is a separate process with no access to Django, settings or keys, and the parent kills it after a timeout.
"""
import ast
import json
import math
import sys
from types import SimpleNamespace

ALLOWED_TO = {'to_period', 'to_timestamp', 'to_frame', 'to_numpy', 'to_list', 'to_dict', 'to_datetime', 'to_numeric'}
DENIED_ATTRS = {'eval', 'query', 'pipe', 'style', 'plot', 'hist', 'boxplot', 'attrs', 'flags', 'mro',
                'gi_frame', 'f_globals', 'func_globals', 'system', 'popen', 'load', 'loads', 'dump', 'dumps'}
DENIED_NODES = (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Global,
                ast.Nonlocal, ast.With, ast.AsyncWith, ast.While, ast.Try, ast.Delete, ast.Await, ast.Yield)
MAX_ROWS = 50


class Refused(Exception):
    pass


def check_code(code):
    if len(code) > 4000:
        raise Refused('code too long')
    tree = ast.parse(code, mode='exec')
    for node in ast.walk(tree):
        if isinstance(node, DENIED_NODES):
            raise Refused(f'{type(node).__name__} is not allowed')
        if isinstance(node, ast.Name) and node.id.startswith('_'):
            raise Refused('private names are not allowed')
        if isinstance(node, ast.Attribute):
            name = node.attr
            if name.startswith('_') or name in DENIED_ATTRS or name.startswith('read_') \
                    or (name.startswith('to_') and name not in ALLOWED_TO):
                raise Refused(f'.{name} is not allowed')
    return tree


def toolbox(pd, np):
    pd_safe = SimpleNamespace(**{n: getattr(pd, n) for n in (
        'to_datetime', 'to_numeric', 'Grouper', 'cut', 'qcut', 'concat', 'DataFrame', 'Series',
        'Timedelta', 'Timestamp', 'DateOffset', 'NamedAgg', 'date_range', 'isna', 'notna')})
    np_safe = SimpleNamespace(**{n: getattr(np, n) for n in (
        'round', 'mean', 'median', 'sum', 'std', 'abs', 'where', 'nan', 'percentile', 'corrcoef',
        'polyfit', 'log', 'sqrt', 'maximum', 'minimum', 'arange', 'clip')})
    return pd_safe, np_safe


def to_table(result, pd):
    """Turn the result into {columns, rows} with plain JSON values."""
    if isinstance(result, pd.Series):
        name = result.name if result.name is not None else 'value'
        result = result.to_frame(name=str(name))
    if isinstance(result, pd.DataFrame):
        df = result
        # An unnamed whole-number index is just row numbers (for example after sort_values): leave it out.
        # A named or text index (a groupby key) is part of the answer, so it becomes a column.
        row_numbers = df.index.names == [None] and pd.api.types.is_integer_dtype(df.index)
        if not row_numbers:
            df = df.reset_index()
        df = df.head(MAX_ROWS)
        columns = [' / '.join(map(str, c)) if isinstance(c, tuple) else str(c) for c in df.columns]
        rows = [[plain(v, pd) for v in row] for row in df.itertuples(index=False, name=None)]
        return {'columns': columns, 'rows': rows, 'truncated': len(result) > MAX_ROWS}
    return {'columns': ['result'], 'rows': [[plain(result, pd)]], 'truncated': False}


def plain(value, pd):
    if isinstance(value, (pd.Timestamp,)):
        return value.strftime('%Y-%m-%d')
    if isinstance(value, pd.Period):
        return str(value)
    if hasattr(value, 'item'):
        value = value.item()
    if isinstance(value, float):
        return None if math.isnan(value) else round(value, 2)
    if isinstance(value, (int, str, bool)) or value is None:
        return value
    return str(value)


def main():
    job = json.loads(sys.stdin.read())
    try:
        check_code(job['code'])
    except (Refused, SyntaxError) as exc:
        print(json.dumps({'ok': False, 'error': f'refused: {exc}'}))
        return

    import numpy as np
    import pandas as pd
    from asteval import Interpreter

    if job['kind'] == 'csv':
        df = pd.read_csv(job['path'], parse_dates=job.get('dates') or [])
    else:
        df = pd.read_excel(job['path'], sheet_name=job.get('sheet'), parse_dates=job.get('dates') or [])
    pd_safe, np_safe = toolbox(pd, np)

    interp = Interpreter(minimal=True, use_numpy=False, with_import=False, with_importfrom=False)
    for name in ('open', 'eval', 'exec', 'compile', 'getattr', 'setattr', 'delattr', 'globals', 'locals', 'vars', 'dir', 'input'):
        interp.symtable.pop(name, None)
    interp.symtable.update({'df': df, 'pd': pd_safe, 'np': np_safe})
    interp(job['code'])
    if interp.error:
        print(json.dumps({'ok': False, 'error': interp.error[0].get_error()[1][:300]}))
        return
    if 'result' not in interp.symtable:
        print(json.dumps({'ok': False, 'error': 'the code did not set `result`'}))
        return
    print(json.dumps({'ok': True, 'table': to_table(interp.symtable['result'], pd)}))


if __name__ == '__main__':
    main()
