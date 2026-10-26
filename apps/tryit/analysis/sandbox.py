"""Start sandbox_runner.py in its own process and return its result."""
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

from . import datasets
from .sandbox_runner import Refused, check_code

logger = logging.getLogger(__name__)

RUNNER = Path(__file__).resolve().parent / 'sandbox_runner.py'
TIMEOUT_SECONDS = 10

SOURCES = {
    'retail-sales': {'path': str(datasets.DATA_DIR / 'insightdesk' / 'retail_sales.csv'), 'kind': 'csv', 'dates': ['date']},
    'cafe-orders': {'path': str(datasets.DATA_DIR / 'reportbot' / 'cafe_sales.xlsx'), 'kind': 'xlsx',
                    'sheet': 'Transactions', 'dates': ['date']},
}


class SandboxError(Exception):
    pass


def run(table_key, code):
    """Run pandas code against a table. Returns {columns, rows, truncated}."""
    try:
        check_code(code)  # refuse early, before starting a process
    except (Refused, SyntaxError) as exc:
        raise SandboxError(f'refused: {exc}') from exc
    job = dict(SOURCES[table_key], code=code)
    # A minimal environment: no Django settings, no API keys
    env = {k: os.environ[k] for k in ('SYSTEMROOT', 'PATH', 'TEMP', 'TMP') if k in os.environ}
    env['OPENBLAS_NUM_THREADS'] = '1'
    try:
        proc = subprocess.run([sys.executable, '-I', str(RUNNER)], input=json.dumps(job), capture_output=True,
                              text=True, timeout=TIMEOUT_SECONDS, env=env)
    except subprocess.TimeoutExpired as exc:
        raise SandboxError('the calculation took too long') from exc
    try:
        out = json.loads(proc.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError) as exc:
        logger.warning('Sandbox produced no result: %s', proc.stderr[-300:])
        raise SandboxError('the calculation failed') from exc
    if not out.get('ok'):
        raise SandboxError(out.get('error', 'the calculation failed'))
    return out['table']
