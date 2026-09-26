# ⚕️ OBGYN Master Clinical Suite & Atlas Portal

Interactive Clinical Study, Examination Revision, and AI Knowledge Suite for MRCOG & FCPS Candidates.

---

## 🌐 Live Hosted Portal (GitHub Pages)
- **Hosted Portal URL**: [https://wassam-haider.github.io/OBGYN-ATLAS-PORTAL/](https://wassam-haider.github.io/OBGYN-ATLAS-PORTAL/)
- **Local Access**: Open [index.html](file:///c:/bhabhi%20mcpc/mcps/index.html) or [obgyn_portal/web_docs/index.html](file:///c:/bhabhi%20mcpc/mcps/obgyn_portal/web_docs/index.html) in any web browser.

### 🔐 Clinical Access Credentials
- **Candidate Username**: `batool_zehra`
- **Access Password**: `GYDOC123`

---

## 🗂️ Clean Project Architecture

The repository is organized into four clean, dedicated subsystems:

```text
mcps/
├── 🌐 obgyn_portal/       # OBGYN PORTAL STUFF
│   ├── web_docs/          # 48 interactive HTML study modules, portal dashboard, & media
│   ├── update_portal.py   # Regenerate & update portal cards catalog
│   ├── add_portal_nav.py  # Inject navigation headers into study modules
│   ├── fix_css.py         # Ensure inline styles & responsive theme support
│   └── verify.py          # Portal verification & health-check runner
│
├── 📚 obgyn_data/         # OBGYN DATA STUFF
│   ├── all docs/          # 48 markdown clinical study notes & reference tables
│   │   ├── *.md           # Clinical study notes
│   │   └── images for */  # Clinical images, ultrasound scans, & operative photographs
│   └── allchats.xlsx      # Clinical transcript & dialogue reference spreadsheet
│
├── ⚡ workflow_agents/    # WORKFLOW AGENT STUFF
│   ├── build_atlas.py     # Automated engine converting notes into interactive HTML
│   └── inject_images.py   # Automated image gallery & lightbox injector
│
├── 🤖 rag_chatbot/        # RAG CHATBOT STUFF
│   ├── rag_pipeline.py    # Text normalizer, TSV converter, & context-enriched chunker
│   ├── analyze_corpus.py  # Structural analysis & pattern scanner
│   ├── detailed_stats.py  # Statistical distributions (lines, words, tokens)
│   └── corpus_report_clean_utf8.md # Empirical corpus report
│
├── .agents/               # IDE Workspace Customizations & Skills (Atlas Builder)
├── index.html             # Production redirect entrypoint to obgyn_portal/web_docs/index.html
└── .nojekyll              # GitHub Pages static asset routing configuration
```

---

## ⚡ Core Workflows

### 1. Build / Update Interactive Atlases
To convert any raw note into an interactive HTML application:
```powershell
python workflow_agents/build_atlas.py "obgyn_data/all docs/YOUR_NOTE.md"
```
Or to batch convert all notes:
```powershell
python workflow_agents/build_atlas.py
```

### 2. Verify Portal Modules
To check all 48 modules, galleries, and portal navigation:
```powershell
python obgyn_portal/verify.py
```
