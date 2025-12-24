import pandas as pd
import os

# Configuration
input_file = "Bangladesh_IBQ.xlsx"
output_file = "Bangladesh_IBQ_Combined.xlsx"

# Read the Excel file
xls = pd.ExcelFile(input_file)

# Create Excel writer for output
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    # Process each sheet
    for sheet_name in xls.sheet_names:
        print(f"Processing sheet: {sheet_name}")
        
        # Read the sheet
        df = pd.read_excel(input_file, sheet_name=sheet_name)
        
        # Check if the option columns exist
        option_columns = ['বিকল্প ১', 'বিকল্প ২', 'বিকল্প ৩', 'বিকল্প ৪']
        
        if all(col in df.columns for col in option_columns):
            # Combine the 4 option columns into one
            # Format: A) option1, B) option2, C) option3, D) option4
            labels = ['A)', 'B)', 'C)', 'D)']
            df['বিকল্প'] = df.apply(
                lambda row: ', '.join([
                    f"{labels[i]} {str(row[col])}" 
                    for i, col in enumerate(option_columns) 
                    if pd.notna(row[col]) and str(row[col]).strip() != ''
                ]),
                axis=1
            )
            
            # Drop the original 4 option columns
            df = df.drop(columns=option_columns)
            
            print(f"  - Combined {len(option_columns)} option columns into 'বিকল্প'")
        else:
            print(f"  - Warning: Not all option columns found in sheet '{sheet_name}'. Skipping combination.")
        
        # Write to the new Excel file
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"\n[SUCCESS] Created new file: {output_file}")
print(f"The 4 option columns have been combined into one column called 'বিকল্প'")
