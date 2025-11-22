import pandas as pd
import os

file_path = r"C:\Users\nilad\Documents\country-dataset\pakistan\IBQ\Pakistan_IBQ.xlsx"
xls = pd.ExcelFile(file_path)

target_col = "جواب"

print(f"Checking for missing '{target_col}' column in {file_path}...")
for sheet in xls.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)
    if target_col not in df.columns:
        print(f"\n[MISSING] Sheet: {sheet}")
        print(f"Columns found: {list(df.columns)}")
    else:
        # print(f"[OK] Sheet: {sheet}")
        pass
