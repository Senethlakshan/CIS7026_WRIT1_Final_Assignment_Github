# CIS7026 — Business Process and Data Analysis

## Project: Q3C / Q3D — Process Mining Implementation

Overview
- This project contains analysis code and visualizations for the BPI Challenge 2017 event log used in the CIS7026 assignment. It implements classical process mining analyses (activity frequencies, directly-follows graphs, conformance checking) and an object-centric perspective (OCPM) variant.

Author & Date
- Author: Seneth
- Date: 29-03-2026

Repository structure
- Py Project/CIS7026_WRIT1_Final_Assignment_Github/
  - `q3c_main_analysis.py` — main analysis script (classical + conformance + plots).
  - `q3d_ocpm.py` — object-centric process mining analysis and plots.
  - `dataset/` — contains `BPI Challenge 2017.csv` (event log used by the scripts).
  - `outputs/` — generated figures and outputs saved by the scripts.

Dataset
- The event log CSV is located at `Py Project/CIS7026_WRIT1_Final_Assignment_Github/dataset/BPI Challenge 2017.csv`.
- Please ensure the CSV remains at that path when running the scripts.

Requirements
- Python 3.9+ recommended.
- Main Python packages used:
  - `pandas`
  - `numpy`
  - `matplotlib`
  - `seaborn` (optional)

Install dependencies (example):

```bash
python -m pip install pandas numpy matplotlib seaborn
```

Usage
1. From the repository root run the main analysis script:

```bash
python "Py Project/CIS7026_WRIT1_Final_Assignment_Github/q3c_main_analysis.py"
```

2. To run the object-centric analysis:

```bash
python "Py Project/CIS7026_WRIT1_Final_Assignment_Github/q3d_ocpm.py"
```

Outputs
- Figures and saved plots are written to `Py Project/CIS7026_WRIT1_Final_Assignment_Github/outputs/` by default.
- Inspect that directory after running the scripts to review generated charts (DFG frequency, conformance pie chart, OCPM visualizations, etc.).

Notes & Tips
- If you move or rename the dataset file, update the path in the scripts accordingly (search for `pd.read_csv("dataset/BPI Challenge 2017.csv")`).
- The scripts use simple, self-contained plotting and file-save calls (no external plotting server required).

Contact
- If you need edits to the README (add example outputs, more run options, or a `requirements.txt`), tell me what to include and I will update it.
