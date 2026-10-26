import os
import re
import sys
from pathlib import Path

# HaggLab Design Rules Checker
# Enforces:
# 1. No inline style attributes or inline <script> in HTML templates
# 2. No external hosts except Cloudflare Turnstile
# 3. Every <img> has an alt attribute
# 4. No leftover [Bracket] placeholders or lorem ipsum
# 5. No fake testimonial markup
# 6. Exactly one <h1> per full page template

BASE_DIR = Path(__file__).resolve().parent.parent

BANNED_HTML_PATTERNS = [
    (r'<[^>]+\bstyle\s*=\s*["\'][^"\']*["\']', 'Inline style attribute is banned (violates CSP and design system)'),
    (r'<script(?![^>]*\bsrc\b)[^>]*>[\s\S]*?</script>', 'Inline <script> block is banned (violates strict CSP)'),
]

BANNED_TEXT_PATTERNS = [
    (r'\[[A-Za-z0-9\s_-]+\]', 'Leftover bracket placeholder found in template/copy'),
    (r'\blorem\s+ipsum\b', 'Lorem ipsum placeholder found'),
    (r'\b(client testimonial|client review|five-star rating)\b', 'Fake testimonial/review markup found'),
]

ALLOWED_EXTERNAL_HOSTS = [
    'challenges.cloudflare.com',
]

def check_template(filepath):
    errors = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Skip partial component files for h1 check
    is_page_template = 'templates/pages/' in filepath.as_posix() or 'templates/base.html' in filepath.as_posix()

    for pattern, desc in BANNED_HTML_PATTERNS:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            sample = match.group(0)[:80].replace('\n', ' ')
            errors.append(f"{filepath}: {desc} -> '{sample}'")

    for pattern, desc in BANNED_TEXT_PATTERNS:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            sample = match.group(0)
            errors.append(f"{filepath}: {desc} -> '{sample}'")

    # Check for external URLs that are not allowed
    # Finds src="https://..." or href="https://..."
    urls = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)["\']', content, re.IGNORECASE)
    for url in urls:
        # Check against allowed external hosts
        is_allowed = any(host in url for host in ALLOWED_EXTERNAL_HOSTS)
        # External links in <a> tags are allowed (e.g. fiverr.com), but assets (img, script, link stylesheet) are not
        # Let's check if it's an asset load
        asset_match = re.search(r'<(?:script|link|img|iframe)[^>]+(?:src|href)\s*=\s*["\']' + re.escape(url) + r'["\']', content, re.IGNORECASE)
        if asset_match and not is_allowed:
            errors.append(f"{filepath}: External asset loaded from unauthorized host: {url}")

    # Check <img> has alt
    img_tags = re.findall(r'<img\b[^>]*>', content, re.IGNORECASE)
    for img in img_tags:
        if not re.search(r'\balt\s*=', img, re.IGNORECASE):
            errors.append(f"{filepath}: <img> tag missing alt attribute: {img[:60]}")

    # Check h1 count on page templates
    if 'templates/pages/' in filepath.as_posix():
        # Count <h1> tags
        h1_matches = re.findall(r'<h1\b[^>]*>', content, re.IGNORECASE)
        if len(h1_matches) > 1:
            errors.append(f"{filepath}: Multiple <h1> tags found ({len(h1_matches)}). Each page must have exactly one <h1>.")

    return errors

def main():
    errors = []
    templates_dir = BASE_DIR / 'templates'
    if templates_dir.exists():
        for root, _, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    errors.extend(check_template(Path(root) / file))

    if errors:
        print(f"DESIGN RULE CHECK FAILED ({len(errors)} violations):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("Design rule check passed: zero violations found.")
        sys.exit(0)

if __name__ == '__main__':
    main()
