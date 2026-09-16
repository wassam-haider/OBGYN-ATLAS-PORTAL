---
name: atlas-builder
description: Builds interactive, atlas-style HTML study apps from markdown and plaintext notes matching the design, styling, and interactivity of anatomy_interactive_atlas.html. Use whenever new .md notes are added to 'all docs' or when the user asks to convert notes into interactive atlases.
---

# Atlas Builder Skill

This skill provides an automated workflow to convert medical and study notes (`.md` or `.txt`) into interactive, standalone HTML study atlases that match the format, styling, and interactivity of `anatomy_interactive_atlas.html`.

## When to Use

- When the user adds new `.md` files to `all docs` or any other notes directory.
- When the user asks to "convert my notes", "update the atlas", "generate interactive atlas", or "re-run the atlas converter".
- When single or batch `.md` notes need to be transformed into interactive web apps with flashcards, quizzes, and mastery tracking.

## Interactive Atlas Features

Every generated `.html` atlas includes:
1. **📖 Atlas Reader**: Full syllabus with responsive cards, topic-by-topic checklists, styled zebra-striped tables with value pills, clinical callout banners (high-yield amber, informational teal), flow sequences (`➔`), section audio text-to-speech (`🔊 Listen`), and clipboard copy tools (`📋 Copy`).
2. **🗂️ Active Recall Flashcards**: 3D flip card recall with category pills, automatic shuffling, and keyboard shortcuts (`Space` to flip, `ArrowRight`/`ArrowLeft` to navigate).
3. **✍️ Board-Style Quiz**: Interactive multiple-choice questions with answer verification, scoring, and clinical explanations.
4. **⚡ High-Yield Drill / Summary Matrix**: Topic-specific rapid-review cards and matrices.
5. **🔍 Live Search**: Real-time keyword filtering across all sections and tables.
6. **📊 Mastery Progress Bar**: Persistent checkbox tracking saved to `localStorage` unique to each document.
7. **🌓 Dark/Light Theme**: Persistent theme switcher.
8. **🖨️ Clean Print Support**: Clean CSS media print styles hiding navigation bars.

## How to Run

### 1. Batch Convert All Notes in `all docs/`
Run the converter script from the workspace root:
```powershell
python build_atlas.py
```
This automatically discovers all `.md` files in `all docs/` and compiles their corresponding `.html` interactive atlases directly into `web_docs/`.

### 2. Convert a Single New File
When a user adds a new `.md` file, run:
```powershell
python build_atlas.py "all docs/MY_NEW_NOTE.md"
```
The resulting atlas is automatically saved into `web_docs/MY_NEW_NOTE.html`.

### 3. Specify a Custom Output Directory (Optional)
```powershell
python build_atlas.py --output-dir "custom_folder"
```

## Folder Structure
- `c:\bhabhi mcpc\mcps\all docs\`: Source markdown study notes (`.md`).
- `c:\bhabhi mcpc\mcps\web_docs\`: All compiled interactive HTML study atlases (`.html`), including `anatomy_interactive_atlas.html`.
- `c:\bhabhi mcpc\mcps\build_atlas.py`: Automated generator script.
- `c:\bhabhi mcpc\mcps\allchats.xlsx`: User spreadsheet reference.

## Script Location & Architecture
- **Script**: `c:\bhabhi mcpc\mcps\build_atlas.py`
- **Zero External Dependencies**: Pure Python standard library (`re`, `html`, `json`, `argparse`, `os`, `sys`). Works on any Python 3 environment.
- **Source Notes Directory**: `c:\bhabhi mcpc\mcps\all docs/`
