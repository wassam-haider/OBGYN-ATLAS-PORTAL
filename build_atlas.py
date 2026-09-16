"""
Interactive Atlas Converter & Workflow Engine
=============================================
Converts study notes (.md / plaintext) into interactive, atlas-style HTML applications
matching the design, styling, and interactive features of anatomy_interactive_atlas.html.

Key Interactivity & Design Features:
- 📖 Atlas Reader: Organized section cards, breadcrumbs, pill tags, responsive typography
- 🗂️ Flashcards: 3D flip card recall with category tags, spacebar & arrow key navigation
- ✍️ Board Quiz: Interactive multiple-choice questions with answer tracking & explanations
- ⚡ High-Yield Drill: Document-specific rapid-review matrix & clinical tables
- 🔍 Live Search: Real-time filtering across all sections and tables
- 📊 Mastery Progress Bar: Topic-by-topic checkboxes with persistent localStorage
- 🔊 Speech Synthesis: One-click Text-to-Speech audio reading per section
- 📋 Copy Tools: Instant clipboard copying for single sections or entire atlas
- 🌓 Dark/Light Mode: Persistent theme toggle
- 🖨️ Clean Print: Print/PDF-ready styling with automatic nav hiding
"""

import os
import sys
import re
import json
import argparse
import html

