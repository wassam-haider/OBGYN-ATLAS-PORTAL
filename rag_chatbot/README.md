# 🤖 RAG Chatbot Stuff (`rag_chatbot/`)

This directory houses the RAG (Retrieval-Augmented Generation) pipeline, Chroma Cloud embedding scripts, interactive Streamlit teaching assistant, terminal chatbot, corpus analysis tools, and structural inspection reports.

---

## 📁 Contents

| File | Description |
| :--- | :--- |
| `app.py` | Modern Streamlit web application providing a conversational teaching interface with FCPS trainer persona, strict grounding, and source citation. |
| `chatbot.py` | Terminal-based interactive chatbot querying Chroma Cloud with L2 similarity threshold filtering and trainer prompt. |
| `embeder.py` | Batch embedding & upsert pipeline using OpenRouter (`openai/text-embedding-3-small`) to store documents into Chroma Cloud (`fcps_gyn_notes`). |
| `test.py` | Diagnostic script for inspecting Chroma Cloud collections, distances, and retrieval scores. |
| `rag_pipeline.py` | Deterministic rule-based ingestion & chunking pipeline (normalizes pseudo-headings, converts TSV tables, chunks clinical sections with context metadata into JSONL). |
| `analyze_corpus.py` | Structural scanner analyzing heading patterns, table formats, and boilerplate across all documents. |
| `detailed_stats.py` | Mathematical and statistical distribution generator (calculating min/max/median/mean line, word, and token counts). |
| `corpus_report_clean_utf8.md` | Clean markdown report documenting the empirical structure of the 48 medical documents. |
| `corpus_analysis_utf8.txt` | Detailed raw output from the corpus scanner. |
| `corpus_raw.txt` | Raw text diagnostic output. |

---

## ⚙️ Setup & Usage

### 1. Environment Configuration
Create a `.env` file in this directory (or repository root):
```env
OPENROUTER_API_KEY=sk-or-v1-...
CHROMA_API_KEY=...
CHROMA_TENANT=...
CHROMA_DATABASE=...
```

### 2. Run the Streamlit Chatbot Web App
```powershell
python -m streamlit run rag_chatbot/app.py
```

### 3. Run the Terminal Chatbot
```powershell
python rag_chatbot/chatbot.py
```

### 4. Embed & Upsert Chunks into Chroma Cloud
```powershell
python rag_chatbot/embeder.py
```
