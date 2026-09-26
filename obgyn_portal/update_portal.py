"""
update_portal.py
Updates index.html and portal.html to include all 46 atlas HTML files in web_docs.
"""

import os
import re
from urllib.parse import quote

WEB_DOCS = os.path.join(os.path.dirname(__file__), "web_docs")

# ─── card metadata catalog ──────────────────────────────────────────────
# Each tuple: (filename, icon, color_class, category, pill_label, title, desc, drill_label)
# color_class: color-blue | color-teal | color-rose | color-amber | color-purple | color-emerald

CARD_CATALOG = [
    # ──── ORIGINAL 9 ──────────────────────────────────────────────────────
    ("anatomy_interactive_atlas.html",
     "🏛️", "color-blue", "imaging gynaecology obstetrics",
     "Core Anatomy & Physio",
     "Master OBGYN Anatomy, Histology, Embryology & Physiology",
     "Comprehensive reference covering pelvic floor, vascular danger zones, urinary anatomy, embryological shunts, and maternal systemic physiology.",
     "⚡ Surgical Drill"),

    ("MASTER CLASSIFICATION OF GYNECOLOGICAL BUGS.html",
     "🦠", "color-rose", "microbiology gynaecology",
     "Gynaecology Bugs",
     "Master Classification of Gynecological Bugs",
     "Bacterial, viral, fungal, and parasitic pathogens in gynaecology with STI correlations, PID management, and NICE evidence-based criteria.",
     "⚡ Bug Matrix"),

    ("MASTER GYNAECOLOGY SIGNS, EponYMS, TRIADS, SYNDROMES & DIAGNOSTIC CRITERIA.html",
     "🩺", "color-purple", "gynaecology",
     "Signs & Eponyms",
     "Master Gynaecology Signs, Eponyms, Triads & Syndromes",
     "Physiological and pathological clinical signs, classic exam triads, syndrome criteria, and microscopic diagnostic patterns.",
     "⚡ Eponyms Drill"),

    ("MASTER OBSTETRIC INVESTIGATIONS & CUT-OFFS.html",
     "🧪", "color-teal", "obstetrics",
     "Obstetric Cut-Offs",
     "Master Obstetric Investigations & Diagnostic Cut-Offs (Part 1)",
     "103 structured tables outlining normal ranges, abnormal thresholds, and RCOG/NICE diagnostic cut-offs from early pregnancy to term.",
     "⚡ Cut-Offs Matrix"),

    ("MASTER OBSTETRIC INVESTIGATIONS & CUT-OFFS2.html",
     "🤰", "color-amber", "obstetrics",
     "Obstetric Signs",
     "Master Consolidated Obstetric Signs, Eponyms & Criteria (Part 2)",
     "Presumptive, probable, and positive pregnancy signs, labour mechanics, third-stage emergencies, and puerperal criteria.",
     "⚡ Rapid Drill"),

    ("MASTER OBSTETRIC \u201cBUGS\u201d CATALOGUE.html",
     "🧫", "color-rose", "microbiology obstetrics",
     "Perinatal Infections",
     "Master Obstetric \u201cBugs\u201d Catalogue",
     "Organism-by-organism breakdown of maternal disease, fetal transmission, TORCH profiles, congenital syndromes, and exam differentiation.",
     "⚡ TORCH Matrix"),

    ("MASTER RADIOLOGICAL SIGNS IN OBSTETRICS & GYNAECOLOGY.html",
     "📡", "color-blue", "imaging obstetrics gynaecology",
     "Ultrasound & Imaging",
     "Master Radiological Signs in Obstetrics & Gynaecology",
     "High-yield ultrasound patterns for ectopic pregnancy, early failure, twin chorionicity, placental invasion, and adnexal masses.",
     "⚡ Imaging Matrix"),

    ("MASTER \u2014 INVESTIGATION OF CHOICE IN GYNAECOLOGY.html",
     "📋", "color-teal", "gynaecology",
     "IOC & Gold Standards",
     "Master Investigation of Choice in Gynaecology",
     "Exhaustive guide to initial investigation of choice (IOC) vs Gold Standard (GS) across 164 clinical gynaecological conditions.",
     "⚡ Protocol Matrix"),

    ("rcog master table.html",
     "⏱️", "color-emerald", "obstetrics",
     "Delivery Timing",
     "RCOG Master Table \u2014 Ideal Time of Delivery",
     "Definitive gestational timing and delivery mode recommendations across 78 maternal, fetal, and placental conditions.",
     "⚡ Timing Matrix"),

    # ──── NEW 38 ──────────────────────────────────────────────────────────
    ("COMPLETE L&D TRIAGE ARRIVAL  ASSESSMENT  MANAGEMENT  DISPOSITION.html",
     "🚨", "color-rose", "obstetrics labour",
     "L&D Triage",
     "Complete L&D Triage — Arrival, Assessment, Management & Disposition",
     "Step-by-step labour ward triage workflow covering maternal assessment, fetal monitoring, disposition criteria, and management algorithms.",
     "⚡ Triage Drill"),

    ("COMPLETE OBGYN OPD MANAGEMENT LIST.html",
     "🏥", "color-teal", "gynaecology obstetrics",
     "OPD Management",
     "Complete OBGYN OPD Management List",
     "Comprehensive outpatient management protocols for over 90 obstetric and gynaecological conditions seen in clinical practice.",
     "⚡ OPD Protocols"),

    ("CONTRACEPTION \u2014 MRCOG PART 3 OSCE MASTER GUIDE.html",
     "💊", "color-purple", "gynaecology mrcog osce",
     "Contraception OSCE",
     "Contraception \u2014 MRCOG Part 3 OSCE Master Guide",
     "OSCE-structured guide to counselling, eligibility criteria, UKMEC classifications, failure rates, and patient communication for all contraceptive methods.",
     "⚡ Counselling Drill"),

    ("EMERGENCY OBSTETRICS \u2014 MRCOG PART 3 OSCE MASTER ATLAS.html",
     "⚡", "color-rose", "obstetrics mrcog osce emergencies",
     "Emergency Obstetrics",
     "Emergency Obstetrics \u2014 MRCOG Part 3 OSCE Master Atlas",
     "High-stakes obstetric emergencies including PPH, shoulder dystocia, cord prolapse, eclampsia, and uterine rupture with structured management steps.",
     "⚡ Emergency Drill"),

    ("GYNAECOLOGICAL SURGERYPreoperative assessment prerequisites and preparation.html",
     "🔬", "color-blue", "gynaecology surgery",
     "Surgical Pre-op",
     "Gynaecological Surgery — Preoperative Assessment, Prerequisites & Preparation",
     "Systematic preoperative assessment framework for gynaecological procedures including consent, risk stratification, and surgical preparation protocols.",
     "⚡ Pre-op Checklist"),

    ("GYNAECOLOGY DISCHARGE & FOLLOW-UP MASTER LIST.html",
     "📤", "color-teal", "gynaecology",
     "Discharge & Follow-up",
     "Gynaecology Discharge & Follow-Up Master List",
     "Condition-by-condition discharge criteria, follow-up intervals, red flag symptoms, and GP communication templates for gynaecological admissions.",
     "⚡ Discharge Drill"),

    ("Important Biochemistry, Immunopathology & Anatomical Landmarks in Gynaecology.html",
     "🔬", "color-amber", "gynaecology biochemistry",
     "Gyn Biochemistry",
     "Important Biochemistry, Immunopathology & Anatomical Landmarks in Gynaecology",
     "Key tumour markers, immune mechanisms, surgical landmarks, and anatomical reference points critical for gynaecological clinical practice.",
     "⚡ Landmark Drill"),

    ("Important Biochemistry, Immunopathology & Anatomical Landmarks in Obstetrics.html",
     "🧬", "color-blue", "obstetrics biochemistry",
     "Obs Biochemistry",
     "Important Biochemistry, Immunopathology & Anatomical Landmarks in Obstetrics",
     "Essential maternal biochemical adaptations, immunological mechanisms, placental markers, and anatomical landmarks in obstetric practice.",
     "⚡ Biochem Drill"),

    ("L&D TRIAGe clinical pathway.html",
     "🛤️", "color-emerald", "obstetrics labour",
     "Clinical Pathway",
     "L&D Triage Clinical Pathway",
     "Structured clinical decision pathway for labour ward triage from patient arrival through assessment, risk stratification, and disposition planning.",
     "⚡ Pathway Drill"),

    ("MASTER ATLAS \u2014 GYNAECOLOGICAL PROBLEMS IN PREGNANCY.html",
     "🤱", "color-purple", "gynaecology obstetrics",
     "Gyn in Pregnancy",
     "Master Atlas \u2014 Gynaecological Problems in Pregnancy",
     "Non-obstetric gynaecological conditions complicating pregnancy including adnexal masses, fibroids, cervical pathology, and VTE management.",
     "⚡ Problem Drill"),

    ("MASTER GYNECOLOGY PROCEDURES & OPERATIVE MANOEUVRES.html",
     "✂️", "color-blue", "gynaecology surgery procedures",
     "Gyn Procedures",
     "Master Gynecology Procedures & Operative Manoeuvres",
     "Complete atlas of gynaecological surgical techniques, step-by-step manoeuvres, instrument selection, and intraoperative decision-making.",
     "⚡ Procedure Drill"),

    ("MASTER LIST LABOUR-ROOM TRIAGE CASES AFTER 24 WEEKS.html",
     "🏥", "color-rose", "obstetrics labour",
     "Labour Room Triage",
     "Master List — Labour-Room Triage Cases After 24 Weeks",
     "Complete triage reference for presentations after 24 weeks gestation including antepartum haemorrhage, PROM, preterm labour, and hypertensive emergencies.",
     "⚡ Triage Matrix"),

    ("MASTER OBGYN DIFFERENTIAL & DEFINITIVE DIAGNOSIS ATLAS.html",
     "🔍", "color-purple", "obstetrics gynaecology diagnosis",
     "Differential Dx",
     "Master OBGYN Differential & Definitive Diagnosis Atlas",
     "Systematic approach to differential and definitive diagnosis across major obstetric and gynaecological presentations with discriminating features.",
     "⚡ Dx Drill"),

    ("MASTER OBGYN PROGNOSIS ATLAS \u2014 RCOG-FOCUSED.html",
     "📈", "color-amber", "obstetrics gynaecology rcog",
     "Prognosis Atlas",
     "Master OBGYN Prognosis Atlas \u2014 RCOG-Focused",
     "RCOG-aligned prognostic data, recurrence rates, survival statistics, and outcome predictors for major obstetric and gynaecological conditions.",
     "⚡ Prognosis Drill"),

    ("MASTER OBSTETRIC & GYNAECOLOGICAL DIAGNOSTIC CRITERIA.html",
     "📐", "color-teal", "obstetrics gynaecology",
     "Diagnostic Criteria",
     "Master Obstetric & Gynaecological Diagnostic Criteria",
     "Comprehensive reference of RCOG, NICE, and WHO diagnostic criteria for 30+ major conditions with thresholds, definitions, and classification systems.",
     "⚡ Criteria Drill"),

    ("MASTER OBSTETRIC & GYNAECOLOGICAL LABORATORY VALUE ATLAS.html",
     "🧪", "color-blue", "obstetrics gynaecology laboratory",
     "Lab Values",
     "Master Obstetric & Gynaecological Laboratory Value Atlas",
     "Trimester-specific reference ranges, critical values, and RCOG-aligned interpretation guides for haematological, biochemical, and endocrine lab tests.",
     "⚡ Lab Value Drill"),

    ("MASTER OBSTETRIC PROCEDURES & MANOEUVRES ATLAS.html",
     "🤲", "color-emerald", "obstetrics procedures",
     "Obstetric Procedures",
     "Master Obstetric Procedures & Manoeuvres Atlas",
     "Detailed step-by-step obstetric procedures including assisted delivery, manoeuvres for complications, operative techniques, and post-procedure management.",
     "⚡ Procedure Drill"),

    ("MASTER RCOG OBSTETRIC DELIVERY ATLAS.html",
     "👶", "color-rose", "obstetrics rcog delivery",
     "Delivery Atlas",
     "Master RCOG Obstetric Delivery Atlas",
     "RCOG-focused delivery timing, mode recommendations, and management algorithms across all major obstetric conditions — with clinical figures.",
     "⚡ Delivery Matrix"),

    ("MASTER RCOG OBSTETRIC DRUG REGIMENS.html",
     "💉", "color-purple", "obstetrics pharmacology rcog",
     "Drug Regimens",
     "Master RCOG Obstetric Drug Regimens",
     "Evidence-based pharmacological regimens for tocolysis, uterotonic therapy, antihypertensives, analgesia, and antibiotic protocols in obstetrics.",
     "⚡ Drug Drill"),

    ("MRCOG Part 3 OSCE \u2014 EARLY PREGNANCY ATLAS.html",
     "🫀", "color-blue", "obstetrics mrcog osce",
     "Early Pregnancy OSCE",
     "MRCOG Part 3 OSCE \u2014 Early Pregnancy Atlas",
     "Structured OSCE preparation for early pregnancy complications including miscarriage, ectopic, molar pregnancy, and hyperemesis — with clinical images.",
     "⚡ OSCE Drill"),

    ("MRCOG Part 3 OSCE \u2014 MENOPAUSE  ADOLESCENT GYNAECOLOGY FGM.html",
     "🌸", "color-amber", "gynaecology mrcog osce menopause",
     "Menopause & FGM OSCE",
     "MRCOG Part 3 OSCE \u2014 Menopause, Adolescent Gynaecology & FGM",
     "OSCE-structured communication and management for menopausal HRT, adolescent presentations, FGM classification, and safeguarding responsibilities.",
     "⚡ Communication Drill"),

    ("MRCOG Part 3 \u2014 Gynaecological Oncology OSCE Atlas.html",
     "🎗️", "color-rose", "gynaecology oncology mrcog osce",
     "Gyn Oncology OSCE",
     "MRCOG Part 3 \u2014 Gynaecological Oncology OSCE Atlas",
     "OSCE preparation for gynaecological malignancies including cervical, endometrial, ovarian, and vulval cancer with FIGO staging and management pathways.",
     "⚡ Oncology Drill"),

    ("MRCOG Part 3 \u2014 Gynaecology Clinical Examination & Pelvic Mass OSCE Atlas.html",
     "👁️", "color-teal", "gynaecology mrcog osce examination",
     "Pelvic Mass OSCE",
     "MRCOG Part 3 \u2014 Gynaecology Clinical Examination & Pelvic Mass OSCE Atlas",
     "Structured pelvic examination technique, mass characterisation, differentials, and OSCE communication frameworks for pelvic mass presentations.",
     "⚡ Examination Drill"),

    ("MRCOG Part 3 \u2014 OPERATIVE  TOACS OSCE MASTER GUIDE.html",
     "🔧", "color-purple", "gynaecology obstetrics mrcog operative",
     "Operative OSCE",
     "MRCOG Part 3 \u2014 Operative & TOACs OSCE Master Guide",
     "Task-Oriented Assessment of Clinical Skills guide covering structured operative communication, surgical consent, debriefing, and team management.",
     "⚡ TOACs Drill"),

    ("MRCOG Part 3 \u2014 PERFORMANCE & COMMUNICATION OSCE MASTER GUIDE.html",
     "💬", "color-blue", "mrcog osce communication",
     "Communication OSCE",
     "MRCOG Part 3 \u2014 Performance & Communication OSCE Master Guide",
     "Breaking bad news, obtaining consent, challenging consultations, multidisciplinary communication, and structured patient-centred frameworks.",
     "⚡ Communication Drill"),

    ("MRCOG Part 3 \u2014 SEXUAL HEALTH OSCE MASTER GUIDE.html",
     "💙", "color-emerald", "gynaecology mrcog osce sexual-health",
     "Sexual Health OSCE",
     "MRCOG Part 3 \u2014 Sexual Health OSCE Master Guide",
     "Sexual health history-taking, STI management, partner notification, HIV in pregnancy, and OSCE communication frameworks for sensitive consultations.",
     "⚡ Sexual Health Drill"),

    ("MRCOG Part 3 \u2014 UROGYNAECOLOGY OSCE ATLAS.html",
     "💧", "color-teal", "gynaecology mrcog osce urogynaecology",
     "Urogynaecology OSCE",
     "MRCOG Part 3 \u2014 Urogynaecology OSCE Atlas",
     "Structured OSCE preparation for urinary incontinence, prolapse assessment, urodynamics interpretation, and conservative versus surgical management.",
     "⚡ Urogynaecology Drill"),

    ("NON-OBSTETRIC GYNAECOLOGICAL EMERGENCIES.html",
     "🚑", "color-rose", "gynaecology emergencies",
     "Gyn Emergencies",
     "Non-Obstetric Gynaecological Emergencies",
     "Acute gynaecological presentations including ovarian torsion, ruptured ectopic, septic abortion, haemoperitoneum, and DUB emergency management.",
     "⚡ Emergency Drill"),

    ("O&G CONDITIONS REQUIRING MDT INVOLVEMENT.html",
     "👥", "color-amber", "obstetrics gynaecology mdt",
     "MDT Conditions",
     "O&G Conditions Requiring MDT Involvement",
     "Comprehensive list of obstetric and gynaecological conditions requiring multidisciplinary team input with referral criteria and specialist roles.",
     "⚡ MDT Drill"),

    ("OBGYN BIOPSIES \u2014 COMPLETE MRCOGFCPSOSCE MASTER LIST.html",
     "🔬", "color-purple", "gynaecology obstetrics biopsy mrcog",
     "Biopsies Atlas",
     "OBGYN Biopsies \u2014 Complete MRCOG/FCPS/OSCE Master List",
     "Complete reference of biopsy indications, techniques, sample processing, and histopathological interpretation across OBGYN practice.",
     "⚡ Biopsy Drill"),

    ("OBGYN OPD PROCEDURES \u2014 COMPLETE LIST.html",
     "🏥", "color-blue", "gynaecology obstetrics procedures",
     "OPD Procedures",
     "OBGYN OPD Procedures \u2014 Complete List",
     "Step-by-step outpatient procedure guides including colposcopy, hysteroscopy, LLETZ, IUD insertion, and speculum examination — with clinical images.",
     "⚡ Procedure Drill"),

    ("Obstetric discharge & follow-up \u2014 RCOG-style comprehensive checklist.html",
     "📋", "color-emerald", "obstetrics discharge",
     "Obs Discharge",
     "Obstetric Discharge & Follow-Up \u2014 RCOG-Style Comprehensive Checklist",
     "Structured postnatal discharge checklist covering maternal wellbeing, newborn checks, contraception advice, and scheduled follow-up appointments.",
     "⚡ Discharge Drill"),

    ("Postoperative assessment monitoring investigations examination Gynaecology.html",
     "📊", "color-amber", "gynaecology surgery postoperative",
     "Post-op Gynaecology",
     "Postoperative Assessment, Monitoring & Investigations — Gynaecology",
     "Systematic postoperative monitoring framework for gynaecological surgery including vital sign targets, investigation timelines, and complication identification.",
     "⚡ Post-op Drill"),

    ("Pre-operative assessment, prerequisites & preparation for obstetric.html",
     "📝", "color-teal", "obstetrics surgery preoperative",
     "Obs Pre-op",
     "Pre-operative Assessment, Prerequisites & Preparation for Obstetric Surgery",
     "Complete obstetric surgical preparation guide including anaesthetic assessment, blood product planning, consent frameworks, and team briefing protocols.",
     "⚡ Pre-op Drill"),

    ("RCOG BLOOD-PRODUCT PREPARATION ATLAS \u2014 O&G.html",
     "🩸", "color-rose", "obstetrics gynaecology blood haematology",
     "Blood Products",
     "RCOG Blood-Product Preparation Atlas \u2014 O&G",
     "RCOG-aligned guide to blood product ordering, crossmatch, massive transfusion protocols, and cell salvage in obstetric and gynaecological emergencies.",
     "⚡ Transfusion Drill"),

    ("RCOG POST-OPERATIVE OBSTETRIC ASSESSMENT \u2014 MASTER CHECKLIST.html",
     "✅", "color-blue", "obstetrics surgery postoperative",
     "Obs Post-op",
     "RCOG Post-Operative Obstetric Assessment \u2014 Master Checklist",
     "Structured post-operative assessment checklist following obstetric surgery, aligned with RCOG standards for enhanced recovery and early complication detection.",
     "⚡ Post-op Checklist"),

    ("REPRODUCTIVE MEDICINE \u2014 MRCOG PART 3 OSCE ATLAS.html",
     "🌱", "color-purple", "gynaecology mrcog osce fertility",
     "Reproductive Medicine",
     "Reproductive Medicine \u2014 MRCOG Part 3 OSCE Atlas",
     "OSCE preparation for fertility counselling, IVF pathways, recurrent miscarriage, PCOS, premature ovarian insufficiency, and assisted conception ethics.",
     "⚡ Fertility Drill"),

    ("gestational-age cut-off  timing-of-delivery table.html",
     "📅", "color-emerald", "obstetrics delivery timing",
     "GA Cut-off Table",
     "Gestational Age Cut-Off & Timing of Delivery Table",
     "Universal gestational age cut-off reference table with RCOG-recommended delivery timing windows for all major maternal and fetal conditions.",
     "⚡ Timing Drill"),

    ("MASTER MRCOG FCPS OG ATLAS.html",
     "🏆", "color-blue", "obstetrics gynaecology mrcog anatomy histology physiology",
     "MRCOG/FCPS Master Atlas",
     "Master MRCOG / FCPS O&G Atlas — Integrated Sciences & Clinical Medicine",
     "Mega integrated atlas covering anatomy, histology, embryology, physiology, pathology, surgery, and viva/OSCE pearls — the definitive MRCOG & FCPS revision reference.",
     "⚡ Viva Drill"),
]