CSS_TEMPLATE = """
:root {
    --bg-primary: #f8fafc;
    --bg-surface: #ffffff;
    --bg-card: #ffffff;
    --text-main: #0f172a;
    --text-muted: #475569;
    --text-light: #64748b;
    --brand-navy: #0f172a;
    --brand-blue: #1d4ed8;
    --brand-cobalt: #2563eb;
    --brand-teal: #0d9488;
    --brand-rose: #e11d48;
    --brand-amber: #d97706;
    --border-subtle: #e2e8f0;
    --border-strong: #cbd5e1;
    --highlight-bg: #fef08a;
    --badge-bg: #eff6ff;
    --badge-text: #1d4ed8;
    --badge-border: #bfdbfe;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
    --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);
    --font-main: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-head: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

[data-theme="dark"] {
    --bg-primary: #090d16;
    --bg-surface: #0f172a;
    --bg-card: #131d31;
    --text-main: #f1f5f9;
    --text-muted: #94a3b8;
    --text-light: #64748b;
    --brand-navy: #020617;
    --brand-blue: #3b82f6;
    --brand-cobalt: #60a5fa;
    --brand-teal: #14b8a6;
    --brand-rose: #f43f5e;
    --brand-amber: #f59e0b;
    --border-subtle: #1e293b;
    --border-strong: #334155;
    --highlight-bg: #854d0e;
    --badge-bg: #1e3a8a33;
    --badge-text: #93c5fd;
    --badge-border: #1e40af;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.4);
    --shadow-md: 0 4px 10px rgba(0,0,0,0.5);
    --shadow-lg: 0 10px 25px rgba(0,0,0,0.6);
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: var(--font-main);
    background-color: var(--bg-primary);
    color: var(--text-main);
    line-height: 1.6;
    transition: background-color 0.25s, color 0.25s;
}

/* APP TOP NAVBAR */
.app-nav {
    position: sticky;
    top: 0;
    z-index: 1000;
    background: rgba(15, 23, 42, 0.96);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,0.1);
    color: #ffffff;
    padding: 10px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}

.brand-block {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-logo {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, var(--brand-cobalt), var(--brand-teal));
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
    font-weight: 800;
    color: #ffffff;
    box-shadow: 0 2px 8px rgba(37,99,235,0.4);
}

.brand-title-text {
    font-family: var(--font-head);
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #ffffff;
}

.brand-subtitle-text {
    font-size: 11px;
    color: #94a3b8;
}

.nav-mode-tabs {
    display: flex;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 3px;
    gap: 2px;
}

.tab-btn {
    background: transparent;
    border: none;
    color: #94a3b8;
    padding: 7px 15px;
    font-size: 12.5px;
    font-weight: 600;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 6px;
}

.tab-btn:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.05);
}

.tab-btn.active {
    background: var(--brand-cobalt);
    color: #ffffff;
    box-shadow: 0 2px 6px rgba(37,99,235,0.35);
}

.nav-actions {
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-header {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #f8fafc;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 5px;
    transition: all 0.2s ease;
}

.btn-header:hover {
    background: rgba(255, 255, 255, 0.2);
}

/* PROGRESS & SEARCH SUBNAV */
.progress-subnav {
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border-subtle);
    padding: 10px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    position: sticky;
    top: 57px;
    z-index: 999;
    box-shadow: var(--shadow-sm);
}

.progress-track-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
    max-width: 420px;
}

.progress-count-text {
    font-size: 12px;
    font-weight: 700;
    color: var(--brand-cobalt);
    min-width: 140px;
}

.progress-bar-bg {
    flex: 1;
    height: 8px;
    background: var(--border-subtle);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, var(--brand-teal), var(--brand-cobalt));
    border-radius: 4px;
    transition: width 0.3s ease;
}

.filter-controls {
    display: flex;
    align-items: center;
    gap: 10px;
}

.search-input-box {
    position: relative;
    width: 280px;
}

.search-input-box input {
    width: 100%;
    padding: 6px 12px 6px 32px;
    font-size: 12.5px;
    border-radius: 6px;
    border: 1px solid var(--border-strong);
    background: var(--bg-primary);
    color: var(--text-main);
    outline: none;
    transition: border 0.2s, box-shadow 0.2s;
}

.search-input-box input:focus {
    border-color: var(--brand-cobalt);
    box-shadow: 0 0 0 3px rgba(37,99,235,0.15);
}

.search-icon {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 13px;
    color: var(--text-light);
}

/* APP MAIN LAYOUT */
.app-container {
    display: flex;
    min-height: calc(100vh - 110px);
}

/* SIDEBAR SYLLABUS */
.app-sidebar {
    width: 320px;
    flex-shrink: 0;
    background: var(--bg-surface);
    border-right: 1px solid var(--border-subtle);
    padding: 18px 16px;
    position: sticky;
    top: 108px;
    height: calc(100vh - 108px);
    overflow-y: auto;
}

.sidebar-heading {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--text-light);
    margin-bottom: 12px;
    padding-left: 6px;
}

.part-nav-list {
    list-style: none;
}

.part-nav-link {
    display: block;
    padding: 7px 10px;
    font-size: 12px;
    color: var(--text-muted);
    text-decoration: none;
    border-radius: 6px;
    transition: all 0.15s ease;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    border-left: 2px solid transparent;
}

.part-nav-link:hover {
    color: var(--brand-cobalt);
    background: var(--bg-primary);
    border-left-color: var(--brand-cobalt);
}

/* MAIN VIEW AREA */
.main-view-area {
    flex: 1;
    padding: 24px 36px;
    max-width: 1100px;
    margin: 0 auto;
    width: 100%;
}

/* READER HERO */
.reader-hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #ffffff;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 28px;
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
}

[data-theme="dark"] .reader-hero {
    background: linear-gradient(135deg, #020617 0%, #0f172a 100%);
    border: 1px solid var(--border-subtle);
}

.reader-hero-title {
    font-family: var(--font-head);
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.5px;
    line-height: 1.3;
    margin-bottom: 8px;
}

.reader-hero-sub {
    font-size: 13.5px;
    color: #94a3b8;
    font-weight: 500;
}

.reader-hero-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-top: 16px;
    padding-top: 14px;
    border-top: 1px solid rgba(255,255,255,0.1);
    font-size: 12px;
    color: #cbd5e1;
}

/* SECTION PART CARD */
.part-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
    overflow: hidden;
}

.part-card.section-mastered {
    border-color: rgba(16, 185, 129, 0.4);
}

.part-card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--border-strong);
}

.part-top-bar {
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border-subtle);
    padding: 14px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}

.part-title-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
}

.part-pill {
    background: var(--badge-bg);
    color: var(--badge-text);
    border: 1px solid var(--badge-border);
    font-size: 11px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 5px;
    font-family: var(--font-mono);
    white-space: nowrap;
}

.part-title {
    font-family: var(--font-head);
    font-size: 16px;
    font-weight: 700;
    color: var(--text-main);
    line-height: 1.4;
}

.part-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.btn-icon {
    background: var(--bg-primary);
    border: 1px solid var(--border-subtle);
    color: var(--text-muted);
    padding: 5px 10px;
    border-radius: 5px;
    font-size: 11.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
    display: flex;
    align-items: center;
    gap: 4px;
}

.btn-icon:hover {
    background: var(--brand-cobalt);
    color: #ffffff;
    border-color: var(--brand-cobalt);
}

.part-body {
    padding: 20px 24px;
}

/* TOPIC ROW & CHECKPOINT */
.topic-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    padding: 10px 12px;
    margin-top: 14px;
    margin-bottom: 8px;
    background: var(--bg-primary);
    border-left: 3px solid var(--brand-cobalt);
    border-radius: 0 6px 6px 0;
    transition: background-color 0.2s ease;
}

.topic-row.mastered-badge-active {
    background: rgba(16, 185, 129, 0.08);
    border-left-color: #10b981;
}

.topic-title-box {
    display: flex;
    align-items: center;
    gap: 10px;
}

.topic-badge {
    background: var(--brand-cobalt);
    color: #ffffff;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 4px;
    white-space: nowrap;
}

.topic-row.mastered-badge-active .topic-badge {
    background: #10b981;
}

.topic-heading {
    font-family: var(--font-head);
    font-size: 14.5px;
    font-weight: 700;
    color: var(--text-main);
}

.mastery-check-label {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-light);
    user-select: none;
    flex-shrink: 0;
}

.topic-checkbox {
    width: 16px;
    height: 16px;
    cursor: pointer;
    accent-color: #10b981;
}

/* LISTS & BULLETS */
.core-list {
    list-style: none;
    margin: 8px 0 12px 6px;
}

.core-bullet {
    display: flex;
    align-items: baseline;
    gap: 8px;
    font-size: 13.5px;
    margin-bottom: 6px;
    line-height: 1.55;
}

.bullet-icon {
    color: var(--brand-cobalt);
    font-size: 10px;
    flex-shrink: 0;
}

.sub-list {
    list-style: none;
    margin: 4px 0 8px 24px;
}

.sub-bullet {
    display: flex;
    align-items: baseline;
    gap: 8px;
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 4px;
    line-height: 1.5;
}

.sub-bullet-icon {
    color: var(--brand-teal);
    font-size: 10px;
    flex-shrink: 0;
}

.bullet-text {
    flex: 1;
}

/* STYLED TABLES */
.table-wrap {
    margin: 14px 0;
    overflow-x: auto;
    border-radius: 8px;
    border: 1px solid var(--border-subtle);
}

.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    text-align: left;
}

.styled-table thead tr {
    background: var(--bg-primary);
    border-bottom: 2px solid var(--border-strong);
}

.styled-table th {
    padding: 10px 14px;
    font-weight: 700;
    color: var(--text-main);
    font-size: 12.5px;
}

.styled-table td {
    padding: 9px 14px;
    border-bottom: 1px solid var(--border-subtle);
    color: var(--text-main);
    vertical-align: top;
}

.styled-table tbody tr:nth-child(even) {
    background: rgba(0,0,0,0.015);
}

[data-theme="dark"] .styled-table tbody tr:nth-child(even) {
    background: rgba(255,255,255,0.02);
}

.styled-table tr:hover {
    background: rgba(37,99,235,0.04);
}

.val-pill {
    display: inline-block;
    background: var(--badge-bg);
    color: var(--badge-text);
    border: 1px solid var(--badge-border);
    padding: 2px 7px;
    border-radius: 4px;
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 600;
}

/* CALLOUTS */
.atlas-callout {
    border-radius: 8px;
    padding: 12px 16px;
    margin: 12px 0;
    border-left: 4px solid;
    font-size: 13px;
    line-height: 1.5;
}

.callout-highyield {
    background: rgba(217, 119, 6, 0.08);
    border-left-color: var(--brand-amber);
}

.callout-highyield .callout-tag {
    color: var(--brand-amber);
    font-weight: 700;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
}

.callout-info {
    background: rgba(13, 148, 136, 0.08);
    border-left-color: var(--brand-teal);
}

.callout-info .callout-tag {
    color: var(--brand-teal);
    font-weight: 700;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
}

.callout-body {
    margin-top: 4px;
    color: var(--text-main);
}

/* SEQUENCE PILL */
.sequence-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--bg-primary);
    border: 1px solid var(--border-subtle);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12.5px;
    font-weight: 600;
    margin: 6px 0;
}

.flow-arrow {
    color: var(--brand-cobalt);
    font-weight: 800;
}

.sub-label {
    font-size: 13px;
    font-weight: 700;
    color: var(--text-muted);
    margin: 14px 0 6px 0;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

.standard-p {
    font-size: 13.5px;
    line-height: 1.6;
    margin: 6px 0;
    color: var(--text-main);
}

/* FLASHCARDS VIEW */
.flashcard-arena {
    display: none;
    max-width: 680px;
    margin: 0 auto;
    padding: 20px 0;
}

.flashcard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.card-perspective {
    perspective: 1200px;
    min-height: 320px;
    cursor: pointer;
    margin-bottom: 24px;
}

.fcard-inner {
    position: relative;
    width: 100%;
    min-height: 320px;
    transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    transform-style: preserve-3d;
}

.fcard-inner.flipped {
    transform: rotateY(180deg);
}

.fcard-front, .fcard-back {
    position: absolute;
    width: 100%;
    min-height: 320px;
    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;
    border-radius: 14px;
    padding: 32px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    border: 1px solid var(--border-subtle);
    box-shadow: var(--shadow-lg);
    background: var(--bg-card);
}

.fcard-back {
    transform: rotateY(180deg);
    background: linear-gradient(145deg, var(--bg-card) 0%, rgba(37,99,235,0.05) 100%);
    border-color: var(--brand-cobalt);
}

.fcard-category {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--brand-cobalt);
}

.fcard-question {
    font-family: var(--font-head);
    font-size: 19px;
    font-weight: 700;
    line-height: 1.45;
    margin: 20px 0;
    color: var(--text-main);
}

.fcard-answer {
    font-size: 15px;
    line-height: 1.6;
    margin: 20px 0;
    color: var(--text-main);
}

.fcard-hint {
    font-size: 11.5px;
    color: var(--text-light);
    text-align: center;
}

.flashcard-controls {
    display: flex;
    justify-content: center;
    gap: 12px;
}

.btn-fc {
    background: var(--bg-surface);
    border: 1px solid var(--border-strong);
    color: var(--text-main);
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 7px;
    cursor: pointer;
    transition: all 0.15s ease;
}

.btn-fc:hover {
    border-color: var(--brand-cobalt);
    color: var(--brand-cobalt);
    box-shadow: var(--shadow-sm);
}

/* QUIZ VIEW */
.quiz-arena {
    display: none;
    max-width: 720px;
    margin: 0 auto;
    padding: 20px 0;
}

.quiz-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 32px;
    box-shadow: var(--shadow-md);
}

.quiz-progress-bar {
    height: 6px;
    background: var(--border-subtle);
    border-radius: 3px;
    margin-bottom: 20px;
    overflow: hidden;
}

.quiz-progress-fill {
    height: 100%;
    width: 0%;
    background: var(--brand-cobalt);
    transition: width 0.3s ease;
}

.quiz-q-num {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    color: var(--brand-cobalt);
    text-transform: uppercase;
    margin-bottom: 8px;
}

.quiz-q-text {
    font-family: var(--font-head);
    font-size: 17px;
    font-weight: 700;
    line-height: 1.45;
    margin-bottom: 24px;
}

.quiz-options-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 20px;
}

.quiz-opt-btn {
    background: var(--bg-primary);
    border: 1px solid var(--border-subtle);
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 13.5px;
    text-align: left;
    color: var(--text-main);
    cursor: pointer;
    transition: all 0.15s ease;
    display: flex;
    align-items: center;
    gap: 12px;
}

.quiz-opt-btn:hover:not(:disabled) {
    border-color: var(--brand-cobalt);
    background: rgba(37,99,235,0.04);
}

.quiz-opt-btn.correct {
    background: rgba(16, 185, 129, 0.12);
    border-color: #10b981;
    color: #065f46;
    font-weight: 600;
}

[data-theme="dark"] .quiz-opt-btn.correct {
    color: #34d399;
}

.quiz-opt-btn.wrong {
    background: rgba(225, 29, 72, 0.12);
    border-color: #e11d48;
    color: #9f1239;
}

[data-theme="dark"] .quiz-opt-btn.wrong {
    color: #fb7185;
}

.quiz-feedback-box {
    display: none;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 13px;
    margin-bottom: 16px;
    background: var(--bg-primary);
    border-left: 4px solid var(--brand-cobalt);
    line-height: 1.5;
}

/* HIGH-YIELD SUMMARY / DRILL TAB */
.surgical-drill-arena {
    display: none;
}

.surgical-hero {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
    color: #ffffff;
    padding: 24px 28px;
    border-radius: 12px;
    margin-bottom: 24px;
}

.grid-surgical {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
    gap: 18px;
}

.surg-box {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 18px;
    box-shadow: var(--shadow-sm);
}

.surg-box-title {
    font-family: var(--font-head);
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border-subtle);
    color: var(--brand-cobalt);
}

.surg-items-list {
    list-style: none;
}

.surg-item {
    font-size: 13px;
    padding: 4px 0;
    color: var(--text-main);
    line-height: 1.5;
}

/* PRINT MEDIA */
@media print {
    .app-nav, .progress-subnav, .app-sidebar, .part-actions, .nav-mode-tabs {
        display: none !important;
    }
    .app-container {
        display: block !important;
    }
    .main-view-area {
        max-width: 100% !important;
        padding: 0 !important;
    }
    .part-card {
        box-shadow: none !important;
        border: 1px solid #ccc !important;
        page-break-inside: avoid;
        margin-bottom: 16px !important;
    }
}

/* RESPONSIVENESS */
@media (max-width: 900px) {
    .app-sidebar {
        display: none;
    }
    .main-view-area {
        padding: 16px;
    }
    .search-input-box {
        width: 180px;
    }
}
"""

