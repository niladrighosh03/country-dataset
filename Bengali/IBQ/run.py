# %%
import pandas as pd
import glob
import os
import time
from dotenv import load_dotenv
import os
import requests
import json
import base64  # <-- NEW: For image encoding
import mimetypes # <-- NEW: For image encoding
mimetypes.add_type("image/webp", ".webp")

# %%

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")

# %%

# =============================
# NEW: Image Encoding Function
# =============================
def encode_image_to_base64(image_path):
    """Encodes a local image file into a Base64 data URI."""
    
    # Guess the MIME type (e.g., 'image/jpeg' or 'image/png')
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type or not mime_type.startswith('image'):
        raise ValueError(f"Could not determine image type for {image_path}")

    # Read the image file in binary mode
    with open(image_path, "rb") as image_file:
        binary_data = image_file.read()
    
    # Encode the binary data to Base64
    base64_encoded_data = base64.b64encode(binary_data)
    
    # Decode to a string
    base64_string = base64_encoded_data.decode('utf-8')
    
    # Format as a data URI
    return f"data:{mime_type};base64,{base64_string}"

# =============================
# MODIFIED: LLM PROMPT FUNCTION
# =============================
url = 'https://cloud.olakrutrim.com/v1/chat/completions'


def ask_llm(question, options, answer, image_path):
    """
    Asks the multimodal LLM to evaluate an MCQ, optionally with an image.
    """
    
    # --- 1. Update prompt to handle image context ---
    prompt = f"""
You are a dataset quality checker for multiple-choice sports MCQs.
**An image may be provided as context. Use this image to evaluate the question and answer.**

Question: {question}
Options: {options}
Correct Answer: {answer}

Evaluate the MCQ on the following:
1. Is the question factually and logically correct (considering the image if provided)?
2. Is the provided answer correct (considering the image if provided)?
3. Does the question make sense as a valid MCQ?
4. Update the Question with the minimal chnages in same languague of the given question.
5. Update the Options with the minimal chnages in same languague of the given question.
6. Give the correct answer of the updated Question among the Options in the same language of the given question.

Note:  ( 0 means error 1 means correct)

Respond ONLY in JSON format (strictly):
{{
  "score": 1 or 0,
  "mistake": "Describe the issue, or 'no mistake' if everything is correct",
  "improved_question": "If score = 1, respond 'no correction needed'. If score = 0, update the question with minimal changes in same language of the given question",
  "improved_options": "If score = 1, respond 'no correction needed'. If score = 0, provide corrected options list",
  "correct_answer": "If score = 1, respond 'no answer needed'. If score = 0, provide the correct answer from the improved options in same language of the given question"
}}
"""

    # --- 2. Set model and headers ---
    model = "Gemma-3-27B-IT"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    # --- 3. Build multimodal content ---
    message_content = [
        {
            "type": "text",
            "text": prompt
        }
    ]

    if image_path:
        try:
            encoded_image = encode_image_to_base64(image_path)
            message_content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": encoded_image
                    }
                }
            )
        except Exception as e:
            print(f"Warning: Could not encode image {image_path}. {e}. Proceeding without it.")

    # --- 4. Build final payload ---
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": message_content}],
        "stream": False
    }

    # --- 5. Make API call and parse response ---
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    result = response.json()
    content = result["choices"][0]["message"]["content"]

    # --- THIS IS THE FIX ---
    # Clean the content string to remove Markdown
    if content.startswith("```json"):
        content = content[7:]  # Remove ```json
    if content.startswith("```"):
        content = content[3:]  # Remove ```
    if content.endswith("```"):
        content = content[:-3] # Remove ```
    content = content.strip() # Remove any leading/trailing whitespace
    # --- END OF FIX ---

    # Parse JSON returned by model
    try:
        data = json.loads(content)
        return (
            data.get("score"),
            data.get("mistake"),
            data.get("improved_question"),
            data.get("improved_options"),
            data.get("correct_answer"),
        )
    except json.JSONDecodeError:
        print("Failed to decode JSON from model:", content) # Now this log will show the *cleaned* content
        return None, None, None, None, None

# %%
# =============================
# CONFIGURATION
# =============================
base_path = r"C:\Users\nilad\Documents\country-dataset\Bengali\IBQ"
output_file = r"Results_IBQ.csv"
output_excel = r"Results_IBQ.xlsx"

# ✅ NEW: Define the base images directory
image_base_dir = os.path.join(base_path, r"images_bangladesh")

