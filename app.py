import streamlit as st
import pandas as pd
import numpy as np

# Set Streamlit page to use the full width
st.set_page_config(layout="wide")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file:
    # Read all sheet names
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    for sheet_name in sheet_names:
        st.subheader(f"{sheet_name}")
        df_raw = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=None)

        # Detect header row
        header_row = None
        for i in range(len(df_raw)):
            if df_raw.iloc[i].notna().sum() >= 2:
                header_row = i
                break

        if header_row is None:
            st.warning(f"No valid header row detected in sheet '{sheet_name}'.")
            continue

        df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=header_row)
        df = df.dropna(how="all", axis=1)  # Drop fully empty columns

        # Replace empty strings or whitespace-only cells with NaN
        df = df.replace(r'^\s*$', np.nan, regex=True)

        # Find first empty row robustly
        empty_rows = [i for i, row in df.iterrows() if all(pd.isna(row))]

        if empty_rows:
            df = df.loc[:empty_rows[0] - 1]

        # Stop at first "Unnamed" column if exists
        unnamed_cols = [c for c in df.columns if str(c).startswith("Unnamed")]
        if unnamed_cols:
            first_unnamed = unnamed_cols[0]
            cutoff_idx = df.columns.get_loc(first_unnamed)
            df = df.iloc[:, :cutoff_idx]

        # SECOND CLEANING PASS: remove any rows that are now fully NaN
        df = df.dropna(how="all", axis=0)

        # Create wide layout columns — more space for table
        col1, col2 = st.columns([6, 1], gap="large")

        with col1:
            st.dataframe(df, use_container_width=True)

        with col2:
            st.markdown(
                f"""
                <div style="
                    background-color: #0e1117;
                    padding: 15px 20px;
                    border-radius: 8px;
                    text-align: center;
                    border: 1px solid #ddd;
                    margin-top: 20px;
                ">
                    <h4 style="margin: 0;">📊 Summary</h4>
                    <p style="margin: 8px 0 0 0;"><b>Rows:</b> {len(df)}</p>
                    <p style="margin: 4px 0 0 0;"><b>Columns:</b> {len(df.columns)}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