def clean_tag(text):
    return re.sub(r'[^\w\-]', '_', text.lower())

def is_section_header(line):
    l = line.strip()
    if not l: return False
    # PART X
    if re.match(r'^PART\s+([A-Z0-9IVXLCDM]+)[\s—\-:]+(.*)', l, re.I):
        return True
    # Roman numeral: I. BACTERIA
    if re.match(r'^[IVXLCDM]+\.\s+[A-Z\s/&,–—\(\)]+$', l):
        return True
    # Number with emoji: 1. 🧫 BACTERIAL PATHOGENS
    if re.match(r'^\d+\.\s+[\U00010000-\U0010ffff\u2600-\u27ff\u2B50]\s*[A-Z\s/&,–—\(\)]+$', l):
        return True
    # Number with ALL CAPS title: 1. EARLY PREGNANCY
    m = re.match(r'^\d+\.\s+([A-Z0-9\s/&,–—\(\)\-\.:;\'"“”]+)$', l)
    if m:
        t = m.group(1).strip()
        words = [w for w in re.findall(r'[a-zA-Z]+', t)]
        if words and all(w.isupper() or w in ['A', 'IN', 'OF', 'THE', 'AND', 'FOR', 'TO', 'OR', 'WITH', 'VS', 'ON', 'AT'] for w in words):
            return True
    # Emoji section: 🧠 FINAL ONE-LINE MEMORY MAP
    if re.match(r'^[\U00010000-\U0010ffff\u2600-\u27ff\u2B50]\s+[A-Z\s/&,–—\(\)]+$', l):
        return True
    return False

def parse_markdown_to_sections(raw_lines, doc_title, doc_subtitle):
    sections = []
    current_sec = {"title": "Overview & Core Guidance", "lines": []}
    
    for l in raw_lines:
        line = l.strip()
        if not line:
            if current_sec["lines"]:
                current_sec["lines"].append(l)
            continue
            
        if line == doc_title or line == doc_subtitle:
            continue
            
        if is_section_header(line):
            if current_sec["lines"]:
                sections.append(current_sec)
            current_sec = {"title": line, "lines": []}
        else:
            current_sec["lines"].append(l)
            
    if current_sec["lines"]:
        sections.append(current_sec)
        
    # If the first section is empty or just whitespace, drop it
    if sections and not any(l.strip() for l in sections[0]["lines"]):
        sections.pop(0)
        
    return sections

def format_cell_content(cell_text):
    c = html.escape(cell_text.strip())
    # bold **text**
    c = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', c)
    # Highlight numbers with units, gestational ages or cut-offs
    c = re.sub(r'([≥≤~±]?\s*\d+(?:\.\d+)?(?:\+\d+)?\s*(?:weeks?|cm|mm|mg|g|µmol/L|mmol/L|mIU/mL|bpm|mmHg|days?|hours?|%|IU|mL|kg))', r'<span class="val-pill">\1</span>', c, flags=re.I)
    return c

def parse_table_block(table_lines):
    if not table_lines:
        return ""
    
    rows = []
    # Check if pipe table
    if all('|' in l for l in table_lines if l.strip()):
        for l in table_lines:
            line = l.strip()
            if not line: continue
            if re.match(r'^\|?[\s\-:|]+\|?$', line): # markdown separator
                continue
            cols = [col.strip() for col in line.split('|')]
            if cols and cols[0] == '': cols.pop(0)
            if cols and cols[-1] == '': cols.pop()
            if cols:
                rows.append(cols)
    else: # Tab-delimited table
        for l in table_lines:
            line = l.rstrip()
            if not line: continue
            cols = [c.strip() for c in line.split('\t')]
            if len(cols) >= 2:
                rows.append(cols)
                
    if not rows:
        return ""
        
    html_out = ['<div class="table-wrap"><table class="styled-table">']
    headers = rows[0]
    html_out.append('<thead><tr>')
    for h in headers:
        html_out.append(f'<th>{html.escape(h)}</th>')
    html_out.append('</tr></thead><tbody>')
    
    for r in rows[1:]:
        html_out.append('<tr>')
        for idx, col in enumerate(r):
            val_fmt = format_cell_content(col)
            if idx == 0:
                html_out.append(f'<td><strong>{val_fmt}</strong></td>')
            else:
                html_out.append(f'<td>{val_fmt}</td>')
        html_out.append('</tr>')
        
    html_out.append('</tbody></table></div>')
    return "\n".join(html_out)

