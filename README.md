# OBGYN-ATLAS-PORTAL

Interactive Clinical Study & Revision Suite for MRCOG & FCPS Candidates.

## 🌐 Live Hosted Portal (GitHub Pages)
Once GitHub Pages is enabled on this repository:
- **Hosted Portal URL**: [https://wassam-haider.github.io/OBGYN-ATLAS-PORTAL/](https://wassam-haider.github.io/OBGYN-ATLAS-PORTAL/)

### 🔐 Clinical Access Credentials
- **Candidate Username**: `batool_zehra`
- **Access Password**: `GYDOC123`

---

## 📚 Included Interactive Atlases

1. **Master OBGYN Anatomy, Histology, Embryology & Physiology** (`anatomy_interactive_atlas.html`)
2. **Master Classification of Gynecological Bugs** (`MASTER CLASSIFICATION OF GYNECOLOGICAL BUGS.html`)
3. **Master Gynaecology Signs, Eponyms, Triads & Diagnostic Criteria** (`MASTER GYNAECOLOGY SIGNS, EponYMS, TRIADS, SYNDROMES & DIAGNOSTIC CRITERIA.html`)
4. **Master Obstetric Investigations & Diagnostic Cut-Offs** (`MASTER OBSTETRIC INVESTIGATIONS & CUT-OFFS.html`)
5. **Master Consolidated Obstetric Signs, Eponyms & Diagnostic Criteria** (`MASTER OBSTETRIC INVESTIGATIONS & CUT-OFFS2.html`)
6. **Master Obstetric “Bugs” Catalogue** (`MASTER OBSTETRIC “BUGS” CATALOGUE.html`)
7. **Master Radiological Signs in Obstetrics & Gynaecology** (`MASTER RADIOLOGICAL SIGNS IN OBSTETRICS & GYNAECOLOGY.html`)
8. **Master Investigation of Choice in Gynaecology** (`MASTER — INVESTIGATION OF CHOICE IN GYNAECOLOGY.html`)
9. **RCOG Master Table — Ideal Time of Delivery** (`rcog master table.html`)

---

## ⚡ Features
- **Interactive Checklists**: Topic-by-topic checkboxes with persistent `localStorage` progress tracking.
- **Active Recall Flashcards**: 3D perspective flip cards with category badges and keyboard navigation.
- **Board Quiz**: Multiple-choice questions with answer feedback and clinical explanations.
- **High-Yield Drill Matrix**: Rapid exam revision tables.
- **Audio TTS**: Listen to any section with built-in text-to-speech.
- **Dark/Light Mode**: Full theme customization.

---

## 🛠️ Automated Note Conversion
To compile new `.md` study notes into interactive HTML atlases:
```powershell
python build_atlas.py "all docs/NEW_NOTE.md"
```
Output is automatically written to `web_docs/`.
