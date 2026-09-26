"""
inject_images.py
Injects a visual image gallery section into HTML atlas pages that have companion image folders.
"""

import os
import re

# Map: HTML filename → image folder name
IMAGE_MAPPINGS = {
    "MASTER RCOG OBSTETRIC DELIVERY ATLAS.html": "images for MASTER RCOG OBSTETRIC DELIVERY ATLAS",
    "MRCOG Part 3 OSCE \u2014 EARLY PREGNANCY ATLAS.html": "images for MRCOG Part 3 OSCE \u2014 EARLY PREGNANCY ATLAS",
    "OBGYN OPD PROCEDURES \u2014 COMPLETE LIST.html": "images for OBGYN OPD PROCEDURES \u2014 COMPLETE LIST",
}

base = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(base)
WEB_DOCS = os.path.join(parent, "obgyn_portal", "web_docs")
if not os.path.exists(WEB_DOCS):
    for cand in [os.path.join(base, "web_docs"), "obgyn_portal/web_docs", "web_docs"]:
        if os.path.exists(cand):
            WEB_DOCS = cand
            break

GALLERY_CSS = """
<style>
/* Image Gallery Styles */
.image-gallery-section {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: var(--shadow-sm);
    overflow: hidden;
}
.gallery-top-bar {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.gallery-icon {
    font-size: 22px;
}
.gallery-title {
    font-family: var(--font-head);
    font-size: 15px;
    font-weight: 800;
    color: #ffffff;
}
.gallery-subtitle {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 2px;
}
.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
    padding: 20px;
}
.gallery-item {
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    overflow: hidden;
    background: var(--bg-primary);
    transition: box-shadow 0.2s, transform 0.2s;
    cursor: pointer;
}
.gallery-item:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}
.gallery-item img {
    width: 100%;
    height: 220px;
    object-fit: contain;
    background: #f8fafc;
    display: block;
    padding: 8px;
}
[data-theme="dark"] .gallery-item img {
    background: #0f172a;
}
.gallery-item-label {
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    border-top: 1px solid var(--border-subtle);
    text-align: center;
}

/* Lightbox */
.lightbox-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.92);
    z-index: 9999;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 16px;
}
.lightbox-overlay.active {
    display: flex;
}
.lightbox-img {
    max-width: 90vw;
    max-height: 80vh;
    object-fit: contain;
    border-radius: 8px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.8);
}
.lightbox-controls {
    display: flex;
    align-items: center;
    gap: 16px;
}
.lightbox-btn {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    color: #fff;
    padding: 8px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
}
.lightbox-btn:hover {
    background: rgba(255,255,255,0.3);
}
.lightbox-counter {
    color: #cbd5e1;
    font-size: 13px;
    font-weight: 600;
    min-width: 80px;
    text-align: center;
}
.lightbox-close {
    position: fixed;
    top: 20px;
    right: 24px;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: #fff;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    font-size: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
}
.lightbox-close:hover {
    background: rgba(239,68,68,0.6);
}
</style>
"""

GALLERY_JS = """
<script>
// Image Gallery Lightbox
(function() {
    let lbImages = [];
    let lbIndex = 0;

    function openLightbox(imgs, idx) {
        lbImages = imgs;
        lbIndex = idx;
        updateLightbox();
        document.getElementById('lb-overlay').classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        document.getElementById('lb-overlay').classList.remove('active');
        document.body.style.overflow = '';
    }

    function updateLightbox() {
        document.getElementById('lb-img').src = lbImages[lbIndex];
        document.getElementById('lb-counter').textContent = (lbIndex + 1) + ' / ' + lbImages.length;
    }

    window.galleryNext = function() {
        lbIndex = (lbIndex + 1) % lbImages.length;
        updateLightbox();
    };
    window.galleryPrev = function() {
        lbIndex = (lbIndex - 1 + lbImages.length) % lbImages.length;
        updateLightbox();
    };
    window.closeLightbox = closeLightbox;

    document.addEventListener('DOMContentLoaded', function() {
        var items = document.querySelectorAll('.gallery-item');
        var imgSrcs = Array.from(items).map(function(el) {
            return el.querySelector('img').src;
        });
        items.forEach(function(item, idx) {
            item.addEventListener('click', function() {
                openLightbox(imgSrcs, idx);
            });
        });

        document.addEventListener('keydown', function(e) {
            var overlay = document.getElementById('lb-overlay');
            if (overlay && overlay.classList.contains('active')) {
                if (e.key === 'ArrowRight') galleryNext();
                else if (e.key === 'ArrowLeft') galleryPrev();
                else if (e.key === 'Escape') closeLightbox();
            }
        });
    });
})();
</script>
"""