def format_section_body(raw_lines, sec_idx, doc_slug, global_topics, section_topics):
    html_out = []
    idx = 0
    in_ul = False
    in_sub_ul = False
    
    while idx < len(raw_lines):
        line = raw_lines[idx].strip()
        if not line:
            idx += 1
            continue
            
        # Table block detection (consecutive lines with tabs or pipes)
        if ('\t' in raw_lines[idx] and len(raw_lines[idx].split('\t')) >= 2) or (line.startswith('|') and '|' in line[1:]):
            if in_sub_ul: html_out.append("</ul>"); in_sub_ul = False
            if in_ul: html_out.append("</ul>"); in_ul = False
            
            table_lines = []
            while idx < len(raw_lines) and (
                ('\t' in raw_lines[idx] and len(raw_lines[idx].split('\t')) >= 2) or 
                (raw_lines[idx].strip().startswith('|') and '|' in raw_lines[idx].strip()[1:]) or
                (table_lines and not raw_lines[idx].strip()) # allow single whitespace line inside table block
            ):
                if not raw_lines[idx].strip() and idx + 1 < len(raw_lines) and not ('\t' in raw_lines[idx+1] or raw_lines[idx+1].strip().startswith('|')):
                    break
                if raw_lines[idx].strip():
                    table_lines.append(raw_lines[idx])
                idx += 1
                
            table_html = parse_table_block(table_lines)
            if table_html:
                html_out.append(table_html)
            continue
            
        # Checkpoint Topic Row: e.g. "1. Organism", "A. Sexually transmitted...", "1. Intradecidual sign"
        topic_match = re.match(r'^(?:(\d+)\.|([A-Z])\.)\s+(.+)$', line)
        if topic_match and not line.endswith(':'):
            num_or_let = topic_match.group(1) or topic_match.group(2)
            title_text = topic_match.group(3).strip()
            if len(title_text) < 120:
                if in_sub_ul: html_out.append("</ul>"); in_sub_ul = False
                if in_ul: html_out.append("</ul>"); in_ul = False
                
                topic_id = f"t-{sec_idx+1}-{len(section_topics)+1}"
                topic_obj = {
                    "id": topic_id,
                    "title": title_text,
                    "badge": num_or_let
                }
                section_topics.append(topic_obj)
                global_topics.append(topic_obj)
                
                html_out.append(f'''
                <div class="topic-row" id="topic-{topic_id}">
                    <div class="topic-title-box">
                        <span class="topic-badge">{html.escape(num_or_let)}</span>
                        <h3 class="topic-heading">{html.escape(title_text)}</h3>
                    </div>
                    <label class="mastery-check-label" title="Mark as Mastered">
                        <input type="checkbox" class="topic-checkbox" data-id="{topic_id}" onchange="toggleMastery('{topic_id}')">
                        <span class="check-custom"></span>
                        <span class="check-text">Mastered</span>
                    </label>
                </div>
                ''')
                idx += 1
                continue
                
        # Sub-list items: '○'
        if line.startswith('○'):
            if not in_sub_ul:
                html_out.append('<ul class="sub-list">')
                in_sub_ul = True
            content = format_cell_content(line[1:].strip())
            html_out.append(f'<li class="sub-bullet"><span class="sub-bullet-icon">○</span> <span class="bullet-text">{content}</span></li>')
            idx += 1
            continue
        else:
            if in_sub_ul:
                html_out.append("</ul>")
                in_sub_ul = False
                
        # Core bullet items: '●', '•', '-', '*'
        if line.startswith(('●', '•', '- ', '* ')):
            if not in_ul:
                html_out.append('<ul class="core-list">')
                in_ul = True
            content = format_cell_content(line[1:].strip() if line.startswith(('●', '•')) else line[2:].strip())
            html_out.append(f'<li class="core-bullet"><span class="bullet-icon">●</span> <span class="bullet-text">{content}</span></li>')
            idx += 1
            continue
        else:
            if in_ul:
                html_out.append("</ul>")
                in_ul = False
                
        # Sequence pills (arrows)
        if ('→' in line or '➔' in line or '↓' in line or '=>' in line) and len(line) < 200:
            content = format_cell_content(line)
            html_out.append(f'<div class="sequence-pill"><span class="flow-arrow">➔</span> <span>{content}</span></div>')
            idx += 1
            continue
            
        # Clinical Callout Detection
        callout_highyield_keywords = [
            "important", "remember", "key", "nice", "rcog", "definitive", "gold standard",
            "triad", "diagnostic criteria", "exam priority", "clinical importance",
            "surgical importance", "warning", "cut-off", "ultra-high-yield", "classic"
        ]
        callout_info_keywords = [
            "appearance", "finding", "modality", "definition", "maternal", "fetal",
            "management", "consequence", "stages", "criteria", "mechanism"
        ]
        
        lower_line = line.lower()
        has_hy_emoji = any(em in line for em in ['⭐', '🔥', '⚡', '⚠️'])
        is_hy = has_hy_emoji or any(lower_line.startswith(k + ':') or lower_line.startswith(k + ' —') or lower_line.startswith(k + ' ') or lower_line == k for k in callout_highyield_keywords)
        is_info = any(lower_line.startswith(k + ':') or lower_line.startswith(k + ' —') or lower_line == k for k in callout_info_keywords)
        
        if (is_hy or is_info) and (':' in line or '—' in line or len(line) < 80):
            cls_name = "callout-highyield" if is_hy else "callout-info"
            tag_part = line
            body_part = ""
            if ':' in line:
                parts = line.split(':', 1)
                tag_part = parts[0].strip()
                body_part = parts[1].strip()
            elif '—' in line:
                parts = line.split('—', 1)
                tag_part = parts[0].strip()
                body_part = parts[1].strip()
                
            if not body_part and idx + 1 < len(raw_lines):
                next_l = raw_lines[idx+1].strip()
                if next_l and not next_l.startswith(('●', '•', 'PART', '1.', '2.', '3.')):
                    body_part = next_l
                    idx += 1
                    
            body_fmt = format_cell_content(body_part) if body_part else ""
            html_out.append(f'''
            <div class="atlas-callout {cls_name}">
                <div class="callout-header"><span class="callout-tag">{html.escape(tag_part)}</span></div>
                {f'<div class="callout-body">{body_fmt}</div>' if body_fmt else ""}
            </div>
            ''')
            idx += 1
            continue
            
        # Short sub-labels
        if len(line) < 55 and not line.endswith(('.', ',', ';')) and not line.startswith('<'):
            html_out.append(f'<h4 class="sub-label">{html.escape(line)}</h4>')
            idx += 1
            continue
            
        # Standard paragraph
        content = format_cell_content(line)
        html_out.append(f'<p class="standard-p">{content}</p>')
        idx += 1
        
    if in_sub_ul: html_out.append("</ul>")
    if in_ul: html_out.append("</ul>")
    
    return "\n".join(html_out)

