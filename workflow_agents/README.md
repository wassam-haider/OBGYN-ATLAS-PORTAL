# ⚡ Workflow Agent Stuff (`workflow_agents/`)

This directory houses automated agent workflows, batch generation engines, and image injection pipelines that convert raw clinical markdown notes into production-ready interactive web applications.

---

## 📁 Directory Structure

```text
workflow_agents/
├── build_atlas.py         # Core Atlas Builder engine (compiles .md notes into interactive HTML)
├── inject_images.py       # Workflow tool injecting visual image galleries & lightboxes
└── README.md              # Workflow documentation and usage instructions
```

*(Note: Workspace customizations and IDE skill definitions reside in `.agents/skills/atlas-builder/` at the repository root to ensure automatic discovery by the Antigravity IDE).*

---

## 🛠️ Usage Instructions

### 1. Build Single Atlas
Convert a specific markdown note into an interactive HTML application:
```powershell
python workflow_agents/build_atlas.py "obgyn_data/all docs/YOUR_NOTE.md"
```
The output HTML file will be generated automatically in `obgyn_portal/web_docs/`.

### 2. Batch Build All Atlases
To batch-compile all notes located in `obgyn_data/all docs/`:
```powershell
python workflow_agents/build_atlas.py
```

### 3. Inject Visual Galleries
To link companion images from `obgyn_data/all docs/images for ...` into the corresponding HTML modules:
```powershell
python workflow_agents/inject_images.py
```