COLORS = ['color-blue', 'color-teal', 'color-rose', 'color-amber', 'color-purple', 'color-emerald']


def url_encode(filename):
    """URL-encode special chars in filename for href."""
    return quote(filename, safe='')


def build_card_html(filename, icon, color, category, pill, title, desc, drill):
    href = url_encode(filename)
    return f"""
                <a href="{href}" class="module-card {color}" data-category="{category}">
                    <div>
                        <div class="card-top">
                            <div class="card-icon-badge">{icon}</div>
                            <span class="card-category-pill">{pill}</span>
                        </div>
                        <h2 class="card-title">{title}</h2>
                        <p class="card-desc">{desc}</p>
                        <div class="card-tags">
                            <span class="feature-tag">📖 Atlas Reader</span>
                            <span class="feature-tag">🗂️ Flashcards</span>
                            <span class="feature-tag">✍️ Board Quiz</span>
                            <span class="feature-tag">{drill}</span>
                        </div>
                    </div>
                    <div class="card-footer">
                        <span class="card-stats-text">Interactive Study Atlas</span>
                        <span class="btn-launch">Launch Atlas →</span>
                    </div>
                </a>"""


def build_all_cards():
    cards_html = ""
    for entry in CARD_CATALOG:
        filename, icon, color, category, pill, title, desc, drill = entry
        # Check if file actually exists in web_docs
        fpath = os.path.join(WEB_DOCS, filename)
        if not os.path.exists(fpath):
            print(f"  [WARN] HTML not found, skipping: {filename}")
            continue
        cards_html += build_card_html(filename, icon, color, category, pill, title, desc, drill)
    return cards_html


