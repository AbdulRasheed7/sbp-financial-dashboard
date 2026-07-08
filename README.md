# 🏦 Institutional Financial Analytics Dashboard — State Bank of Pakistan

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Oracle](https://img.shields.io/badge/Oracle_XE-F80000?style=for-the-badge&logo=oracle&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

> **Built during my internship at the State Bank of Pakistan — Statistics & Data Services Department (SDSD), Summer 2025.**

---

## 📌 Project Overview

The State Bank of Pakistan's SDSD previously relied on manual, Excel-based workflows to analyze financial performance data across Pakistan's regulated institutions. This project replaces that with a **fully interactive, SBP-branded Streamlit dashboard** backed by a locally hosted **Oracle XE database** — enabling real-time filtering, dynamic charting, and instant KPI calculation.

---

## 🎯 Problem Statement

- No dedicated interactive tool for multi-year institutional financial analysis
- Manual Excel reviews were time-consuming and hard to scale
- No side-by-side comparisons or automated ratio calculations across institution types

---

## ✅ What I Built

A **two-page Streamlit web application** that:

- Connects live to an **Oracle XE** local database
- Ingests and cleans financial data from CSV via automated Python-Pandas pipeline
- Covers **5 years (2019–2023)** of data across **8 institution types**:
  Banks · DFIs · MFBs · Leasing Companies · Exchange Companies · Insurance · Modarabas · Investment Banks
- Renders dynamic **KPI tiles**: ROA, ROE, Equity/Asset Ratio
- Displays **waterfall charts** for profit/loss breakdown (Banks, DFIs, MFBs)
- Shows **multi-year trend line charts** for Assets, Liabilities, Equity, and Profit
- Includes an **Excel export button** for filtered data
- Fully branded with SBP colors, logo, and typography

---

## 🗂️ Pages

### Page 1 — Main Dashboard
- Institution + Year dropdowns (auto-populated from Oracle)
- Assets / Liabilities / Equity bar chart
- Profit/Loss waterfall or horizontal bar chart (adaptive by institution type)
- KPI tiles: ROA · ROE · Equity/Asset Ratio
- Download Full Dataset as Excel

### Page 2 — Yearly Comparison
- Institution selector
- Line chart: Assets, Liabilities, Equity trend (2019–2023)
- Line chart: Revenue, Expenses, Profit After Tax trend

---

## ⚙️ Tech Stack

| Component | Technology |
|---|---|
| Frontend / UI | Streamlit |
| Visualizations | Plotly |
| Backend Database | Oracle XE (local) |
| Data Ingestion | Python + Pandas |
| Computation | NumPy, Regex |
| Data Format | CSV → Oracle Table |

---

## 🧠 Key Engineering Features

- **Dynamic schema detection** — uses regex `\d{4}` to identify year columns; zero code changes needed when new years are added
- **Regex-based metric mapping** — normalizes inconsistent metric names across institution types (e.g., `markup.*earned` → "Gross Revenue")
- **NULL-safe ratio calculation** — ROA/ROE/Equity-Asset ratios display "N/A" if any component is missing
- **Automated ingestion pipeline** — drops and rebuilds Oracle table on each CSV upload to enforce schema consistency

---

## 📁 File Structure

```
📁 sbp-financial-dashboard/
├── dashboard.py              # Main Streamlit application
├── upload_to_oracle.py       # CSV ingestion & Oracle upload script
├── financial_data.csv        # Source data (sample/anonymized)
├── sbp_logo.png              # SBP branding asset
└── README.md
```

---

## 🚀 How to Run Locally

**Prerequisites:**
- Python 3.10+
- Oracle XE installed and running locally
- pip packages: `streamlit pandas numpy oracledb plotly`

```bash
# 1. Install dependencies
pip install streamlit pandas numpy oracledb plotly

# 2. Upload data to Oracle
python upload_to_oracle.py

# 3. Launch dashboard
streamlit run dashboard.py
# Opens at http://localhost:8501
```

---

## 📸 Screenshots

> *(Add screenshots of your dashboard here — drag and drop images into the GitHub repo)*

| Main Dashboard | Yearly Comparison |
|---|---|
| ![Main](screenshots/main.png) | ![Trend](screenshots/trend.png) |

---

## 👤 Author

**Abdul Rasheed** — Intern, SDSD, State Bank of Pakistan (SIP 2025)

Supervised by: Ms. Humaira Kiran (Deputy Director, SDSD)
Mentored by: Dr. Abdul Basit (Joint Director, SDSD)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/abdul-rasheed-551814244)
[![Email](https://img.shields.io/badge/Email-D14836?style=flat&logo=gmail&logoColor=white)](mailto:sheikhabdulrasheed2003@gmail.com)
