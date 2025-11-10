Country-Specific Question Bank Processor 🌍

1. Overview 🚀

This project processes and refines question banks (QBs) for various countries. A Python script (run.py) scores questions (0/1), provides corrections, and generates a final, filtered file with the updated questions.

2. Folder Structure 📂

The project is organized by country, with each country containing subfolders for different question types.

/
├── Bengali/
│   ├── HBQ/
│   │   ├── Bangladesh_HBQ.xlsx
│   │   ├── Filtered_Results_HBQ.xlsx
│   │   ├── output.log
│   │   ├── Results_HBQ.csv
│   │   ├── Results_HBQ.xlsx
│   │   └── run.py
│   │
│   ├── SBQ/
│   │   ├── Bangladesh_SBQ.xlsx
│   │   ├── Filtered_Results_SBQ.xlsx
│   │   ├── output.log
│   │   ├── Results_SBQ.csv
│   │   ├── Results_SBQ.xlsx
│   │   └── run.py
│   │
│   └── RBQ/
│       ├── Bangladesh_RBQ.xlsx
│       ├── Filtered_Results_RBQ.xlsx
│       ├── output.log
│       ├── Results_RBQ.csv
│       ├── Results_RBQ.xlsx
│       └── run.py
│
├── china/
│   ├── HBQ/
│   ├── SBQ/
│   └── RBQ/
├── indonesia/
│   ├── ...
└── ...


3. Workflow & Files 🛠️

Each subfolder (e.g., Bengali/SBQ/) contains:

run.py 🏃‍♂️

Purpose: The main script that runs the entire process.

Function: Reads the input file, applies a processing prompt, and generates the output files.

Bangladesh_SBQ.xlsx 📥

Purpose: The input file.

Contains: The raw dataset of questions that need to be processed.

Results_SBQ.xlsx 📈

Purpose: The raw output file from run.py.

Contains: The original data plus new columns: Score, Correct Question, Correct Options, Correct Answer, and Explanation.

Filtered_Results_SBQ.xlsx ✅

Purpose: The final, cleaned output file.

Contains: A filtered, ready-to-use file containing the updated questions.

output.log 📋

Purpose: A log file that captures console output for tracking progress and debugging.

4. How to Run ⚡

Navigate to the directory:

cd Bengali/SBQ/


Ensure required packages (e.g., pandas, openpyxl) are installed.

Execute the script:

python run.py


Check the Filtered_Results_SBQ.xlsx for the final results!