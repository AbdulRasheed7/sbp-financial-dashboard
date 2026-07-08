import pandas as pd
import oracledb
import numpy as np
import re

# Load CSV
df = pd.read_csv("financial_data.csv")
print("📂 CSV loaded successfully.")

# Clean column names
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Detect year columns dynamically
year_cols = sorted([col for col in df.columns if re.fullmatch(r"\d{4}", col)], key=int)
print("📅 Year columns detected in CSV:", ', '.join(year_cols))

# Clean numeric year columns (remove commas, convert to float, handle nulls)
for col in year_cols:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace(["", "-", "—", "–", "nan", "N/A", " - "], np.nan)
        .apply(lambda x: float(x) if pd.notnull(x) and x != "" else None)
    )

print("🧹 Numeric columns cleaned.")

# Oracle connection
dsn = "localhost/XEPDB1"
username = "system"
password = "123456"

conn = oracledb.connect(user=username, password=password, dsn=dsn)
cursor = conn.cursor()
print("🔌 Connected to Oracle XE.")

# Drop if exists (optional)
try:
    cursor.execute("DROP TABLE financial_data")
    print("⚠ Existing table dropped.")
except Exception:
    print("ℹ No existing table found to drop.")

# Create table dynamically
table_cols = ',\n    '.join([f'"{y}" NUMBER' for y in year_cols])
create_stmt = f"""
CREATE TABLE financial_data (
    org_name VARCHAR2(100),
    item_name VARCHAR2(255),
    {table_cols}
)
"""
cursor.execute(create_stmt)
print("✅ New table created with columns:", ', '.join(['org_name', 'item_name'] + year_cols))

# Prepare insert statement dynamically
insert_cols = ', '.join(['org_name', 'item_name'] + [f'"{y}"' for y in year_cols])
placeholders = ', '.join([f':{i+1}' for i in range(2 + len(year_cols))])
insert_stmt = f"""
INSERT INTO financial_data ({insert_cols})
VALUES ({placeholders})
"""

# Insert data row by row
for _, row in df.iterrows():
    values = [row['org_name'], row['item_name']] + [
        float(row[y]) if pd.notnull(row[y]) and row[y] != "" else None
        for y in year_cols
    ]
    try:
        cursor.execute(insert_stmt, values)
    except Exception as e:
        print("❌ Failed row:", row.tolist())
        print("⚠ Error:", e)

print(f"📤 Uploaded {len(df)} rows to financial_data.")


conn.commit()
cursor.close()
conn.close()
print("✅ Upload complete. Oracle connection closed.")