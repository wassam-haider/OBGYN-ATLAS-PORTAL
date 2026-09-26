import os, sys, glob, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

all_docs = 'all docs'
all_files = []
for root, dirs, files in os.walk(all_docs):
    for f in files:
        if f.endswith('.md') or f.startswith('gestational-age'):
            all_files.append(os.path.join(root, f))
all_files = sorted(set(all_files))

print(f"Total analyzed files: {len(all_files)}")

num_sec_re = re.compile(r'^\s*(\d+)\.\s+([A-Z0-9\s,\'\"&\—\-/–()]+)$', re.MULTILINE)
tab_re = re.compile(r'\t')
pipe_re = re.compile(r'\|')
bullet_re = re.compile(r'^\s*[-*•]\s', re.MULTILINE)
numlist_re = re.compile(r'^\s*\d+[.)]\s', re.MULTILINE)
md_heading_re = re.compile(r'^#{1,6}\s', re.MULTILINE)
bold_re = re.compile(r'\*\*.*?\*\*')
italic_re = re.compile(r'(?<!\*)\*[^*\n]+\*(?!\*)')
img_re = re.compile(r'!\[.*?\]\(.*?\)')
link_re = re.compile(r'(?<!!)\[.*?\]\(.*?\)')
code_re = re.compile(r'```|`[^`]+`')
html_re = re.compile(r'<[a-zA-Z\/][^>]*>')
qa_re = re.compile(r'(?:^|\n)\s*(?:Q:|Question:|A:|Answer:|Scenario:|Candidate:)', re.IGNORECASE)

file_stats = []
total_lines = 0
total_words = 0

for p in all_files:
    with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
        txt = fp.read()
    lines = txt.splitlines()
    words = len(txt.split())
    total_lines += len(lines)
    total_words += words
    
    num_secs = num_sec_re.findall(txt)
    tabs = len(tab_re.findall(txt))
    pipes = len(pipe_re.findall(txt))
    md_heads = len(md_heading_re.findall(txt))
    bullets = len(bullet_re.findall(txt))
    numlists = len(numlist_re.findall(txt))
    bolds = len(bold_re.findall(txt))
    italics = len(italic_re.findall(txt))
    imgs = len(img_re.findall(txt))
    links = len(link_re.findall(txt))
    codes = len(code_re.findall(txt))
    htmls = len(html_re.findall(txt))
    qas = len(qa_re.findall(txt))
    
    file_stats.append({
        'name': os.path.basename(p),
        'path': p,
        'lines': len(lines),
        'words': words,
        'tokens_est': int(words * 1.3),
        'md_heads': md_heads,
        'num_secs': len(num_secs),
        'tabs': tabs,
        'pipes': pipes,
        'bullets': bullets,
        'numlists': numlists,
        'bolds': bolds,
        'italics': italics,
        'imgs': imgs,
        'links': links,
        'codes': codes,
        'htmls': htmls,
        'qas': qas,
        'sample_num_secs': [s[1].strip()[:50] for s in num_secs[:6]]
    })

print(f"Total corpus lines: {total_lines:,}")
print(f"Total corpus words: {total_words:,}")
print(f"Estimated corpus tokens: {int(total_words * 1.3):,}")

files_with_md_headings = [f for f in file_stats if f['md_heads'] > 0]
print(f"Files with standard Markdown headings (#): {len(files_with_md_headings)}")

files_with_tabs = [f for f in file_stats if f['tabs'] > 10]
print(f"Files with TSV tables (tabs > 10): {len(files_with_tabs)}")

files_with_pipes = [f for f in file_stats if f['pipes'] > 10]
print(f"Files with Markdown pipe tables (pipes > 10): {len(files_with_pipes)}")

files_with_numbered_secs = [f for f in file_stats if f['num_secs'] > 0]
print(f"Files with numbered pseudo-headings (1. TITLE): {len(files_with_numbered_secs)}")

files_with_bullets = [f for f in file_stats if f['bullets'] > 0]
print(f"Files with Markdown bullets (-/*): {len(files_with_bullets)}")

files_with_bolds = [f for f in file_stats if f['bolds'] > 0]
print(f"Files with Markdown bold (**): {len(files_with_bolds)}")

files_with_italics = [f for f in file_stats if f['italics'] > 0]
print(f"Files with Markdown italic (*): {len(files_with_italics)}")

files_with_imgs = [f for f in file_stats if f['imgs'] > 0]
print(f"Files with images (![]): {len(files_with_imgs)}")

files_with_html = [f for f in file_stats if f['htmls'] > 0]
print(f"Files with HTML tags (<...>): {len(files_with_html)}")

files_with_code = [f for f in file_stats if f['codes'] > 0]
print(f"Files with code blocks/ticks: {len(files_with_code)}")

lines_arr = sorted([f['lines'] for f in file_stats])
words_arr = sorted([f['words'] for f in file_stats])
tokens_arr = sorted([f['tokens_est'] for f in file_stats])

import statistics
print("\n--- DISTRIBUTIONS ---")
print(f"Lines: min={min(lines_arr)}, max={max(lines_arr)}, median={statistics.median(lines_arr)}, mean={statistics.mean(lines_arr):.1f}")
print(f"Words: min={min(words_arr)}, max={max(words_arr)}, median={statistics.median(words_arr)}, mean={statistics.mean(words_arr):.1f}")
print(f"Tokens (est): min={min(tokens_arr)}, max={max(tokens_arr)}, median={statistics.median(tokens_arr)}, mean={statistics.mean(tokens_arr):.1f}")

print("\n--- TOP NUMBERED HEADINGS ACROSS FILES ---")
for f in file_stats[:8]:
    print(f"\n{f['name']}: {f['num_secs']} numbered sections detected")
    for s in f['sample_num_secs']:
        print(f"   • {s}")
