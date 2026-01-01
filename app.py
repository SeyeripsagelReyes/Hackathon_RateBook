import streamlit as st
import pandas as pd
from upload_handler import process_excel_file

st.set_page_config(
    page_title="NorimaRB",
    page_icon="🍔",
    layout="wide"
)

st.title("Norima Rate Book")

# --------------------------------------------------
# Load external CSS
# --------------------------------------------------
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --------------------------------------------------
# Session State
# --------------------------------------------------
defaults = {
    "required_file": None,
    "current_file": None,
    "required_sheets": None,   # FILTERED
    "current_sheets": None,    # RAW
    "reset_flag": False
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --------------------------------------------------
# Reset Logic
# --------------------------------------------------
if st.session_state.reset_flag:
    for k in defaults:
        st.session_state[k] = defaults[k]
    st.session_state.reset_flag = False
    st.rerun()

# --------------------------------------------------
# Upload Section
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    if st.session_state.required_file is None:
        file = st.file_uploader("Upload Required RateBook", type=["xlsx", "xls"])
        if file:
            st.session_state.required_file = file
            st.session_state.required_sheets = process_excel_file(file)
            st.success(f"✅ Required file uploaded: {file.name}")
    else:
        st.success(f"✅ Required file: {st.session_state.required_file.name}")

with col2:
    if st.session_state.required_file and st.session_state.current_file is None:
        file = st.file_uploader("Upload Current RateBook", type=["xlsx", "xls"])
        if file:
            st.session_state.current_file = file
            st.session_state.current_sheets = pd.read_excel(file, sheet_name=None)
            st.success(f"✅ Current file uploaded: {file.name}")
    elif st.session_state.current_file:
        st.success(f"✅ Current file: {st.session_state.current_file.name}")

# --------------------------------------------------
# Display
# --------------------------------------------------
left, right = st.columns(2)

# -------- Required (Filtered) --------
with left:
    if st.session_state.required_sheets:
        st.subheader("📂 Required File (Filtered)")
        for name, df in st.session_state.required_sheets.items():
            with st.expander(f"📑 {name} ({df.shape[0]} rows)"):
                st.dataframe(df, use_container_width=True)
    else:
        st.info("Upload Required RateBook to start.")

# -------- Current + Comparison --------
with right:
    if st.session_state.current_sheets:
        st.subheader("📂 Current File (Compared to Required)")

        def normalize_value(val):
            """Normalize for comparison"""
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
            """Check if all values in req_row exist in cur_row"""
            req_norm = [normalize_value(v) for v in req_row]
            cur_norm = [normalize_value(v) for v in cur_row]
            return all(any(r == c for c in cur_norm) for r in req_norm)

        with st.spinner("🔄 Comparing required rows with current file..."):
            for sheet, req_df in st.session_state.required_sheets.items():

                if sheet not in st.session_state.current_sheets:
                    st.error(f"❌ Sheet '{sheet}' missing in Current File")
                    continue

                cur_df = st.session_state.current_sheets[sheet]

                # Fill NaNs and convert to strings for normalization
                req_cmp = req_df.fillna("").astype(str)
                cur_cmp = cur_df.fillna("").astype(str)

                # Find missing rows
                missing_rows = []
                for req_idx, req_row in req_cmp.iterrows():
                    matched = any(row_matches(req_row, cur_row) for _, cur_row in cur_cmp.iterrows())
                    if not matched:
                        missing_rows.append(req_row)

                if not missing_rows:
                    status = "✅ All required rows exist"
                else:
                    status = f"⚠️ {len(missing_rows)} required rows missing"

                with st.expander(
                    f"📑 {sheet} ({cur_df.shape[0]} rows) — {status}",
                    expanded=False
                ):
                    st.dataframe(cur_df, use_container_width=True)


# --------------------------------------------------
# Floating Remove Button
# --------------------------------------------------
if st.session_state.required_file:
    if st.button("Reset"):
        st.session_state.reset_flag = True
        st.rerun()
