import re
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FONTS_DIR = BASE_DIR / 'static' / 'fonts'
FONTS_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

URL = 'https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap'

def main():
    print("Fetching font CSS from Google Fonts API...")
    res = requests.get(URL, headers={'User-Agent': USER_AGENT})
    if res.status_code != 200:
        print(f"Failed to fetch fonts: {res.status_code}")
        return

    css = res.text
    blocks = re.findall(r'/\* ([^*]+) \*/\s*(@font-face\s*\{[^}]+\})', css)
    
    font_face_rules = []
    downloaded_urls = {}

    for subset, block in blocks:
        if 'latin' not in subset:
            continue

        family_m = re.search(r"font-family:\s*['\"]?([^'\";]+)['\"]?", block)
        style_m = re.search(r"font-style:\s*([^;]+);", block)
        weight_m = re.search(r"font-weight:\s*([^;]+);", block)
        src_m = re.search(r"url\((https://[^)]+\.woff2)\)", block)

        if not (family_m and style_m and weight_m and src_m):
            continue

        family = family_m.group(1)
        style = style_m.group(1).strip()
        weight = weight_m.group(1).strip()
        url = src_m.group(1)

        clean_family = family.replace(" ", "").lower()
        clean_name = f"{clean_family}-{weight}-{style}.woff2"
        font_path = FONTS_DIR / clean_name

        if url not in downloaded_urls:
            print(f"Downloading {clean_name}...")
            f_res = requests.get(url, headers={'User-Agent': USER_AGENT})
            if f_res.status_code == 200:
                with open(font_path, 'wb') as f:
                    f.write(f_res.content)
                downloaded_urls[url] = clean_name
            else:
                print(f"Failed {url}")
                continue

        local_file = downloaded_urls[url]
        local_rule = f"""@font-face {{
  font-family: '{family}';
  font-style: {style};
  font-weight: {weight};
  font-display: swap;
  src: url('/static/fonts/{local_file}') format('woff2');
}}"""
        if local_rule not in font_face_rules:
            font_face_rules.append(local_rule)

    css_path = BASE_DIR / 'static' / 'css' / 'fonts.css'
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write("/* Self-hosted fonts for HaggLab */\n\n" + "\n\n".join(font_face_rules) + "\n")
    print(f"Saved {len(font_face_rules)} font faces to {css_path}")

if __name__ == '__main__':
    main()