# ✅ Regional language column mapping (update if needed)
COL_QUESTION = "প্রশ্ন"
COL_OPTIONS  = "বিকল্প"
COL_ANSWER   = "সঠিক বিকল্প"
COL_IMAGE_NO = "ছবি" # <-- NEW: Column name for the image file
# %%
# ✅ If output file doesn’t exist → write header
import csv
if not os.path.exists(output_file):
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["image_no", "country", "file", "sheet",
                         "question", "option", "answer", "score",
                         "What's wrong in Question", "How can I improve the question", "How can I improve the Options", "Correct Answer"])

# ✅ Load already processed rows (to skip on restart)
processed = set()
df_existing = pd.read_csv(output_file, encoding="utf-8-sig")
for i, row in df_existing.iterrows():
    processed.add((row["file"], row["sheet"], row["question"]))


# %%
# =============================
# MODIFIED: MAIN PROCESS
# =============================
from datetime import datetime

start_time = datetime.now()
print("Started at:", start_time.strftime("%H:%M:%S"))

excel_files = glob.glob(os.path.join(base_path, "**/*.xlsx"), recursive=True)
print(excel_files)
for file in excel_files:
        
    country = os.path.basename(os.path.dirname(file))
    xls = pd.ExcelFile(file)
    print(f"\n-> Processing: {file}")

    for sheet in xls.sheet_names:
        df = pd.read_excel(file, sheet_name=sheet)

        if COL_QUESTION not in df.columns:
            continue

        '''skip the Boli khela sheet'''
        if sheet == "Boli Khela":
            continue
            
        if COL_IMAGE_NO not in df.columns:
            print(f"Warning: Column '{COL_IMAGE_NO}' not found in sheet '{sheet}'. Will proceed without images.")

        for idx, row in df.iterrows():
            key = (os.path.basename(file), sheet, row[COL_QUESTION])

            if key in processed:
                continue

            # Handle alternative column names
            ans_col = COL_ANSWER if COL_ANSWER in df.columns else COL_ANSWER_ALT
            
            if ans_col not in df.columns:
                print(f"[ERROR] Answer column not found in {sheet}. Skipping row {idx}.")
                continue

            q, option, ans = row[COL_QUESTION], row[COL_OPTIONS], row[ans_col]
            
            # --- MODIFIED: Image Path Logic ---
            image_path = None
            image_name_to_save = None  # <-- Initialize variable to save
            
            if COL_IMAGE_NO in df.columns:
                image_name_base = row.get(COL_IMAGE_NO)
                
                if pd.notna(image_name_base):
                    image_name_base = str(image_name_base).strip()
                    image_name_to_save = image_name_base # <-- This is the value we'll save
                    image_folder = os.path.join(image_base_dir, sheet)
                    
                    image_files_found = glob.glob(os.path.join(image_folder, f"{image_name_base}.*")) #with extension
                    
                    if image_files_found:
                        image_path = image_files_found[0] 
                    else:
                        print(f"Warning: Image '{image_name_base}' not found in {image_folder} for row {idx}")
            # --- End Image Path Logic ---

            try:
                score, mistake, improved_question, improved_options, correct_answer = ask_llm(q, option, ans, image_path)
                
            except Exception as e:
                print(f"[ERROR] Error on row {idx}: {e}") 
                score = 0
                mistake = f"ERROR: {e}"
                improved_question = "ERROR"
                improved_options = "ERROR"
                correct_answer = "ERROR"

            # ✅ WRITE IMMEDIATELY to CSV (MODIFIED)
            # ✅ WRITE IMMEDIATELY to CSV (FIXED)
            with open(output_file, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow([image_name_to_save, country, os.path.basename(file), sheet,
                                 q, option, ans, score, mistake, improved_question, improved_options, correct_answer])

            processed.add(key)

            print(f"[SAVED] -> {country} | {sheet} | Row {idx}")
            time.sleep(0.3) 

print("\n[COMPLETE]!")
print("Live-updating CSV:", output_file)


end_time = datetime.now()
print("Ended at:", end_time.strftime("%H:%M:%S"))
print("Total Duration:", end_time - start_time)


# %%
'''Convert CSV to Excel with separate sheets'''

# This section is ALREADY CORRECT. 
# It will read the new "image_no" column from the CSV
# and automatically include it in the final Excel file.

# Read the CSV file
df = pd.read_csv(output_file) # Use output_file

# Columns to remove
columns_to_remove = ["country", "file"] # Keep 'sheet' for grouping

# Create Excel writer
with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
    # Group by the 'sheet' column
    for sheet_name, sheet_data in df.groupby("sheet"):
        # Drop unnecessary columns (this leaves "image_no" and the others)
        sheet_data = sheet_data.drop(columns=columns_to_remove + ["sheet"], errors="ignore")
        
        # Write each sheet to the Excel file
        sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"[SUCCESS] Successfully created '{output_excel}'")