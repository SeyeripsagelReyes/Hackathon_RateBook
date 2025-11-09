import streamlit as st
from upload_handler import process_excel_file

st.set_page_config(
    page_title="NorimaRB",
    page_icon="🍔",
    layout="wide"
)

st.title("Norima Rate Book")

# Initialize session state
for key in ["required_processed", "required_sheets", "current_file", "required_file_name", "remove_required_flag"]:
    if key not in st.session_state:
        st.session_state[key] = False if "processed" in key or "flag" in key else None
        if key == "required_sheets":
            st.session_state[key] = {}

# Handle remove request at the very top
if st.session_state.remove_required_flag:
    # Reset all state
    st.session_state.required_processed = False
    st.session_state.required_sheets = {}
    st.session_state.required_file_name = None
    st.session_state.current_file = None
    st.session_state.remove_required_flag = False
    st.rerun()  # Safe to rerun at the very start
    st.stop()

# Side-by-side uploaders
col1, col2 = st.columns(2)

with col1:
    # Show uploader if no required file uploaded
    if not st.session_state.required_processed:
        required_file = st.file_uploader("Upload Required RateBook Data", type=["xlsx", "xls"])
        if required_file:
            st.session_state.required_sheets = process_excel_file(required_file)
            st.session_state.required_processed = True
            st.session_state.required_file_name = required_file.name
            st.success(f"✅ Required File processed: {required_file.name}")
    else:
        st.success(f"✅ Required File uploaded: {st.session_state.required_file_name}")
        # Flag the remove request instead of rerunning immediately
        if st.button("Remove Required File", key="remove_required"):
            st.session_state.remove_required_flag = True
            st.rerun()

with col2:
    # Show Current File uploader only if Required File is processed
    if st.session_state.required_processed:
        st.session_state.current_file = st.file_uploader(
            "Upload Current RateBook Data", type=["xlsx", "xls"], key="current_uploader"
        )
        if st.session_state.current_file:
            st.success(f"✅ Current File uploaded: {st.session_state.current_file.name}")

# Display side by side
col_left, col_right = st.columns(2)

# Left section: Required File #
with col_left:
    if st.session_state.required_processed:
        st.subheader(f"📂 Required File: {st.session_state.required_file_name}")
        for sheet_name, df in st.session_state.required_sheets.items():
            row_count, col_count = df.shape
            with st.expander(f"📑 {sheet_name} — {row_count} rows × {col_count} cols", expanded=False):
                st.dataframe(df, use_container_width=True)
    else:
        st.info("Upload Required RateBook Data to start.")

# Right section: Current File #
with col_right:
    if st.session_state.current_file:
        st.subheader(f"📂 Current File: {st.session_state.current_file.name}")
        current_sheets = process_excel_file(st.session_state.current_file)
        for sheet_name, df in current_sheets.items():
            row_count, col_count = df.shape
            with st.expander(f"📑 {sheet_name} — {row_count} rows × {col_count} cols", expanded=False):
                st.dataframe(df, use_container_width=True)
    elif st.session_state.required_processed:
        st.info("Upload Current RateBook Data to compare with Required Ratebook Data.")
