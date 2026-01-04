import streamlit as st
import pandas as pd
from upload_handler import process_excel_file
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(
    page_title="NorimaRB",
    page_icon="🍔",
    layout="wide"
)

# --------------------------------------------------
# Session State
# --------------------------------------------------
defaults = {
    "required_file": None,
    "current_file": None,
    "required_sheets": None,   # FILTERED
    "current_sheets": None,    # RAW
    "missing_map": {},         # sheet -> missing row indices
    "reset_flag": False
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --------------------------------------------------
# Load external CSS
# --------------------------------------------------
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------- Warning --------
if st.session_state.required_file is None:
    st.warning("⚠️ Upload Required RateBook first to enable Current RateBook uploader.")

st.title("🍔 Norima Rate Book")

# --------------------------------------------------
# Reset Button
# --------------------------------------------------
if st.button("RESET"):
    streamlit_js_eval(js_expressions="parent.window.location.reload()")


# --------------------------------------------------
# Reset Logic
# --------------------------------------------------
if st.session_state.reset_flag:
    for k in defaults:
        st.session_state[k] = defaults[k]
    st.session_state.reset_flag = False
    st.rerun()

# --------------------------------------------------
# Uploader
# --------------------------------------------------
col1, col2 = st.columns(2)

# -------- Required File --------
with col1:
    file = st.file_uploader(
        "Upload Required RateBook", 
        type=["xlsx", "xls"], 
        key="required_uploader"
    )
    if file:
        if st.session_state.required_file != file:
            st.session_state.required_file = file
            with st.spinner(f"Processing {file.name}... 📘"):
                st.session_state.required_sheets = process_excel_file(file)
            st.toast(f"Required file uploaded: {file.name}", icon="📘")
        else:
            st.toast(f"Required file loaded: {file.name}")

# -------- Current File --------
with col2:
    if st.session_state.required_file is not None:
        file = st.file_uploader(
            "Upload Current RateBook", 
            type=["xlsx", "xls"], 
            key="current_uploader"
        )
        if file:
            if st.session_state.current_file != file:
                st.session_state.current_file = file
                with st.spinner(f"Processing {file.name}... 📗"):
                    st.session_state.current_sheets = pd.read_excel(file, sheet_name=None)
                st.toast(f"Current file uploaded: {file.name}", icon="📗")
            else:
                st.toast(f"Current file loaded: {file.name}")

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def normalize_value(val):
    if isinstance(val, str):
        val = val.strip().lower()
        if val in ["yes", "true"]:
            return True
        if val in ["no", "false"]:
            return False
        try:
            return float(val)
        except:
            return val
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, bool):
        return val
    return str(val).strip().lower()

def row_matches(req_row, cur_row):
    req_norm = [normalize_value(v) for v in req_row]
    cur_norm = [normalize_value(v) for v in cur_row]
    return all(any(r == c for c in cur_norm) for r in req_norm)

def highlight_missing(missing_indices):
    def _style(row):
        return [
            "background-color: #ffcccc" if row.name in missing_indices else ""
            for _ in row
        ]
    return _style

# --------------------------------------------------
# Comparison Logic
# --------------------------------------------------
if st.session_state.required_sheets and st.session_state.current_sheets:
    st.session_state.missing_map = {}

    with st.spinner("Comparing sheets, please wait... ⚡"):
     for sheet, req_df in st.session_state.required_sheets.items():

        if sheet not in st.session_state.current_sheets:
            st.session_state.missing_map[sheet] = list(req_df.index)
            continue

        cur_df = st.session_state.current_sheets[sheet]

        req_cmp = req_df.fillna("").astype(str)
        cur_cmp = cur_df.fillna("").astype(str)

        missing_indices = []

        for req_idx, req_row in req_cmp.iterrows():
            matched = any(
                row_matches(req_row, cur_row)
                for _, cur_row in cur_cmp.iterrows()
            )
            if not matched:
                missing_indices.append(req_idx)

        st.session_state.missing_map[sheet] = missing_indices

# --------------------------------------------------
# Display
# --------------------------------------------------
left, right = st.columns(2)

# -------- Required  --------
with left:
    if st.session_state.required_sheets:
        st.subheader("📂 Required File")

        for name, df in st.session_state.required_sheets.items():
            missing = st.session_state.missing_map.get(name, [])

            styled_df = (
                df.style.apply(highlight_missing(missing), axis=1)
                if missing else df
            )

            with st.expander(f"📑 {name} ({df.shape[0]} rows)"):
                st.dataframe(styled_df, use_container_width=True)

# -------- Current + Status --------
with right:
    if st.session_state.current_sheets:
        st.subheader("📂 Ratebook ")

        for sheet, cur_df in st.session_state.current_sheets.items():
            missing = st.session_state.missing_map.get(sheet, [])

            if sheet not in st.session_state.required_sheets:
                status = "ℹ️ Not required"
            elif not missing:
                status = "✅ All required rows match"
            else:
                status = f"⚠️ {len(missing)} required row/s mismatch"

            with st.expander(
                f"📑 {sheet} ({cur_df.shape[0]} rows) — {status}",
                expanded=False
            ):
                st.dataframe(cur_df, use_container_width=True)