def generate_flashcards(sections, doc_title):
    cards = []
    
    # 1. Tables Q/A
    for sec in sections:
        sec_title = sec["title"]
        for l in sec["lines"]:
            if '\t' in l:
                cols = [c.strip() for c in l.split('\t') if c.strip()]
                if len(cols) >= 2 and not cols[0].lower().startswith(('condition', 'organism', 'test', 'stage', '#', 'situation')):
                    q_term = cols[0]
                    a_text = "<br>".join([f"<strong>{cols[j]}</strong>" if j == 1 else cols[j] for j in range(1, len(cols))])
                    cards.append({
                        "category": sec_title.split('—')[-1].strip()[:30],
                        "q": f"What are the diagnostic features, cut-offs or clinical guidelines for <strong>{html.escape(q_term)}</strong>?",
                        "a": a_text
                    })
            elif l.strip().startswith('|') and '|' in l.strip()[1:]:
                cols = [c.strip() for c in l.strip().split('|') if c.strip()]
                if len(cols) >= 2 and not any(cols[0].lower().startswith(x) for x in ['condition', 'organism', 'test', 'stage', '---', '#']):
                    q_term = re.sub(r'\*+', '', cols[0])
                    a_text = "<br>".join([f"<strong>{re.sub(r'[*]+', '', cols[j])}</strong>" if j == 1 else re.sub(r'[*]+', '', cols[j]) for j in range(1, len(cols))])
                    cards.append({
                        "category": sec_title.split('—')[-1].strip()[:30],
                        "q": f"What is the management/clinical association for <strong>{html.escape(q_term)}</strong>?",
                        "a": a_text
                    })
                    
    # 2. Sequences & Callouts
    for sec in sections:
        sec_title = sec["title"]
        for l in sec["lines"]:
            line = l.strip()
            if '→' in line or '➔' in line:
                cards.append({
                    "category": "Clinical Sequence",
                    "q": f"Describe the key sequence or progression in: <strong>{html.escape(sec_title)}</strong>",
                    "a": f"<strong>{html.escape(line)}</strong>"
                })
            elif any(line.lower().startswith(k) for k in ['triad:', 'classic triad:', 'gold standard:', 'diagnostic criteria:']):
                cards.append({
                    "category": "High-Yield Triad / Criteria",
                    "q": f"State the verified {html.escape(line.split(':')[0])} in: <strong>{html.escape(sec_title)}</strong>",
                    "a": html.escape(line.split(':', 1)[-1].strip())
                })
                
    unique_cards = []
    seen = set()
    for c in cards:
        if c['q'] not in seen and len(c['q']) < 250 and len(c['a']) > 3:
            seen.add(c['q'])
            unique_cards.append(c)
        if len(unique_cards) >= 25:
            break
            
    if not unique_cards:
        unique_cards.append({
            "category": "Core Knowledge",
            "q": f"What is the primary scope of {html.escape(doc_title)}?",
            "a": "Comprehensive review of clinical guidelines, investigations, and high-yield criteria."
        })
        
    return unique_cards

def generate_quiz_questions(flashcards, sections):
    quiz = []
    candidates = []
    for fc in flashcards:
        clean_a = re.sub(r'<[^>]+>', ' ', fc['a']).strip()
        clean_q = re.sub(r'<[^>]+>', ' ', fc['q']).strip()
        if len(clean_a) < 140 and len(clean_a) > 4:
            candidates.append((clean_q, clean_a, fc['category']))
            
    for i, (q, correct_a, cat) in enumerate(candidates):
        distractors = [c[1] for j, c in enumerate(candidates) if j != i and c[1] != correct_a and len(c[1]) < 140]
        if len(distractors) < 3:
            distractors.extend([
                "Follow expectant management with serial surveillance",
                "Immediate laparoscopy and surgical staging",
                "Repeat clinical assessment in 6–8 weeks"
            ])
        options = [correct_a] + distractors[:3]
        corr_idx = i % 4
        options[0], options[corr_idx] = options[corr_idx], options[0]
        
        quiz.append({
            "q": q,
            "options": options,
            "correct": corr_idx,
            "explanation": f"Key Guideline / Fact: {correct_a} ({cat})."
        })
        if len(quiz) >= 12:
            break
            
    return quiz

def generate_summary_matrix_cards(sections, flashcards):
    cards = []
    for sec in sections[:12]:
        title = sec["title"]
        items = []
        for l in sec["lines"]:
            s = l.strip()
            if s.startswith(('●', '•', '- ', '* ')):
                items.append(s[1:].strip() if s.startswith(('●', '•')) else s[2:].strip())
            elif '\t' in s:
                cols = [c.strip() for c in s.split('\t')]
                if len(cols) >= 2 and not cols[0].lower().startswith(('condition', 'organism', 'stage', '#')):
                    items.append(f"{cols[0]}: {cols[1]}")
            if len(items) >= 6:
                break
        if items:
            cards.append({
                "title": title[:40],
                "items": items
            })
            
    if not cards and flashcards:
        for fc in flashcards[:6]:
            cards.append({
                "title": fc["category"],
                "items": [re.sub(r'<[^>]+>', '', fc["q"]), re.sub(r'<[^>]+>', '', fc["a"])]
            })
    return cards

def determine_tab4_label(doc_title):
    t = doc_title.lower()
    if 'bug' in t or 'microbiol' in t or 'pathogen' in t:
        return "⚡ Bug Catalog Matrix"
    if 'delivery' in t or 'timing' in t:
        return "⚡ Gestational Timing Matrix"
    if 'investigation' in t or 'cut-off' in t:
        return "⚡ Diagnostic Cut-offs Matrix"
    if 'radiolog' in t or 'ultrasound' in t or 'sign' in t:
        return "⚡ Imaging & Signs Matrix"
    return "⚡ High-Yield Drill"