def update_portal_file(filepath, total_count):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Build new cards HTML
    new_cards = build_all_cards()

    # Replace the modules-container section content
    # Find the opening and closing of the modules section
    start_marker = '<section class="modules-grid" id="modules-container">'
    end_marker = '</section>'

    start_idx = content.find(start_marker)
    if start_idx == -1:
        print(f"  [WARN] Could not find modules-container in: {filepath}")
        return

    # Find the corresponding </section>
    search_from = start_idx + len(start_marker)
    end_idx = content.find(end_marker, search_from)
    if end_idx == -1:
        print(f"  [WARN] Could not find end of modules-container in: {filepath}")
        return

    end_idx += len(end_marker)

    new_section = f"""{start_marker}
{new_cards}

            {end_marker}"""

    content = content[:start_idx] + new_section + content[end_idx:]

    # Update the "All Modules (N)" count in filter button
    content = re.sub(
        r'All Modules \(\d+\)',
        f'All Modules ({total_count})',
        content
    )

    # Update stats counter if present
    content = re.sub(
        r'(\d+)\s*Atlases',
        f'{total_count} Atlases',
        content
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  [OK] Updated: {os.path.basename(filepath)} with {total_count} modules")


def main():
    print("Updating portal files with all 46 atlas links...\n")

    # Count how many entries have actual HTML files
    total = sum(1 for e in CARD_CATALOG if os.path.exists(os.path.join(WEB_DOCS, e[0])))
    print(f"Found {total} atlas HTML files\n")

    for fname in ['index.html', 'portal.html']:
        fpath = os.path.join(WEB_DOCS, fname)
        if os.path.exists(fpath):
            update_portal_file(fpath, total)
        else:
            print(f"  [SKIP] Not found: {fname}")

    print("\nDone.")


if __name__ == '__main__':
    main()
