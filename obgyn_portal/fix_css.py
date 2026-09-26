"""
fix_css.py
Patches the 39 new atlas HTML files to embed the full CSS inline
instead of relying on the stub style.css external file.
"""

import os
import sys

base = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(base)
# Add workflow_agents and parent to sys.path
sys.path.insert(0, os.path.join(parent, "workflow_agents"))
sys.path.insert(0, base)
from build_atlas import CSS_TEMPLATE

WEB_DOCS = os.path.join(base, "web_docs")

# Original 9 files that already have correct CSS — skip these
SKIP_FILES = {
    'index.html',
    'portal.html',
    'anatomy_interactive_atlas.html',
    'MASTER CLASSIFICATION OF GYNECOLOGICAL BUGS.html',
    'MASTER GYNAECOLOGY SIGNS, EponYMS, TRIADS, SYNDROMES & DIAGNOSTIC CRITERIA.html',
    'MASTER OBSTETRIC INVESTIGATIONS & CUT-OFFS.html',
    'MASTER OBSTETRIC INVESTIGATIONS & CUT-OFFS2.html',
    'MASTER OBSTETRIC \u201cBUGS\u201d CATALOGUE.html',
    'MASTER RADIOLOGICAL SIGNS IN OBSTETRICS & GYNAECOLOGY.html',
    'MASTER \u2014 INVESTIGATION OF CHOICE IN GYNAECOLOGY.html',
    'rcog master table.html',
}

OLD_LINK = '<link rel="stylesheet" href="style.css">'
NEW_STYLE = f'<style>\n{CSS_TEMPLATE}\n    </style>'


def fix_file(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already fixed (has inline style tag with CSS vars)
    if '--bg-primary' in content and '<style>' in content and OLD_LINK not in content:
        print(f"  [SKIP] Already has inline CSS: {os.path.basename(html_path)}")
        return False

    if OLD_LINK not in content:
        print(f"  [WARN] No style.css link found: {os.path.basename(html_path)}")
        return False

    # Replace the external stylesheet link with inline CSS
    content = content.replace(OLD_LINK, NEW_STYLE, 1)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True


def main():
    print(f"Fixing CSS in new atlas HTML files...\n")
    fixed = 0
    skipped = 0

    for fname in sorted(os.listdir(WEB_DOCS)):
        if not fname.endswith('.html'):
            continue
        if fname in SKIP_FILES:
            continue

        html_path = os.path.join(WEB_DOCS, fname)
        result = fix_file(html_path)
        if result:
            print(f"  [OK] Fixed: {fname}")
            fixed += 1
        else:
            skipped += 1

    print(f"\nFixed: {fixed} | Skipped/Already OK: {skipped}")


if __name__ == '__main__':
    main()