def convert_md_to_interactive_atlas(input_md_path, output_html_path=None):
    if not os.path.exists(input_md_path):
        raise FileNotFoundError(f"Input file not found: {input_md_path}")
        
    if output_html_path is None:
        base_name = os.path.splitext(input_md_path)[0]
        output_html_path = base_name + ".html"
        
    doc_filename = os.path.basename(input_md_path)
    doc_slug = clean_tag(os.path.splitext(doc_filename)[0])
    
    with open(input_md_path, 'r', encoding='utf-8') as f:
        text = f.read()
        
    raw_lines = text.splitlines()
    non_empty = [l.strip() for l in raw_lines if l.strip()]
    
    doc_title = non_empty[0] if non_empty else doc_filename
    doc_subtitle = "MRCOG / FCPS / RCOG Guidance — Interactive Study Atlas"
    if len(non_empty) > 1 and not is_section_header(non_empty[1]) and len(non_empty[1]) > 5 and non_empty[1].lower() != "key":
        doc_subtitle = non_empty[1]
    elif "rcog master table" in doc_filename.lower():
        doc_subtitle = "RCOG Guidance — Ideal Timing of Delivery & Mode Recommendations"
        
    sections = parse_markdown_to_sections(raw_lines, doc_title, doc_subtitle)
    
    global_topics = []
    section_cards_html = []
    sidebar_links_html = []
    
    for sec_idx, sec in enumerate(sections):
        sec_title = sec["title"]
        part_id = f"part-{sec_idx+1}"
        sec_topic_id = f"sec-{sec_idx+1}"
        
        section_topics = []
        body_content = format_section_body(sec["lines"], sec_idx, doc_slug, global_topics, section_topics)
        
        # If this section has NO sub-topics inside it, register the section itself as a topic!
        header_check_html = ""
        if len(section_topics) == 0:
            global_topics.append({
                "id": sec_topic_id,
                "title": sec_title,
                "badge": str(sec_idx + 1)
            })
            header_check_html = f'''
            <label class="mastery-check-label" title="Mark Section as Mastered">
                <input type="checkbox" class="topic-checkbox" data-id="{sec_topic_id}" onchange="toggleMastery('{sec_topic_id}')">
                <span class="check-custom"></span>
                <span class="check-text">Mastered</span>
            </label>
            '''
        
        sidebar_links_html.append(f'<li><a href="#{part_id}" class="part-nav-link" title="{html.escape(sec_title)}">{html.escape(sec_title)}</a></li>')
        
        section_cards_html.append(f'''
        <article class="part-card" id="{part_id}" data-part-index="{sec_idx+1}">
            <div class="part-top-bar">
                <div class="part-title-wrapper">
                    <span class="part-pill">SECTION {sec_idx+1}</span>
                    <h2 class="part-title">{html.escape(sec_title)}</h2>
                </div>
                <div class="part-actions">
                    {header_check_html}
                    <button class="btn-icon" onclick="readAloudSection('{part_id}')" title="Read this section aloud">🔊 Listen</button>
                    <button class="btn-icon" onclick="copySectionText('{part_id}')" title="Copy section text">📋 Copy</button>
                </div>
            </div>
            <div class="part-body">
                {body_content}
            </div>
        </article>
        ''')
        
    total_topics = len(global_topics)
    
    flashcards = generate_flashcards(sections, doc_title)
    quiz_questions = generate_quiz_questions(flashcards, sections)
    matrix_cards = generate_summary_matrix_cards(sections, flashcards)
    tab4_label = determine_tab4_label(doc_title)
    
    drill_boxes_html = []
    for box in matrix_cards:
        items_li = "\n".join([f'<li class="surg-item">● {html.escape(it)}</li>' for it in box["items"]])
        drill_boxes_html.append(f'''
        <div class="surg-box">
            <div class="surg-box-title">📌 {html.escape(box["title"])}</div>
            <ul class="surg-items-list">
                {items_li}
            </ul>
        </div>
        ''')
        
    js_code = f"""
    const totalTopics = {total_topics};
    const flashcards = {json.dumps(flashcards)};
    const quizQuestions = {json.dumps(quiz_questions)};
    const storageKey = 'obgyn_mastered_{doc_slug}';

    let currentFcIndex = 0;
    let currentQuizIndex = 0;
    let quizScore = 0;
    let filterOnlyUnmastered = false;

    let masteredSet = new Set(JSON.parse(localStorage.getItem(storageKey) || '[]'));

    function initApp() {{
        updateMasteryProgress();
        document.querySelectorAll('.topic-checkbox').forEach(cb => {{
            const id = cb.getAttribute('data-id');
            if (masteredSet.has(id)) {{
                cb.checked = true;
                const row = document.getElementById('topic-' + id);
                if (row) row.classList.add('mastered-badge-active');
                if (id.startsWith('sec-')) {{
                    const card = document.getElementById('part-' + id.replace('sec-', ''));
                    if (card) card.classList.add('section-mastered');
                }}
            }}
        }});
        if (flashcards.length > 0) loadFlashcard(0);
        if (quizQuestions.length > 0) loadQuizQuestion(0);
    }}

    function toggleMastery(id) {{
        const row = document.getElementById('topic-' + id);
        const cb = document.querySelector(`.topic-checkbox[data-id="${{id}}"]`);
        if (cb && cb.checked) {{
            masteredSet.add(id);
            if (row) row.classList.add('mastered-badge-active');
            if (id.startsWith('sec-')) {{
                const card = document.getElementById('part-' + id.replace('sec-', ''));
                if (card) card.classList.add('section-mastered');
            }}
        }} else {{
            masteredSet.delete(id);
            if (row) row.classList.remove('mastered-badge-active');
            if (id.startsWith('sec-')) {{
                const card = document.getElementById('part-' + id.replace('sec-', ''));
                if (card) card.classList.remove('section-mastered');
            }}
        }}
        localStorage.setItem(storageKey, JSON.stringify(Array.from(masteredSet)));
        updateMasteryProgress();
    }}

    function updateMasteryProgress() {{
        const count = masteredSet.size;
        const pct = totalTopics > 0 ? Math.round((count / totalTopics) * 100) : 0;
        const textEl = document.getElementById('progress-text');
        const fillEl = document.getElementById('progress-bar');
        if (textEl) textEl.innerText = `${{count}} / ${{totalTopics}} Mastered (${{pct}}%)`;
        if (fillEl) fillEl.style.width = pct + '%';
    }}

    function filterMasteredOnly(btn) {{
        filterOnlyUnmastered = !filterOnlyUnmastered;
        btn.innerText = filterOnlyUnmastered ? "Showing: Unchecked" : "Unchecked Only";
        
        // Filter topic rows
        document.querySelectorAll('.topic-row').forEach(row => {{
            const cb = row.querySelector('.topic-checkbox');
            if (!cb) return;
            const id = cb.getAttribute('data-id');
            if (filterOnlyUnmastered && masteredSet.has(id)) {{
                row.style.display = 'none';
            }} else {{
                row.style.display = 'flex';
            }}
        }});

        // Filter section cards where section itself is the topic
        document.querySelectorAll('.part-card').forEach(card => {{
            const cb = card.querySelector('.part-top-bar .topic-checkbox');
            if (!cb) return;
            const id = cb.getAttribute('data-id');
            if (filterOnlyUnmastered && masteredSet.has(id)) {{
                card.style.display = 'none';
            }} else {{
                card.style.display = 'block';
            }}
        }});
    }}

    function switchMode(mode) {{
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        const activeTab = document.getElementById('tab-' + mode);
        if (activeTab) activeTab.classList.add('active');

        document.getElementById('view-reader').style.display = (mode === 'reader') ? 'block' : 'none';
        document.getElementById('view-flashcards').style.display = (mode === 'flashcards') ? 'block' : 'none';
        document.getElementById('view-quiz').style.display = (mode === 'quiz') ? 'block' : 'none';
        document.getElementById('view-surgical').style.display = (mode === 'surgical') ? 'block' : 'none';

        const sidebar = document.getElementById('sidebar-nav');
        if (sidebar) {{
            sidebar.style.display = (mode === 'reader') ? 'block' : 'none';
        }}
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function toggleTheme() {{
        const html = document.documentElement;
        const current = html.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        localStorage.setItem('obgyn_theme', next);
    }}

    function loadFlashcard(index) {{
        if (!flashcards.length) return;
        currentFcIndex = index;
        const card = flashcards[currentFcIndex];
        const inner = document.getElementById('flashcard-inner');
        if (inner) inner.classList.remove('flipped');
        document.getElementById('fc-category').innerText = card.category;
        document.getElementById('fc-question').innerHTML = card.q;
        document.getElementById('fc-answer').innerHTML = card.a;
        document.getElementById('fc-counter').innerText = `Card ${{currentFcIndex + 1}} of ${{flashcards.length}}`;
    }}

    function flipCurrentCard() {{
        const inner = document.getElementById('flashcard-inner');
        if (inner) inner.classList.toggle('flipped');
    }}

    function nextCard() {{
        if (!flashcards.length) return;
        currentFcIndex = (currentFcIndex + 1) % flashcards.length;
        loadFlashcard(currentFcIndex);
    }}

    function prevCard() {{
        if (!flashcards.length) return;
        currentFcIndex = (currentFcIndex - 1 + flashcards.length) % flashcards.length;
        loadFlashcard(currentFcIndex);
    }}

    function shuffleCards() {{
        for (let i = flashcards.length - 1; i > 0; i--) {{
            const j = Math.floor(Math.random() * (i + 1));
            [flashcards[i], flashcards[j]] = [flashcards[j], flashcards[i]];
        }}
        loadFlashcard(0);
    }}

    function loadQuizQuestion(index) {{
        if (!quizQuestions.length) return;
        currentQuizIndex = index;
        const qData = quizQuestions[index];
        document.getElementById('quiz-num').innerText = `QUESTION ${{index + 1}} OF ${{quizQuestions.length}}`;
        document.getElementById('quiz-prog-fill').style.width = `${{((index) / quizQuestions.length) * 100}}%`;
        document.getElementById('quiz-text').innerHTML = qData.q;
        
        const optContainer = document.getElementById('quiz-options');
        optContainer.innerHTML = '';

        const feedback = document.getElementById('quiz-feedback');
        feedback.style.display = 'none';
        feedback.innerHTML = '';
        document.getElementById('btn-quiz-next').style.display = 'none';

        qData.options.forEach((optText, optIdx) => {{
            const btn = document.createElement('button');
            btn.className = 'quiz-opt-btn';
            btn.innerHTML = `<span style="font-weight:700; width:22px;">${{String.fromCharCode(65 + optIdx)}}.</span> <span>${{optText}}</span>`;
            btn.onclick = () => checkQuizAnswer(optIdx, qData);
            optContainer.appendChild(btn);
        }});
    }}

    function checkQuizAnswer(selectedIdx, qData) {{
        const buttons = document.querySelectorAll('.quiz-opt-btn');
        buttons.forEach((btn, idx) => {{
            btn.disabled = true;
            if (idx === qData.correct) {{
                btn.classList.add('correct');
            }} else if (idx === selectedIdx) {{
                btn.classList.add('wrong');
            }}
        }});

        if (selectedIdx === qData.correct) {{
            quizScore++;
        }}

        const feedback = document.getElementById('quiz-feedback');
        feedback.style.display = 'block';
        feedback.innerHTML = `<strong>${{selectedIdx === qData.correct ? "✓ Correct!" : "✗ Incorrect."}}</strong> ${{qData.explanation}}`;

        const nextBtn = document.getElementById('btn-quiz-next');
        nextBtn.style.display = 'block';
        if (currentQuizIndex === quizQuestions.length - 1) {{
            nextBtn.innerText = "View Final Score";
        }} else {{
            nextBtn.innerText = "Next Question →";
        }}
    }}

    function nextQuizQuestion() {{
        if (currentQuizIndex < quizQuestions.length - 1) {{
            loadQuizQuestion(currentQuizIndex + 1);
        }} else {{
            const pct = Math.round((quizScore / quizQuestions.length) * 100);
            document.getElementById('quiz-text').innerText = `Quiz Complete! You scored ${{quizScore}} / ${{quizQuestions.length}} (${{pct}}%)`;
            document.getElementById('quiz-options').innerHTML = `<p style="font-size:15px; color:var(--text-muted); margin-bottom:16px;">Review key clinical points to ensure maximum exam recall.</p><button class="btn-fc" onclick="restartQuiz()">↺ Retake Quiz</button>`;
            document.getElementById('quiz-feedback').style.display = 'none';
            document.getElementById('btn-quiz-next').style.display = 'none';
        }}
    }}

    function restartQuiz() {{
        quizScore = 0;
        loadQuizQuestion(0);
    }}

    function handleSearch(query) {{
        const q = query.toLowerCase().trim();
        const cards = document.querySelectorAll('.part-card');
        cards.forEach(card => {{
            if (!q) {{
                card.style.display = 'block';
                return;
            }}
            const text = card.innerText.toLowerCase();
            card.style.display = text.includes(q) ? 'block' : 'none';
        }});
    }}

    function readAloudSection(sectionId) {{
        if (!('speechSynthesis' in window)) {{
            alert('Speech synthesis is not supported by your browser.');
            return;
        }}
        window.speechSynthesis.cancel();
        const section = document.getElementById(sectionId);
        const textToRead = section.innerText;
        const utterance = new SpeechSynthesisUtterance(textToRead);
        utterance.rate = 1.0;
        window.speechSynthesis.speak(utterance);
    }}

    function copySectionText(sectionId) {{
        const section = document.getElementById(sectionId);
        navigator.clipboard.writeText(section.innerText).then(() => {{
            alert('Section text copied to clipboard!');
        }});
    }}

    function copyAllAtlasText() {{
        const reader = document.getElementById('view-reader');
        navigator.clipboard.writeText(reader.innerText).then(() => {{
            alert('Entire Atlas text copied to clipboard!');
        }});
    }}

    document.addEventListener('keydown', (e) => {{
        if (document.getElementById('view-flashcards').style.display === 'block') {{
            if (e.code === 'Space') {{
                e.preventDefault();
                flipCurrentCard();
            }} else if (e.code === 'ArrowRight') {{
                nextCard();
            }} else if (e.code === 'ArrowLeft') {{
                prevCard();
            }}
        }}
    }});

    window.addEventListener('DOMContentLoaded', () => {{
        const savedTheme = localStorage.getItem('obgyn_theme');
        if (savedTheme) {{
            document.documentElement.setAttribute('data-theme', savedTheme);
        }}
        initApp();
    }});
    """

    html_output = f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(doc_title)} — Interactive Atlas</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <!-- APP NAVBAR -->
    <nav class="app-nav">
        <div class="brand-block">
            <div class="brand-logo">⚕</div>
            <div>
                <div class="brand-title-text">{html.escape(doc_title[:38])}</div>
                <div class="brand-subtitle-text">{html.escape(doc_subtitle[:50])}</div>
            </div>
        </div>

        <div class="nav-mode-tabs">
            <button class="tab-btn active" id="tab-reader" onclick="switchMode('reader')">📖 Atlas Reader</button>
            <button class="tab-btn" id="tab-flashcards" onclick="switchMode('flashcards')">🗂️ Flashcards ({len(flashcards)})</button>
            <button class="tab-btn" id="tab-quiz" onclick="switchMode('quiz')">✍️ Board Quiz</button>
            <button class="tab-btn" id="tab-surgical" onclick="switchMode('surgical')">{tab4_label}</button>
        </div>

        <div class="nav-actions">
            <button class="btn-header" onclick="toggleTheme()" title="Switch Light/Dark mode">🌓 Theme</button>
            <button class="btn-header" onclick="copyAllAtlasText()" title="Copy all text">📋 Copy All</button>
            <button class="btn-header" onclick="window.print()" title="Print complete Atlas">🖨️ Print</button>
        </div>
    </nav>

    <!-- PROGRESS & SEARCH SUBNAV -->
    <div class="progress-subnav">
        <div class="progress-track-wrapper">
            <span class="progress-count-text" id="progress-text">0 / {total_topics} Mastered (0%)</span>
            <div class="progress-bar-bg">
                <div class="progress-fill" id="progress-bar"></div>
            </div>
        </div>

        <div class="filter-controls">
            <div class="search-input-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="atlas-search" placeholder="Search {len(sections)} sections & keywords..." oninput="handleSearch(this.value)">
            </div>
            <button class="btn-header" style="background:var(--bg-primary); color:var(--text-main); border:1px solid var(--border-strong);" onclick="filterMasteredOnly(this)" id="btn-filter-mastered">Unchecked Only</button>
        </div>
    </div>

    <!-- MAIN APP CONTAINER -->
    <div class="app-container">
        <!-- SIDEBAR -->
        <aside class="app-sidebar" id="sidebar-nav">
            <div class="sidebar-heading">Navigation Syllabus ({len(sections)} Sections)</div>
            <ul class="part-nav-list">
                {"".join(sidebar_links_html)}
            </ul>
        </aside>

        <!-- MAIN VIEW AREA -->
        <main class="main-view-area">

            <!-- MODE 1: ATLAS READER -->
            <section id="view-reader">
                <div class="reader-hero">
                    <h1 class="reader-hero-title">{html.escape(doc_title)}</h1>
                    <div class="reader-hero-sub">⭐ {html.escape(doc_subtitle)}</div>
                    <div class="reader-hero-meta">
                        <span>✓ Full Master Syllabus</span>
                        <span>✓ High-Yield Exam Colored Callouts</span>
                        <span>✓ Active Recall Mastery Checkpoints</span>
                        <span>✓ Built-in Audio Speech Synthesis</span>
                    </div>
                </div>

                {"".join(section_cards_html)}
            </section>

            <!-- MODE 2: ACTIVE RECALL FLASHCARDS -->
            <section id="view-flashcards" class="flashcard-arena">
                <div class="flashcard-header">
                    <div>
                        <h2 style="font-family:var(--font-head); font-size:18px;">Active Recall Flashcards</h2>
                        <p style="font-size:12px; color:var(--text-light);">Click the card or press Space to flip. Test your spontaneous recall.</p>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:var(--brand-cobalt);" id="fc-counter">Card 1 of {len(flashcards)}</div>
                </div>

                <div class="card-perspective" onclick="flipCurrentCard()">
                    <div class="fcard-inner" id="flashcard-inner">
                        <div class="fcard-front">
                            <span class="fcard-category" id="fc-category">Clinical Category</span>
                            <div class="fcard-question" id="fc-question">Loading question...</div>
                            <span class="fcard-hint">Tap / Click card to reveal answer ↺</span>
                        </div>
                        <div class="fcard-back">
                            <span class="fcard-category">Verified Answer</span>
                            <div class="fcard-answer" id="fc-answer">Loading answer...</div>
                            <span class="fcard-hint">Click card again to flip back</span>
                        </div>
                    </div>
                </div>

                <div class="flashcard-controls">
                    <button class="btn-fc" onclick="prevCard()">← Previous</button>
                    <button class="btn-fc" style="background:#10b981; color:#fff; border-color:#10b981;" onclick="flipCurrentCard()">Flip Card</button>
                    <button class="btn-fc" onclick="shuffleCards()">🔀 Shuffle</button>
                    <button class="btn-fc" onclick="nextCard()">Next →</button>
                </div>
            </section>

            <!-- MODE 3: BOARD QUIZ -->
            <section id="view-quiz" class="quiz-arena">
                <div class="quiz-card">
                    <div class="quiz-progress-bar">
                        <div class="quiz-progress-fill" id="quiz-prog-fill"></div>
                    </div>
                    <div class="quiz-q-num" id="quiz-num">QUESTION 1 OF {len(quiz_questions)}</div>
                    <div class="quiz-q-text" id="quiz-text">Loading question...</div>
                    <div class="quiz-options-list" id="quiz-options"></div>
                    <div class="quiz-feedback-box" id="quiz-feedback"></div>
                    <div style="display:flex; justify-content:flex-end;">
                        <button class="btn-fc" id="btn-quiz-next" style="display:none; background:var(--brand-cobalt); color:#fff;" onclick="nextQuizQuestion()">Next Question →</button>
                    </div>
                </div>
            </section>

            <!-- MODE 4: HIGH-YIELD DRILL ARENA -->
            <section id="view-surgical" class="surgical-drill-arena">
                <div class="surgical-hero">
                    <span style="font-size:11px; font-weight:800; letter-spacing:1px; background:rgba(255,255,255,0.2); padding:3px 10px; border-radius:12px;">EXAM HIGH-YIELD DRILL</span>
                    <h2 style="font-family:var(--font-head); font-size:22px; margin-top:8px;">{tab4_label.replace('⚡', '').strip()}</h2>
                    <p style="font-size:13px; opacity:0.9; margin-top:4px;">Core associations, key diagnostic parameters, and rapid exam differentiation:</p>
                </div>

                <div class="grid-surgical">
                    {"".join(drill_boxes_html)}
                </div>
            </section>

        </main>
    </div>

    <script>
{js_code}
    </script>
