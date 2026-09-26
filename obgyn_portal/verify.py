import os, re

base = os.path.dirname(os.path.abspath(__file__))
web_docs = os.path.join(base, "web_docs") if os.path.exists(os.path.join(base, "web_docs")) else "web_docs"

# Count all atlas HTML files
atlas_files = [f for f in os.listdir(web_docs) if f.endswith('.html') and f not in ['index.html','portal.html']]
print(f'Total atlas HTML files: {len(atlas_files)}')

# Check index.html has the right count
with open(f'{web_docs}/index.html', 'r', encoding='utf-8') as f:
    idx = f.read()
count_match = re.search(r'All Modules \((\d+)\)', idx)
print(f'Index.html shows: All Modules ({count_match.group(1) if count_match else "NOT FOUND"})')

# Check a new file has portal link
test = 'MASTER RCOG OBSTETRIC DELIVERY ATLAS.html'
with open(f'{web_docs}/{test}', 'r', encoding='utf-8') as f:
    content = f.read()
print(f'{test}:')
print(f'  Has portal link: {"index.html" in content}')
print(f'  Has image gallery: {"image-gallery-section" in content}')
print(f'  Has lightbox: {"lightbox" in content}')

# Count gallery items
gallery_count = content.count('class="gallery-item"')
print(f'  Gallery items: {gallery_count}')

# Check early pregnancy atlas for gallery
test2 = 'MRCOG Part 3 OSCE \u2014 EARLY PREGNANCY ATLAS.html'
with open(f'{web_docs}/{test2}', 'r', encoding='utf-8') as f:
    content2 = f.read()
print(f'Early Pregnancy Atlas:')
print(f'  Has gallery: {"image-gallery-section" in content2}')
img_count2 = content2.count('class="gallery-item"')
print(f'  Gallery items: {img_count2}')

# Check OPD procedures atlas
test3 = 'OBGYN OPD PROCEDURES \u2014 COMPLETE LIST.html'
with open(f'{web_docs}/{test3}', 'r', encoding='utf-8') as f:
    content3 = f.read()
print(f'OPD Procedures Atlas:')
print(f'  Has gallery: {"image-gallery-section" in content3}')
img_count3 = content3.count('class="gallery-item"')
print(f'  Gallery items: {img_count3}')

# Count new files vs old
old_files = {
    'MASTER CLASSIFICATION OF GYNECOLOGICAL BUGS.html',
    'MASTER GYNAECOLOGY SIGNS, EponYMS, TRIADS, SYNDROMES & DIAGNOSTIC CRITERIA.html',
    'MASTER OBSTETRIC INVESTIGATIONS & CUT-OFFS.html',
    'MASTER OBSTETRIC INVESTIGATIONS & CUT-OFFS2.html',
    'MASTER OBSTETRIC \u201cBUGS\u201d CATALOGUE.html',
    'MASTER RADIOLOGICAL SIGNS IN OBSTETRICS & GYNAECOLOGY.html',
    'MASTER \u2014 INVESTIGATION OF CHOICE IN GYNAECOLOGY.html',
    'rcog master table.html',
    'anatomy_interactive_atlas.html',
}
new_files = [f for f in atlas_files if f not in old_files]
print(f'New atlas files added: {len(new_files)}')
print('All done!')
