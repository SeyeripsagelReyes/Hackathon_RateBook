import pandas as pd
import numpy as np

def process_excel_file(uploaded_file):
    """
    Reads an Excel file and returns a dictionary:
    {sheet_name: cleaned_dataframe}
    """
    xls = pd.ExcelFile(uploaded_file)
    sheets = {}

    for sheet_name in xls.sheet_names:
        df_raw = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=None)

        # Detect header row
        header_row = None
        for i in range(len(df_raw)):
            if df_raw.iloc[i].notna().sum() >= 2:
                header_row = i
                break

        if header_row is None:
            continue  # skip sheets without valid header

        df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=header_row)
        df = df.dropna(how="all", axis=1)
        df = df.replace(r'^\s*$', np.nan, regex=True)

        empty_rows = [i for i, row in df.iterrows() if all(pd.isna(row))]
        if empty_rows:
            df = df.loc[:empty_rows[0] - 1]

        unnamed_cols = [c for c in df.columns if str(c).startswith("Unnamed")]
        if unnamed_cols:
            cutoff_idx = df.columns.get_loc(unnamed_cols[0])
            df = df.iloc[:, :cutoff_idx]

        df = df.dropna(how="all", axis=0)

        sheets[sheet_name] = df

    return sheets
