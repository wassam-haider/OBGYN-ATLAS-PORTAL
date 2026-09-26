"""
add_portal_nav.py
Adds a '🏠 Portal' button to the nav-actions of newly generated atlas HTML files
that don't already have a portal link.
"""

import os

WEB_DOCS = os.path.join(os.path.dirname(__file__), "web_docs")

# Existing original 9 files (already have portal nav or are the portal itself)
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

PORTAL_BUTTON = '<a href="index.html" class="btn-header" style="text-decoration:none;" title="Back to Portal">🏠 Portal</a>'

def add_portal_link(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has portal link
    if 'index.html' in content or 'portal.html' in content:
        print(f"  [SKIP] Already has portal link: {os.path.basename(html_path)}")
        return

    # Inject the portal button into nav-actions, before the Theme button
    target = '<button class="btn-header" onclick="toggleTheme()"'
    if target not in content:
        print(f"  [WARN] Could not find nav-actions target in: {os.path.basename(html_path)}")
        return

    content = content.replace(target, PORTAL_BUTTON + '\n            ' + target, 1)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  [OK] Portal link added: {os.path.basename(html_path)}")


def main():
    print("Adding portal navigation links to new atlas files...\n")
    count = 0
    for f in sorted(os.listdir(WEB_DOCS)):
        if not f.endswith('.html'):
            continue
        if f in SKIP_FILES:
            continue
        html_path = os.path.join(WEB_DOCS, f)
        add_portal_link(html_path)
        count += 1
    print(f"\nProcessed {count} files.")


if __name__ == '__main__':
    main()