LIGHTBOX_HTML = """
<!-- LIGHTBOX -->
<div class="lightbox-overlay" id="lb-overlay">
    <button class="lightbox-close" onclick="closeLightbox()">✕</button>
    <img class="lightbox-img" id="lb-img" src="" alt="Clinical Image">
    <div class="lightbox-controls">
        <button class="lightbox-btn" onclick="galleryPrev()">← Previous</button>
        <span class="lightbox-counter" id="lb-counter">1 / 1</span>
        <button class="lightbox-btn" onclick="galleryNext()">Next →</button>
    </div>
</div>
"""

def build_gallery_html(folder_name, image_files):
    items_html = ""
    for i, img in enumerate(image_files, 1):
        img_src = f"{folder_name}/{img}"
        label = f"Figure {i}"
        items_html += f"""
        <div class="gallery-item">
            <img src="{img_src}" alt="{label}" loading="lazy">
            <div class="gallery-item-label">{label}</div>
        </div>"""

    return f"""
    <!-- IMAGE GALLERY SECTION -->
    <div class="image-gallery-section" id="gallery-section">
        <div class="gallery-top-bar">
            <span class="gallery-icon">🖼️</span>
            <div>
                <div class="gallery-title">Clinical Figures & Reference Diagrams</div>
                <div class="gallery-subtitle">{len(image_files)} high-yield images — click any image to enlarge</div>
            </div>
        </div>
        <div class="gallery-grid">
            {items_html}
        </div>
    </div>"""


def inject_gallery(html_path, folder_name):
    """Inject the gallery into the HTML file's reader section."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already injected
    if 'image-gallery-section' in content:
        print(f"  [SKIP] Gallery already injected: {html_path}")
        return

    # Get image files from the folder
    img_folder_path = os.path.join(WEB_DOCS, folder_name)
    if not os.path.exists(img_folder_path):
        print(f"  [WARN] Image folder not found: {img_folder_path}")
        return

    image_files = sorted([
        f for f in os.listdir(img_folder_path)
        if f.lower().endswith(('.jpeg', '.jpg', '.png', '.gif', '.webp'))
    ])

    if not image_files:
        print(f"  [WARN] No images found in: {img_folder_path}")
        return

    gallery_html = build_gallery_html(folder_name, image_files)

    # Inject gallery CSS before </head>
    content = content.replace('</head>', GALLERY_CSS + '\n</head>', 1)

    # Inject lightbox HTML after <body>
    body_pos = content.find('<body>')
    if body_pos != -1:
        insert_pos = body_pos + len('<body>')
        content = content[:insert_pos] + '\n' + LIGHTBOX_HTML + '\n' + content[insert_pos:]

    # Inject gallery JS before </body>
    content = content.replace('</body>', GALLERY_JS + '\n</body>', 1)

    # Inject gallery section right after the reader-hero div (the opening hero block ends)
    # Look for the end of the reader-hero block
    hero_end = content.find('</div>', content.find('reader-hero-meta'))
    if hero_end == -1:
        # Fallback: inject before first section card
        inject_before = '<div class="part-card"'
        idx = content.find(inject_before)
        if idx != -1:
            content = content[:idx] + gallery_html + '\n                ' + content[idx:]
        else:
            print(f"  [WARN] Could not find injection point in: {html_path}")
            return
    else:
        # Find the closing </div> of reader-hero-meta, then the closing </div> of reader-hero
        meta_end = content.find('</div>', hero_end) + len('</div>')
        content = content[:meta_end] + '\n' + gallery_html + content[meta_end:]

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  [OK] Gallery injected ({len(image_files)} images): {os.path.basename(html_path)}")


def main():
    print("Injecting image galleries into atlas HTML files...\n")
    for html_name, folder_name in IMAGE_MAPPINGS.items():
        html_path = os.path.join(WEB_DOCS, html_name)
        if not os.path.exists(html_path):
            # Try to find by normalized name
            for f in os.listdir(WEB_DOCS):
                if html_name.lower() in f.lower() or f.lower() in html_name.lower():
                    html_path = os.path.join(WEB_DOCS, f)
                    break
        if not os.path.exists(html_path):
            print(f"  [MISS] HTML not found: {html_name}")
            continue
        inject_gallery(html_path, folder_name)

    print("\nDone.")


if __name__ == '__main__':
    main()