</body>
</html>
"""

    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_output)
        
    print(f"Successfully generated atlas: {output_html_path} ({len(sections)} sections, {total_topics} topics, {len(flashcards)} flashcards)")
    return output_html_path

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown / Plaintext study notes into Interactive Atlas HTML apps.")
    parser.add_argument("inputs", nargs="*", help="One or more markdown files to convert. If omitted, converts all .md files in 'all docs'.")
    default_out_dir = os.path.join(os.path.dirname(__file__), "web_docs")
    parser.add_argument("--output-dir", "-o", default=default_out_dir, help="Directory to save output HTML files (defaults to web_docs).")
    parser.add_argument("--force", "-f", action="store_true", help="Force rebuild even if HTML already exists.")
    
    args = parser.parse_args()
    
    target_files = []
    if args.inputs:
        for inp in args.inputs:
            if os.path.isdir(inp):
                for f in sorted(os.listdir(inp)):
                    if f.endswith('.md'):
                        target_files.append(os.path.join(inp, f))
            elif os.path.isfile(inp):
                target_files.append(inp)
    else:
        default_dir = os.path.join(os.path.dirname(__file__), "all docs")
        if os.path.exists(default_dir):
            for f in sorted(os.listdir(default_dir)):
                if f.endswith('.md'):
                    target_files.append(os.path.join(default_dir, f))
                    
    if not target_files:
        print("No .md files found to convert.")
        sys.exit(1)
        
    print(f"Interactive Atlas Converter: Processing {len(target_files)} file(s)...")
    success_count = 0
    os.makedirs(args.output_dir, exist_ok=True)
    for fpath in target_files:
        out_name = os.path.splitext(os.path.basename(fpath))[0] + ".html"
        out_path = os.path.join(args.output_dir, out_name)
            
        try:
            convert_md_to_interactive_atlas(fpath, out_path)
            success_count += 1
        except Exception as e:
            print(f"Error converting {fpath}: {e}", file=sys.stderr)
            
    print(f"\nCompleted: {success_count}/{len(target_files)} atlases successfully built in '{args.output_dir}'.")

if __name__ == '__main__':
    main()
