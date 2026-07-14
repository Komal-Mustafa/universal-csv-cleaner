import streamlit as st

# ------------------------------------------------------
# Universal Messy Data Cleaner Agent
# Upload any messy CSV/TXT file and this agent will clean it:
# - removes empty / null / blank values
# - removes extra whitespace
# - removes duplicate rows
# - fills missing numeric cells with mean/median (or N/A)
# - standardizes messy category text (Male/male/M -> Male)
# Built using only core python logic (strings, lists, loops,
# dictionaries, conditionals) - no pandas used.
# ------------------------------------------------------

st.set_page_config(page_title="Universal Data Cleaner", page_icon="🧹")

st.title("🧹 Universal Messy Data Cleaner Agent")
st.write(
    "Upload a messy CSV or TXT file, or paste data manually below. "
    "The agent will strip whitespace, remove empty/null values, fill missing "
    "numeric cells with mean or median, and remove duplicate rows."
)

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
    # for each column, collect valid numeric values and work out mean/median
    stats_per_col = []

    for col_index in range(num_columns):
        values = []
        for row in all_rows:
            if col_index < len(row):
                cell = row[col_index]
                if cell != "" and is_number(cell):
                    values.append(float(cell))

        if len(values) == 0:
            stats_per_col.append(None)  # not a numeric column / no data
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

    # first pass - just clean whitespace/junk, don't drop anything yet
    all_rows = []
    for line in lines:
        if line.strip() == "":
            continue
        all_rows.append(clean_row(line))

    # figure out how many columns this data has (use the widest row)
    num_columns = 0
    for row in all_rows:
        if len(row) > num_columns:
            num_columns = len(row)

    # work out mean/median per column, only needed if user picked that mode
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

                # decide what to fill this blank cell with
                if blank_mode in ("mean", "median") and column_stats is not None:
                    col_stat = column_stats[col_index] if col_index < len(column_stats) else None
                    if col_stat is not None:
                        fill_value = col_stat[blank_mode]
                        filled_values.append(str(round(fill_value, 2)))
                    else:
                        filled_values.append("N/A")  # not a numeric column
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


# --- Input section: file upload OR manual paste ---

uploaded_file = st.file_uploader("Upload a CSV or TXT file", type=["csv", "txt"])

sample = """John Doe,  , john@email.com
Jane Smith, 25, jane@email.com
John Doe,  , john@email.com
  , 30, mark@email.com
Sara Ali, null, sara@email.com
Sara Ali, null, sara@email.com
"""

raw_text = ""

if uploaded_file is not None:
    raw_bytes = uploaded_file.read()
    raw_text = raw_bytes.decode("utf-8", errors="ignore")
    st.success(f"File uploaded: {uploaded_file.name}")
    st.text_area("Preview of uploaded data", value=raw_text, height=180, disabled=True)
else:
    raw_text = st.text_area(
        "Or paste your messy data here (used only if no file is uploaded)",
        value=sample,
        height=180
    )

st.subheader("Cleaning Options")

blank_choice = st.radio(
    "What should happen to blank/missing cells?",
    [
        "Fill with Mean (numeric columns only)",
        "Fill with Median (numeric columns only)",
        "Fill with 'N/A'",
        "Remove the whole row"
    ],
    index=0
)

if blank_choice.startswith("Fill with Mean"):
    blank_mode = "mean"
elif blank_choice.startswith("Fill with Median"):
    blank_mode = "median"
elif blank_choice.startswith("Fill with 'N/A'"):
    blank_mode = "fill_na"
else:
    blank_mode = "remove"

standardize_choice = st.checkbox(
    "Standardize messy category values (Male/male/M -> Male, IT/it/I.T. -> IT, etc.)",
    value=True
)

st.caption(
    "Note: Mean/Median only applies to columns where the values are numbers "
    "(like age or salary). Text columns with blanks will still be filled with 'N/A'."
)

if st.button("Clean My Data"):
    if raw_text.strip() == "":
        st.warning("Please upload a file or paste some data first!")
    else:
        cleaned_rows, stats = clean_data(raw_text, blank_mode=blank_mode, standardize=standardize_choice)

        st.subheader("Cleaning Report")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Total Rows", stats["total_rows"])
        col2.metric("Empty Rows Removed", stats["empty_rows_removed"])
        col3.metric("Rows w/ Missing Removed", stats["rows_removed_missing_cell"])
        col4.metric("Rows w/ Blanks Filled", stats["cells_filled"])
        col5.metric("Duplicates Removed", stats["duplicate_rows_removed"])
        col6.metric("Final Rows", stats["final_rows"])

        st.subheader("Cleaned Data")

        if len(cleaned_rows) == 0:
            st.warning("Nothing left after cleaning. All rows were empty or duplicates.")
        else:
            st.table(cleaned_rows)

            output_lines = []
            for row in cleaned_rows:
                output_lines.append(",".join(row))
            output_text = "\n".join(output_lines)

            st.download_button(
                label="Download Cleaned Data (CSV)",
                data=output_text,
                file_name="cleaned_data.csv",
                mime="text/csv"
            )