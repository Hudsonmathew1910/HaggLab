import os
import sys
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent

VIEWPORTS = {
    '1440': {'width': 1440, 'height': 900},
    '768': {'width': 768, 'height': 1024},
    '390': {'width': 390, 'height': 844},
}

KEY_PAGES = [
    ('home', '/'),
    ('solutions_hub', '/solutions/'),
    ('solution_doc_assistant', '/solutions/answer-customers-staff-faster/'),
    ('projects_hub', '/projects/'),
    ('project_documind', '/projects/documind/'),
    ('process', '/process/'),
    ('security', '/security/'),
    ('about', '/about/'),
    ('faq', '/faq/'),
    ('start', '/start/'),
    ('hire', '/hire/'),
    ('privacy', '/privacy/'),
    ('terms', '/terms/'),
]

def capture_site(base_url, output_dir, viewports=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if viewports is None:
        viewports = VIEWPORTS

    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        for vp_name, vp_size in viewports.items():
            print(f"Capturing viewport {vp_name} ({vp_size['width']}x{vp_size['height']})...")
            context = browser.new_context(
                viewport={'width': vp_size['width'], 'height': vp_size['height']},
                device_scale_factor=1,
            )
            page = context.new_page()
            
            for slug, path in KEY_PAGES:
                url = f"{base_url.rstrip('/')}{path}"
                filename = f"{slug}_{vp_name}.webp"
                filepath = output_dir / filename
                try:
                    page.goto(url, wait_until='networkidle', timeout=15000)
                    # Trigger scroll reveals so full-page screenshot renders all cards
                    page.evaluate("() => { document.querySelectorAll('.reveal-on-scroll').forEach(el => el.classList.add('is-revealed')); }")
                    page.wait_for_timeout(200)
                    page.screenshot(path=str(filepath), full_page=True, type='webp')
                    print(f"  [OK] {slug} -> {filepath.name}")
                except Exception as e:
                    print(f"  [ERR] {slug} ({url}): {e}")
                    
            context.close()
        browser.close()

def main():
    parser = argparse.ArgumentParser(description="Capture screenshots of HaggLab pages")
    parser.add_argument('--base-url', default='http://127.0.0.1:8000', help='Base URL of running site')
    parser.add_argument('--dest', default='docs/design/before', help='Destination folder relative to project root')
    parser.add_argument('--viewports', nargs='*', default=['1440', '768', '390'], help='Viewports to capture')
    
    args = parser.parse_args()
    
    dest_path = BASE_DIR / args.dest
    selected_vps = {k: VIEWPORTS[k] for k in args.viewports if k in VIEWPORTS}
    
    print(f"Starting capture to {dest_path}...")
    capture_site(args.base_url, dest_path, selected_vps)
    print("Done!")

if __name__ == '__main__':
    main()
