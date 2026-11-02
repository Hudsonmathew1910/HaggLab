"""
Check the site's Python packages, any time:

    python scripts/security_check.py          (run it with the project venv's python)

1. Known vulnerabilities: pip-audit checks every installed package against the public vulnerability database.
2. Updates: lists the packages from requirements.txt that have a newer version.

To update a package:  python -m pip install -U <name>   then run the tests:  python manage.py test
If all is well, raise its minimum version in requirements.txt and deploy.
GitHub also runs the scan every Monday (.github/workflows/security.yml) and Dependabot opens update pull requests.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def site_packages():
    names = set()
    for line in (ROOT / 'requirements.txt').read_text(encoding='utf-8').splitlines():
        line = line.split('#')[0].strip()
        if line:
            names.add(re.split(r'[<>=~!\[; ]', line)[0].lower().replace('_', '-'))
    return names


def main():
    print('1. Known vulnerabilities (pip-audit)\n', flush=True)
    try:
        audit = subprocess.run([sys.executable, '-m', 'pip_audit', '--progress-spinner', 'off'], cwd=ROOT)
    except FileNotFoundError:
        audit = None
    if audit is None or audit.returncode not in (0, 1):
        print('pip-audit is not installed in this Python. Install it with:  python -m pip install pip-audit')
        found_vulns = None
    else:
        found_vulns = audit.returncode == 1

    print('\n2. Newer versions of the site\'s packages\n')
    out = subprocess.run([sys.executable, '-m', 'pip', 'list', '--outdated', '--format', 'json',
                          '--disable-pip-version-check'], capture_output=True, text=True, cwd=ROOT)
    wanted = site_packages()
    rows = [p for p in json.loads(out.stdout or '[]') if p['name'].lower().replace('_', '-') in wanted]
    if rows:
        for p in rows:
            print(f"  {p['name']:<20} {p['version']:<10} -> {p['latest_version']}")
    else:
        print('  All up to date.')

    print()
    if found_vulns:
        print('RESULT: vulnerable packages found. Update the ones listed above, run the tests, then deploy.')
        return 1
    if found_vulns is None:
        print('RESULT: vulnerability scan could not run (see above).')
        return 2
    print('RESULT: no known vulnerabilities.' + (' Some updates are available.' if rows else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
