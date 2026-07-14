import streamlit as st

# ============================================================
# Data Cleaner Aura
# Upload a messy CSV/TXT file (or paste raw data) and clean it:
#   - strips whitespace, drops null/blank tokens
#   - removes fully empty rows and exact duplicate rows
#   - fills missing numeric cells with mean / median / N/A
#   - normalizes messy category text (Male/male/M -> Male)
# Pure core-Python logic (strings, lists, dicts, loops) — no pandas.
# ============================================================

st.set_page_config(
    page_title="Data Cleaner Aura",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# THEME / STYLE
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap');

    :root{
        --bg-0:#0a0716;
        --bg-1:#120e24;
        --card:rgba(28,22,48,0.55);
        --card-border:rgba(190,150,255,0.16);
        --line:rgba(180,170,210,0.14);
        --aura-1:#a15bff;
        --aura-2:#ff5fb0;
        --aura-3:#3fd6ff;
        --aura-4:#5ce8b8;
        --text-hi:#f3eefc;
        --text-lo:#a396c0;
        --danger:#ff6b8b;
        --warn:#ffb454;
        --radius:16px;
    }

    html, body, [class*="css"]{ font-family:'Inter', sans-serif; }

    /* ---------- animated aurora background ---------- */
    [data-testid="stAppViewContainer"]{
        background: var(--bg-0);
        position: relative;
        overflow: hidden;
    }
    [data-testid="stAppViewContainer"]::before{
        content:"";
        position: fixed; inset: -20%;
        background:
            radial-gradient(700px 480px at 15% 10%, rgba(161,91,255,0.30), transparent 60%),
            radial-gradient(650px 500px at 85% 15%, rgba(255,95,176,0.22), transparent 60%),
            radial-gradient(750px 550px at 50% 90%, rgba(63,214,255,0.18), transparent 60%),
            radial-gradient(500px 400px at 90% 80%, rgba(92,232,184,0.14), transparent 60%);
        filter: blur(10px);
        animation: auroraDrift 22s ease-in-out infinite alternate;
        z-index: 0;
        pointer-events: none;
    }
    @keyframes auroraDrift{
        0%   { transform: translate(0,0) scale(1); }
        50%  { transform: translate(-2%, 2%) scale(1.06); }
        100% { transform: translate(2%, -2%) scale(1.02); }
    }
    [data-testid="stHeader"]{ background: transparent; }
    .block-container{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px; position: relative; z-index: 1; }

    /* ---------- Hero header ---------- */
    .hero-wrap{ position:relative; padding: 6px 0 26px 0; }
    .hero-row{ display:flex; align-items:center; gap:16px; }
    .logo-mark{
        width:44px; height:44px; border-radius:13px; flex-shrink:0;
        background: conic-gradient(from 200deg, var(--aura-1), var(--aura-2), var(--aura-3), var(--aura-4), var(--aura-1));
        box-shadow: 0 0 0 1px rgba(255,255,255,0.08) inset, 0 0 32px rgba(161,91,255,0.55);
        position:relative;
        animation: logoGlow 4s ease-in-out infinite;
    }
    @keyframes logoGlow{
        0%, 100% { box-shadow: 0 0 0 1px rgba(255,255,255,0.08) inset, 0 0 26px rgba(161,91,255,0.45); }
        50%      { box-shadow: 0 0 0 1px rgba(255,255,255,0.08) inset, 0 0 40px rgba(255,95,176,0.55); }
    }
    .logo-mark::after{
        content:""; position:absolute; inset:6px; border-radius:9px; background: var(--bg-0);
    }
    .brand-title{
        font-family:'Space Grotesk', sans-serif; font-weight:700; font-size:1.75rem;
        letter-spacing:-0.02em; line-height:1.1; margin:0;
        background: linear-gradient(90deg, #f3eefc 0%, #d9c8ff 45%, #ffc7e6 100%);
        -webkit-background-clip: text; background-clip: text; color: transparent;
    }
    .brand-tag{
        display:inline-block; margin-left:12px; padding:3px 10px; border-radius:100px;
        font-family:'JetBrains Mono', monospace; font-size:0.62rem; letter-spacing:0.08em;
        color: var(--aura-4); border:1px solid rgba(92,232,184,0.4); background: rgba(92,232,184,0.08);
        vertical-align: middle;
    }
    .brand-sub{
        color: var(--text-lo); font-size:0.95rem; margin: 10px 0 0 60px; max-width:640px; line-height:1.6;
    }
    .hero-divider{
        height:1px; margin-top:24px;
        background: linear-gradient(90deg, rgba(161,91,255,0.55), rgba(255,95,176,0.25), transparent);
    }

    /* ---------- Section labels ---------- */
    .section-label{
        font-family:'JetBrains Mono', monospace; font-size:0.72rem; letter-spacing:0.12em;
        color: var(--aura-3); text-transform:uppercase; margin: 32px 0 12px 0; font-weight:500;
        display:flex; align-items:center; gap:10px;
    }
    .section-label::after{ content:""; flex:1; height:1px; background: var(--line); }

    /* ---------- Tabs ---------- */
    [data-baseweb="tab-list"]{ gap: 4px; border-bottom: 1px solid var(--line); }
    [data-baseweb="tab"]{
        font-family:'Inter', sans-serif; font-weight:500; font-size:0.9rem; color: var(--text-lo);
        padding: 10px 4px; margin-right: 24px; transition: color .2s ease;
    }
    [data-baseweb="tab"]:hover{ color: var(--text-hi); }
    [data-baseweb="tab"] p { font-size: 0.88rem; }
    [aria-selected="true"][data-baseweb="tab"]{ color: var(--text-hi) !important; }
    [data-baseweb="tab-highlight"]{
        background: linear-gradient(90deg, var(--aura-1), var(--aura-2)) !important; height:2px;
    }
    [data-baseweb="tab-border"]{ display:none; }

    /* ---------- File uploader ---------- */
    [data-testid="stFileUploaderDropzone"]{
        background: rgba(255,255,255,0.02);
        border: 1.5px dashed rgba(161,91,255,0.35);
        border-radius: 14px;
        transition: border-color .25s ease, background .25s ease, box-shadow .25s ease;
    }
    [data-testid="stFileUploaderDropzone"]:hover{
        border-color: rgba(255,95,176,0.7);
        background: rgba(161,91,255,0.06);
        box-shadow: 0 0 24px -6px rgba(161,91,255,0.4);
    }
    [data-testid="stFileUploaderDropzone"] button{
        background: transparent !important; color: var(--aura-3) !important;
        border: 1px solid rgba(63,214,255,0.4) !important; border-radius: 9px !important;
        transition: all .2s ease !important;
    }
    [data-testid="stFileUploaderDropzone"] button:hover{
        background: rgba(63,214,255,0.14) !important; border-color: var(--aura-3) !important;
    }

    /* ---------- Text area ---------- */
    .stTextArea textarea{
        background: rgba(255,255,255,0.025) !important; color: var(--text-hi) !important;
        border: 1px solid var(--line) !important; border-radius: 12px !important;
        font-family:'JetBrains Mono', monospace !important; font-size: 0.82rem !important;
        line-height:1.6 !important;
    }
    .stTextArea textarea:focus{
        border-color: var(--aura-1) !important; box-shadow: 0 0 0 1px var(--aura-1), 0 0 22px -4px rgba(161,91,255,0.5) !important;
    }

    /* ---------- Radio (segmented pills) ---------- */
    div[role="radiogroup"]{ gap: 8px; }
    div[role="radiogroup"] label{
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--line);
        padding: 10px 15px; border-radius: 10px; margin-right: 6px;
        transition: all .2s ease;
    }
    div[role="radiogroup"] label:hover{
        border-color: rgba(161,91,255,0.6); background: rgba(161,91,255,0.08);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px -8px rgba(161,91,255,0.5);
    }
    div[role="radiogroup"] label div:first-child{ display:none; }

    /* ---------- Checkbox ---------- */
    .stCheckbox label p{ color: var(--text-hi) !important; font-size:0.9rem; }

    /* ---------- Buttons (shine-on-hover) ---------- */
    .stButton>button{
        width:100%; position: relative; overflow: hidden; isolation: isolate;
        background: linear-gradient(135deg, var(--aura-1) 0%, var(--aura-2) 55%, var(--aura-3) 100%);
        background-size: 200% 200%;
        color:#0a0716; font-weight:700; font-family:'Space Grotesk', sans-serif;
        border:none; border-radius:12px; padding: 0.75rem 1rem; font-size:0.98rem;
        letter-spacing:0.01em;
        box-shadow: 0 8px 24px -8px rgba(161,91,255,0.65);
        transition: transform .2s ease, box-shadow .2s ease, background-position .5s ease;
    }
    .stButton>button:hover{
        transform: translateY(-3px);
        box-shadow: 0 16px 34px -8px rgba(255,95,176,0.6);
        background-position: 100% 50%;
    }
    .stButton>button:active{ transform: translateY(-1px) scale(.99); }

    .stDownloadButton>button{
        width:100%;
        background: rgba(92,232,184,0.08);
        color: var(--aura-4); font-weight:600; font-family:'Space Grotesk', sans-serif;
        border:1px solid rgba(92,232,184,0.4); border-radius:12px; padding:0.68rem 1rem;
        transition: all .2s ease;
    }
    .stDownloadButton>button:hover{
        background: rgba(92,232,184,0.18); border-color: var(--aura-4);
        transform: translateY(-3px); box-shadow: 0 14px 28px -10px rgba(92,232,184,0.55);
    }

    /* ---------- Metric stat cards ---------- */
    .stat-grid{ display:grid; grid-template-columns: repeat(6, 1fr); gap:12px; margin: 6px 0 4px 0; }
    .stat-card{
        background: var(--card); border:1px solid var(--card-border); border-radius:14px;
        padding: 16px 15px 13px 15px; position:relative; overflow:hidden;
        backdrop-filter: blur(12px);
        transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
    }
    .stat-card:hover{
        transform: translateY(-4px);
        border-color: rgba(161,91,255,0.55);
        box-shadow: 0 14px 30px -10px rgba(161,91,255,0.4);
    }
    .stat-card::before{
        content:""; position:absolute; top:0; left:0; right:0; height:3px;
        background: linear-gradient(90deg, var(--aura-1), var(--aura-2), var(--aura-3));
    }
    .stat-num{
        font-family:'JetBrains Mono', monospace; font-weight:700; font-size:1.6rem; color: var(--text-hi);
        line-height:1.1;
    }
    .stat-label{
        color: var(--text-lo); font-size:0.68rem; margin-top:7px; letter-spacing:0.03em;
        text-transform:uppercase; line-height:1.3;
    }
    .stat-card.warn .stat-num{ color: var(--warn); }
    .stat-card.danger .stat-num{ color: var(--danger); }
    .stat-card.ok .stat-num{ color: var(--aura-4); }

    @media (max-width: 900px){ .stat-grid{ grid-template-columns: repeat(3, 1fr); } }
    @media (max-width: 560px){
        .stat-grid{ grid-template-columns: repeat(2, 1fr); }
        .brand-title{ font-size:1.35rem; }
        .brand-sub{ margin-left:0; margin-top:14px; }
        .hero-row{ flex-wrap:wrap; }
    }

    /* ---------- Dataframe ---------- */
    [data-testid="stDataFrame"]{
        border:1px solid var(--card-border); border-radius:14px; overflow:hidden;
    }

    /* ---------- Misc text ---------- */
    .stCaption, .stMarkdown p{ color: var(--text-lo); }
    .footer-note{
        margin-top: 44px; padding-top:18px; border-top:1px solid var(--line);
        color: var(--text-lo); font-size:0.78rem; display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;
    }
    .footer-note span.mono{ font-family:'JetBrains Mono', monospace; color: rgba(161,91,255,0.8); }

    #MainMenu{visibility:hidden;} footer{visibility:hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# CORE CLEANING LOGIC (unchanged)
# ------------------------------------------------------------
junk_values = ["", "none", "null", "n/a", "na", "nan", "-"]

standard_map = {
    "male": "Male", "m": "Male",
    "female": "Female", "f": "Female",
    "ops": "Operations", "operations": "Operations",
    "it": "IT", "i.t.": "IT",
    "hr": "Human Resources", "human resources": "Human Resources",
    "finance": "Finance",
    "sales": "Sales",
    "yes": "Yes", "no": "No"
}


def clean_row(row):
    parts = row.split(",")
    cleaned_parts = []
    for value in parts:
        value = value.strip()
        if value.lower() in junk_values:
            value = ""
        cleaned_parts.append(value)
    return cleaned_parts


def is_row_empty(row_values):
    empty_count = 0
    for v in row_values:
        if v == "":
            empty_count += 1
    return empty_count == len(row_values)


def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def standardize_value(value):
    key = value.lower().strip()
    if key in standard_map:
        return standard_map[key]
    return value


def calculate_column_stats(all_rows, num_columns):
    stats_per_col = []
    for col_index in range(num_columns):
        values = []
        for row in all_rows:
            if col_index < len(row):
                cell = row[col_index]
                if cell != "" and is_number(cell):
                    values.append(float(cell))

        if len(values) == 0:
            stats_per_col.append(None)
        else:
            mean_val = sum(values) / len(values)
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            if n % 2 == 1:
                median_val = sorted_vals[n // 2]
            else:
                median_val = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2
            stats_per_col.append({"mean": mean_val, "median": median_val})
    return stats_per_col


def clean_data(raw_text, blank_mode="fill_na", standardize=True):
    lines = raw_text.strip().split("\n")

    all_rows = []
    for line in lines:
        if line.strip() == "":
            continue
        all_rows.append(clean_row(line))

    num_columns = 0
    for row in all_rows:
        if len(row) > num_columns:
            num_columns = len(row)

    column_stats = None
    if blank_mode in ("mean", "median"):
        column_stats = calculate_column_stats(all_rows, num_columns)

    cleaned_rows = []
    seen_rows = []

    stats = {
        "total_rows": 0,
        "empty_rows_removed": 0,
        "rows_removed_missing_cell": 0,
        "cells_filled": 0,
        "duplicate_rows_removed": 0,
        "final_rows": 0
    }

    for row_values in all_rows:
        stats["total_rows"] += 1

        if is_row_empty(row_values):
            stats["empty_rows_removed"] += 1
            continue

        has_blank = "" in row_values

        if has_blank:
            if blank_mode == "remove":
                stats["rows_removed_missing_cell"] += 1
                continue

            filled_values = []
            for col_index, v in enumerate(row_values):
                if v != "":
                    filled_values.append(v)
                    continue

                if blank_mode in ("mean", "median") and column_stats is not None:
                    col_stat = column_stats[col_index] if col_index < len(column_stats) else None
                    if col_stat is not None:
                        fill_value = col_stat[blank_mode]
                        filled_values.append(str(round(fill_value, 2)))
                    else:
                        filled_values.append("N/A")
                else:
                    filled_values.append("N/A")

            row_values = filled_values
            stats["cells_filled"] += 1

        if standardize:
            row_values = [standardize_value(v) for v in row_values]

        row_key = ",".join(row_values).lower()

        duplicate_found = False
        for old_key in seen_rows:
            if old_key == row_key:
                duplicate_found = True
                break

        if duplicate_found:
            stats["duplicate_rows_removed"] += 1
            continue

        seen_rows.append(row_key)
        cleaned_rows.append(row_values)

    stats["final_rows"] = len(cleaned_rows)
    return cleaned_rows, stats


# ------------------------------------------------------------
# HERO SECTION
# ------------------------------------------------------------
st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-row">
            <div class="logo-mark"></div>
            <div>
                <h1 class="brand-title">Data Cleaner Aura<span class="brand-tag">v3.0</span></h1>
            </div>
        </div>
        <p class="brand-sub">
            Drop in a messy CSV or TXT export and get back a normalized, deduplicated,
            analysis-ready dataset — whitespace stripped, nulls resolved, categories standardized.
        </p>
        <div class="hero-divider"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# INPUT
# ------------------------------------------------------------
st.markdown('<div class="section-label">Data Source</div>', unsafe_allow_html=True)

sample = """John Doe,  , john@email.com
Jane Smith, 25, jane@email.com
John Doe,  , john@email.com
  , 30, mark@email.com
Sara Ali, null, sara@email.com
Sara Ali, null, sara@email.com
"""

raw_text = ""
tab_upload, tab_paste = st.tabs(["Upload File", "Paste Raw Data"])

with tab_upload:
    uploaded_file = st.file_uploader(
        "Upload a CSV or TXT file", type=["csv", "txt"], label_visibility="collapsed"
    )
    if uploaded_file is not None:
        raw_bytes = uploaded_file.read()
        raw_text = raw_bytes.decode("utf-8", errors="ignore")
        st.caption(f"Loaded **{uploaded_file.name}** · {len(raw_text.splitlines())} lines")
        st.text_area("Preview", value=raw_text, height=160, disabled=True, label_visibility="collapsed")

with tab_paste:
    pasted_text = st.text_area(
        "Paste your messy data",
        value=sample,
        height=160,
        label_visibility="collapsed",
    )
    if uploaded_file is None:
        raw_text = pasted_text

# ------------------------------------------------------------
# OPTIONS
# ------------------------------------------------------------
st.markdown('<div class="section-label">Cleaning Rules</div>', unsafe_allow_html=True)

opt_col1, opt_col2 = st.columns([2, 1], gap="large")

with opt_col1:
    st.markdown("**Missing / blank cell handling**")
    blank_choice = st.radio(
        "Blank handling",
        [
            "Fill with Mean (numeric columns)",
            "Fill with Median (numeric columns)",
            "Fill with 'N/A'",
            "Remove the row",
        ],
        index=0,
        label_visibility="collapsed",
        horizontal=True,
    )
    st.caption("Mean/Median applies only to numeric columns — text columns fall back to 'N/A'.")

with opt_col2:
    st.markdown("**Category normalization**")
    standardize_choice = st.checkbox(
        "Standardize category text (Male/male/M → Male, IT/it → IT, ...)",
        value=True,
    )

if blank_choice.startswith("Fill with Mean"):
    blank_mode = "mean"
elif blank_choice.startswith("Fill with Median"):
    blank_mode = "median"
elif blank_choice.startswith("Fill with 'N/A'"):
    blank_mode = "fill_na"
else:
    blank_mode = "remove"

st.write("")
run = st.button("Run Cleaning Pipeline")

# ------------------------------------------------------------
# OUTPUT
# ------------------------------------------------------------
if run:
    if raw_text.strip() == "":
        st.warning("Upload a file or paste some data first.")
    else:
        with st.spinner("Processing rows..."):
            cleaned_rows, stats = clean_data(raw_text, blank_mode=blank_mode, standardize=standardize_choice)

        st.markdown('<div class="section-label">Cleaning Report</div>', unsafe_allow_html=True)

        card_defs = [
            ("Total Rows", stats["total_rows"], ""),
            ("Empty Removed", stats["empty_rows_removed"], "warn"),
            ("Missing Removed", stats["rows_removed_missing_cell"], "warn"),
            ("Blanks Filled", stats["cells_filled"], ""),
            ("Duplicates Removed", stats["duplicate_rows_removed"], "danger"),
            ("Final Rows", stats["final_rows"], "ok"),
        ]
        cards_html = '<div class="stat-grid">'
        for label, value, cls in card_defs:
            cards_html += (
                f'<div class="stat-card {cls}">'
                f'<div class="stat-num">{value}</div>'
                f'<div class="stat-label">{label}</div>'
                f"</div>"
            )
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Cleaned Dataset</div>', unsafe_allow_html=True)

        if len(cleaned_rows) == 0:
            st.warning("Nothing left after cleaning — all rows were empty or duplicates.")
        else:
            st.dataframe(cleaned_rows, use_container_width=True, height=min(420, 44 + 35 * len(cleaned_rows)))

            output_lines = []
            for row in cleaned_rows:
                output_lines.append(",".join(row))
            output_text = "\n".join(output_lines)

            dl_col, _ = st.columns([1, 3])
            with dl_col:
                st.download_button(
                    label="Download CSV",
                    data=output_text,
                    file_name="cleaned_data.csv",
                    mime="text/csv",
                )

st.markdown(
    """
    <div class="footer-note">
        <span>Data Cleaner Aura · pure-Python pipeline, no external data libraries</span>
        <span class="mono">v3.0</span>
    </div>
    """,
    unsafe_allow_html=True,
)

