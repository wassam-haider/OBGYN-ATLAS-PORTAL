# 🌐 OBGYN Portal Stuff (`obgyn_portal/`)

This directory contains the production web applications, interactive study atlases, portal dashboard, navigation injection scripts, and CSS/styling utilities for the MRCOG/FCPS clinical revision suite.

---

## 📁 Directory Structure

```text
obgyn_portal/
├── web_docs/              # 48 interactive HTML study modules + portal hubs + media
│   ├── index.html         # Main Clinical Portal dashboard (search, filters, category tabs)
│   ├── portal.html        # Secondary portal layout
│   ├── *.html             # 48 interactive HTML clinical atlas applications
│   ├── images for */      # Clinical diagrams, radiology scans, and procedure photographs
│   └── style.css          # Portal stylesheet
├── update_portal.py       # Catalog generator updating index.html & portal.html cards
├── add_portal_nav.py      # Navigation injector adding "🏠 Portal" buttons to atlas headers
├── fix_css.py             # CSS embedder ensuring inline theme & styling resilience
└── verify.py              # Verification & health-check script for portal modules
```

---

## 🚀 Key Portal Features
- **48 Interactive Modules**: Full syllabi covering early pregnancy, triage, high-risk obstetrics, oncology, urogynecology, and surgical maneuvers.
- **Active Recall Flashcards**: 3D flip card recall with category pills and keyboard controls.
- **Board Quiz**: Practice multiple-choice questions with answer keys and rationale.
- **Image Galleries & Lightbox**: Interactive visual galleries for surgical procedures, delivery drills, and diagnostic ultrasound scans.
- **Offline & Hosted**: Works completely offline or hosted on GitHub Pages.
