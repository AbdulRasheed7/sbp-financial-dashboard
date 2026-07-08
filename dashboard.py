import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import oracledb
import numpy as np

# --- SBP Theme Settings ---
SBP_GREEN = "#005634"  # SBP official dark green
TITLE_FONT_SIZE = "30px"
HEADER_FONT_SIZE = "22px"
TEXT_FONT_SIZE = "16px"

# Big, bold title — SBP-themed color and large font
st.markdown(
    "<h1 style='font-size:60px; color:#007A3D; font-weight:800; margin: 0px;'>SBP Financial Sector Dashboard</h1>",
    unsafe_allow_html=True
)

st.set_page_config(
    page_title="SBP Financial Sector Dashboard",
    page_icon="🟢",  # OR use a custom image if hosted
    layout="wide"
)

st.markdown("""
    <style>
        .main {
            background-color: #F5F9F6;
        }
    </style>
""", unsafe_allow_html=True)

from PIL import Image

# Load SBP Logo
sbp_logo = Image.open("state-bank-of-pakistan-seeklogo.png")

import base64

def get_image_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return encoded

# --- Required Lists (must be defined before usage) ---

institutions = ['Banks', 'DFIs', 'MFBs', 'Leasing', 'Investment Banks', 'Modarba', 'Exchange Companies', 'Insurance']

username = "system"
password = "123456"  # your actual password
dsn = "localhost/XEPDB1"

# Load data from Oracle
query = "SELECT * FROM financial_data"

connection = None
try:
    connection = oracledb.connect(user=username, password=password, dsn=dsn)
    df_main = pd.read_sql(query, con=connection)
finally:
    if connection is not None:
        connection.close()

import re
year_cols = sorted(
    [col for col in df_main.columns if re.fullmatch(r"\d{4}", col)],
    key=int
)

import io

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

# Rename columns to expected format
df_main.rename(columns={
    df_main.columns[0]: "Org Name",
    df_main.columns[1]: "Item Name"
}, inplace=True)
df_main[year_cols] = df_main[year_cols].apply(pd.to_numeric, errors='coerce')

institution_map = {
    'Banks': 'All Banks',
    'DFIs': 'All DFIs',
    'MFBs': 'All Microfinance Banks',
    'Leasing': 'All Leasing Companies',
    'Investment Banks': 'All Invesment Banks',
    'Modarba': 'All Modaraba Companies',
    'Exchange Companies': 'All Exchange Companies',
    'Insurance': 'All Insurance Companies'
}

# Top of the script — shared patterns for all graphs
metric_patterns = {
    'Profit After Tax': [r'profit.*after.*tax'],
    'Profit Before Tax': [r'profit.*before.*tax'],
    'Gross Revenue': [
        r'markup.*interest.*earned',  # for Banks, DFIs, MFBs
        r'gross.*premium',            # for Insurance
        r'total.*revenue',            # for Leasing
        r'\brevenue\b',                 # for Exchange Companies
        r'gross.*revenue',            # generic
        r'income.*lease',             # fallback
    ],
    'Administrative Expenses': [
        r'admin.*expense',
        r'operating.*expense',        # used by Modarabas
    ]
}

# Sidebar header
st.sidebar.markdown(
    "<h2 style='color:#007A3D; font-family:Arial;'>📊 SBP Dashboard</h2>",
    unsafe_allow_html=True
)

# Styled label for page selector
st.sidebar.markdown(
    "<p style='font-size:18px; color:#007A3D; font-family:Arial; margin-bottom:-10px;'><strong>Select a page:</strong></p>",
    unsafe_allow_html=True
)
page = st.sidebar.radio("", ["🏠 Main Dashboard", "📅 Yearly Comparison"])

with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)

    # ✅ Hyperlinked local SBP logo
    img_base64 = get_image_as_base64("state-bank-of-pakistan-seeklogo.png")
    st.markdown(
        f"""
        <a href="https://www.sbp.org.pk" target="_blank">
            <img src="data:image/png;base64,{img_base64}" width="200">
        </a>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ✅ Download full Oracle table
    excel_data = to_excel(df_main)
    st.download_button(
        label="📥 Download Full Dataset (Excel)",
        data=excel_data,
        file_name="SBP_Financial_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


    # --- Helper Functions ---
    def fmt_ratio(val):
        return f"{val:.1%}" if val is not None and pd.notna(val) else "N/A"


    def scale_amount(val):
        if abs(val) >= 1e9:
            return round(val / 1e9, 1), "T"
        elif abs(val) >= 1e6:
            return round(val / 1e6, 1), "B"
        elif abs(val) >= 1e3:
            return round(val / 1e3, 1), "M"
        else:
            return round(val, 1), "K"


    # --- Main Dashboard Page ---
if page == "🏠 Main Dashboard":
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<p style='font-size:18px; color:#007A3D; font-weight:bold; margin-bottom:-20px;'>🏦 Select Institution:</p>",
                unsafe_allow_html=True)

    selected_institution = st.selectbox("", institutions)

    st.markdown("<p style='font-size:18px; color:#007A3D; font-weight:bold; margin-bottom:-20px;'>📅 Select Year:</p>",
                unsafe_allow_html=True)
    selected_year = st.selectbox("", year_cols, index=year_cols.index("2023"))
    target_org = institution_map.get(selected_institution)

    st.markdown("<div style='padding-top: 40px;'></div>", unsafe_allow_html=True)

    df_inst = df_main[df_main['Org Name'] == target_org].copy()

    if not df_inst.empty:
            # --- Bar Chart: Assets, Liabilities, Equity ---
        df_bar = df_inst[df_inst['Item Name'].str.contains("Total", case=False)].copy()


        def map_category(name):
            name = name.lower()
            if "asset" in name:
                return "Assets"
            elif "liabilit" in name:
                return "Liabilities"
            elif "equity" in name:
                return "Equity"
            return None


        df_bar['Category'] = df_bar['Item Name'].apply(map_category)
        df_bar = df_bar.dropna(subset=['Category'])
        df_long = df_bar.melt(id_vars=["Category"], value_vars=year_cols, var_name="Year", value_name="Amount")

        scale_divisor = 1e9 if selected_institution in ['Banks', 'DFIs', 'Insurance'] else 1e6
        scale_suffix = 'T' if scale_divisor == 1e9 else 'B'

        df_long['Amount_Scaled'] = df_long['Amount'] / scale_divisor
        df_long['Label'] = df_long['Amount_Scaled'].apply(lambda x: f"{x:.1f}{scale_suffix}")
        filtered = df_long[df_long["Year"] == selected_year].groupby("Category", as_index=False).first()

        fig_bar = go.Figure()
        color_map = {"Assets": "#1f77b4", "Liabilities": "#ff7f0e", "Equity": "#2ca02c"}
        for _, row in filtered.iterrows():
            fig_bar.add_trace(go.Bar(
                x=[row["Category"]],
                y=[row["Amount_Scaled"]],
                text=[row["Label"]],
                textposition="outside",
                textfont=dict(size=16),
                marker_color={"Assets": "#1f77b4", "Liabilities": "#ff7f0e", "Equity": "#2ca02c"}[row["Category"]]
            ))

        fig_bar.update_layout(
            title={
                'text': f"Assets, Liabilities, Equity - {selected_year} ({target_org})",
                'font': {
                    'size': 24,
                    'color': '#007A3D',
                    'family': 'Arial'
                }
            },
            yaxis={  # 👈 replaces yaxis_title
                'title': f"Amount (Rs. in {scale_suffix})",
                'range': [0, max(filtered["Amount_Scaled"]) * 1.2]
            },
            showlegend=False,
            height=400,
            margin=dict(t=80, b=20)
        )

        st.plotly_chart(fig_bar, use_container_width=True)

            # --- Financial Ratios ---
        total_assets = df_inst[df_inst['Item Name'].str.lower().str.contains("total.*assets", na=False)][
            selected_year].values
        total_equity = df_inst[df_inst['Item Name'].str.lower().str.contains("total.*equity", na=False)][
            selected_year].values
        profit_after_tax = \
        df_inst[df_inst['Item Name'].str.lower().str.contains("profit.*after.*taxation", na=False)][
            selected_year].values

        ta = float(total_assets[0]) if len(total_assets) > 0 else None
        te = float(total_equity[0]) if len(total_equity) > 0 else None
        pat = float(profit_after_tax[0]) if len(profit_after_tax) > 0 else None

        roa = pat / ta if pat and ta else None
        roe = pat / te if pat and te else None
        equity_assets_ratio = te / ta if te and ta else None

        st.markdown("<h3 style='font-size:28px; color:#007A3D; font-family:Arial;'>📊 Key Financial Ratios</h3>",
                    unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        # 🏦 ROA: Measures asset efficiency
        col1.markdown(
            "<h4 style='font-size:20px; color:#007A3D; font-weight:bold; font-family:Arial;'>💼 Return on Assets (ROA)</h4>",
            unsafe_allow_html=True)
        col1.markdown(
            f"<p style='font-size:18px; color:#007A3D; font-weight:bold; font-family:Arial;'>{fmt_ratio(roa)}</p>",
            unsafe_allow_html=True)

        # 📈 ROE: Measures shareholder return
        col2.markdown(
            "<h4 style='font-size:20px; color:#007A3D; font-weight:bold; font-family:Arial;'>📈 Return on Equity (ROE)</h4>",
            unsafe_allow_html=True)
        col2.markdown(
            f"<p style='font-size:18px; color:#007A3D; font-weight:bold; font-family:Arial;'>{fmt_ratio(roe)}</p>",
            unsafe_allow_html=True)

        # 🧮 Equity/Assets Ratio: Measures leverage
        col3.markdown(
            "<h4 style='font-size:20px; color:#007A3D; font-weight:bold; font-family:Arial;'>🧮 Equity/Assets Ratio</h4>",
            unsafe_allow_html=True)
        col3.markdown(
            f"<p style='font-size:18px; color:#007A3D; font-weight:bold; font-family:Arial;'>{fmt_ratio(equity_assets_ratio)}</p>",
            unsafe_allow_html=True)

        st.markdown("---")

    # === Waterfall or Horizontal Bar Chart Section ===

    if selected_institution in ['Banks', 'DFIs', 'MFBs']:
        df_water = df_main.copy()
        df_water.columns = df_water.columns.astype(str)
        df_water.rename(columns={df_water.columns[0]: "Org Name", df_water.columns[1]: "Item"}, inplace=True)

        year_data = df_water[df_water['Org Name'] == target_org][['Item', selected_year]].set_index('Item')[
            selected_year].to_dict()
        profit_before = year_data.get('9. Profit/(loss) before taxation', 0)
        profit_after = year_data.get('10. Profit/(loss) after taxation', 0)
        taxation = profit_before - profit_after

        # Choose scale and label
        if selected_institution == "Banks":
            scale_divisor = 1e9
            y_label = "Rs. (Trillions)"
        else:  # DFIs, MFBs
            scale_divisor = 1e6
            y_label = "Rs. (Billions)"

        steps = [
            {'label': 'Markup earned', 'value': year_data.get('1. Markup/interest earned', 0), 'type': 'relative'},
            {'label': 'Non-markup income', 'value': year_data.get('6. Non-markup/interest income', 0),
             'type': 'relative'},
            {'label': 'Markup expenses', 'value': -year_data.get('2. Markup/interest expenses', 0), 'type': 'relative'},
            {'label': 'Provisions', 'value': -year_data.get('4. Provisions and write-offs', 0), 'type': 'relative'},
            {'label': 'Non-markup expenses', 'value': -year_data.get('7. Non-markup/interest expenses', 0),
             'type': 'relative'},
            {'label': 'Admin expenses', 'value': -year_data.get('8. Administrative expenses', 0), 'type': 'relative'},
            {'label': 'Taxation', 'value': -taxation, 'type': 'relative'},
            {
                'label': 'Profit after tax',
                'value': profit_after,
                'type': 'total',
                'color': '#0057B7' if profit_after >= 0 else 'red'  # 👈 Blue if positive, red if negative
            }
        ]

        fig_wf = go.Figure(go.Waterfall(
            x=[s['label'] for s in steps],
            y=[s['value'] / scale_divisor for s in steps],
            measure=[s['type'] for s in steps],
            text=[
                f"{(abs(s['value']) / scale_divisor):.1f}{'T' if scale_divisor == 1e9 else 'B'}"
                for s in steps
            ],
            connector={"line": {"color": "gray"}},
            increasing={"marker": {"color": "#007A3D"}},  # ✅ SBP green
            decreasing={"marker": {"color": "#D97904"}},  # ✅ muted orange
            totals={"marker": {"color": [s.get('color', 'black') for s in steps if s['type'] == 'total'][0]}}
            # ✅ PAT color override
        ))

        fig_wf.update_layout(
            title={
                'text': f"Profit/Loss Breakdown - {selected_year} ({target_org})",
                'font': {
                    'size': 28,
                    'color': '#007A3D',
                    'family': 'Arial'
                }
            },
            yaxis_title=y_label,
            height=600,
            margin=dict(t=80, b=40)
        )

        st.plotly_chart(fig_wf, use_container_width=True, key="waterfall_chart")


    elif selected_institution not in ['Banks', 'DFIs', 'MFBs']:
        df_filtered = df_main[df_main['Org Name'] == target_org].copy()
        df_filtered.rename(columns={df_filtered.columns[1]: 'Item Name'}, inplace=True)

        values = {}
        for label, patterns in metric_patterns.items():
            for pattern in patterns:
                mask = df_filtered['Item Name'].str.lower().str.contains(pattern, regex=True, na=False)
                if mask.any():
                    values[label] = df_filtered.loc[mask, selected_year].values[0]
                    break

        order = ['Gross Revenue', 'Administrative Expenses', 'Profit Before Tax', 'Profit After Tax']

        x_vals, bar_labels, y_labels, bar_colors = [], [], [], []
        for k in order:
            if k in values:
                v = values[k]
                y_labels.append(k)

                # Format value
                if abs(v) >= 1e9:
                    x_vals.append(round(v / 1e9, 1))
                    bar_labels.append(f"{round(v / 1e9, 1)}T")
                elif abs(v) >= 1e6:
                    x_vals.append(round(v / 1e6, 1))
                    bar_labels.append(f"{round(v / 1e6, 1)}B")
                elif abs(v) >= 1e3:
                    x_vals.append(round(v / 1e3, 1))
                    bar_labels.append(f"{round(v / 1e3, 1)}M")
                else:
                    x_vals.append(round(v, 1))
                    bar_labels.append(f"{round(v, 1)}K")

                # Assign color
                if k == 'Gross Revenue':
                    bar_colors.append('#007A3D')  # SBP green
                elif k == 'Administrative Expenses':
                    bar_colors.append('#D97904')  # muted orange
                elif k in ['Profit Before Tax', 'Profit After Tax']:
                    bar_colors.append('#0057B7' if v >= 0 else 'red')  # blue if positive, red if negative

        if x_vals:
            fig_h = go.Figure(go.Bar(
                y=list(reversed(y_labels)),
                x=list(reversed(x_vals)),
                orientation='h',
                text=list(reversed(bar_labels)),
                textposition='outside',
                marker_color=list(reversed(bar_colors))  # ✅ Apply custom colors
            ))

            fig_h.update_layout(
                title={
                    'text': f"Key Profit/Loss Items - {selected_year} ({target_org})",
                    'font': {
                        'size': 28,
                        'color': '#007A3D',
                        'family': 'Arial'
                    }
                },
                xaxis_title="Rs.",
                height=400,
                margin=dict(t=40, b=20)
            )

            st.plotly_chart(fig_h, use_container_width=True, key="horizontal_bar_chart")

    else:
        st.info("No data available for selected institution.")

elif page == "📅 Yearly Comparison":

    st.markdown(
        "<p style='font-size:18px; color:#007A3D; font-weight:bold; margin-bottom:-20px;'>🏦 Select Institution:</p>",
        unsafe_allow_html=True)

    selected_institution = st.selectbox("", institutions)
    target_org = institution_map.get(selected_institution)

    st.markdown(
        "<h1 style='font-size:40px; color:#007A3D; font-family:Arial;'>Yearly Comparison</h1>",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    df_yearly = df_main[df_main['Org Name'] == target_org].copy()
    df_yearly.rename(columns={df_yearly.columns[1]: 'Item Name'}, inplace=True)

    asset_row = df_yearly[df_yearly['Item Name'].str.lower().str.contains('total assets', na=False, case=False)]
    liability_row = df_yearly[df_yearly['Item Name'].str.lower().str.contains('total liabilities', na=False, case=False)]
    equity_row = df_yearly[df_yearly['Item Name'].str.lower().str.contains('total equity', na=False, case=False)]

    if not asset_row.empty and not liability_row.empty and not equity_row.empty:
        asset_vals = asset_row.iloc[0, 2:]
        liability_vals = liability_row.iloc[0, 2:]
        equity_vals = equity_row.iloc[0, 2:]

        def format_vals(vals):
            return [
                round(val / 1e9, 1) if val >= 1e9 else
                round(val / 1e6, 1) if val >= 1e6 else
                round(val / 1e3, 1) if val >= 1e3 else
                round(val, 1)
                for val in vals
            ]

        def format_hover(vals):
            return [
                f"{v}T" if val >= 1e9 else
                f"{v}B" if val >= 1e6 else
                f"{v}M" if val >= 1e3 else
                f"{v}"
                for val, v in zip(vals, format_vals(vals))
            ]

        max_val = max(asset_vals.max(), liability_vals.max(), equity_vals.max())
        scale_divisor = 1e9 if max_val >= 1e9 else 1e6 if max_val >= 1e6 else 1e3
        y_unit = "Trillions" if scale_divisor == 1e9 else "Billions" if scale_divisor == 1e6 else "Millions"

        asset_vals_fmt = asset_vals / scale_divisor
        liability_vals_fmt = liability_vals / scale_divisor
        equity_vals_fmt = equity_vals / scale_divisor

        asset_hover = [f"{round(v, 1)}{y_unit[0]}" for v in asset_vals_fmt]
        liability_hover = [f"{round(v, 1)}{y_unit[0]}" for v in liability_vals_fmt]
        equity_hover = [f"{round(v, 1)}{y_unit[0]}" for v in equity_vals_fmt]

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(name='Assets', x=year_cols, y=asset_vals_fmt, mode='lines+markers', line=dict(color='#1f77b4'), text=asset_hover, hovertemplate='%{text}<extra></extra>'))
        fig_line.add_trace(go.Scatter(name='Liabilities', x=year_cols, y=liability_vals_fmt, mode='lines+markers', line=dict(color='#ff7f0e'), text=liability_hover, hovertemplate='%{text}<extra></extra>'))
        fig_line.add_trace(go.Scatter(name='Equity', x=year_cols, y=equity_vals_fmt, mode='lines+markers', line=dict(color='#2ca02c'), text=equity_hover, hovertemplate='%{text}<extra></extra>'))

        max_val = max(asset_vals.max(), liability_vals.max(), equity_vals.max())
        y_unit = "Trillions" if max_val >= 1e9 else "Billions" if max_val >= 1e6 else "Millions"

        fig_line.update_layout(
            title={
                'text': f"Assets, Liabilities, and Equity Trend ({target_org})",
                'font': {
                    'size': 28,
                    'color': '#007A3D',
                    'family': 'Arial'
                }
            },
            yaxis=dict(
                title=f"Amount (Rs. in {y_unit})",
                tickformat=".1f",
                tickprefix="",
                hoverformat=".1f"
            ),
            xaxis=dict(
                title="Year",
                tickmode='array',
                tickvals=year_cols,
                ticktext=year_cols
            ),
            height=500,
            margin=dict(t=40, b=20)
        )

        st.plotly_chart(fig_line, use_container_width=True, key="line_chart_yearly")

        st.markdown("<br><br>", unsafe_allow_html=True)

        trend_data = df_main.copy()
        trend_data.columns = trend_data.columns.astype(str)

        # Filter only relevant rows
        trend_data = trend_data[trend_data['Org Name'] == target_org].copy()

        # Convert years to numeric
        trend_data[year_cols] = trend_data[year_cols].apply(pd.to_numeric, errors='coerce')

        fig_trend = go.Figure()

        for label, patterns in metric_patterns.items():
            found = False
            for pattern in patterns:
                row = trend_data[trend_data['Item Name'].str.lower().str.contains(pattern, regex=True, na=False)]
                if not row.empty:
                    values = row[year_cols].values.flatten()
                    fig_trend.add_trace(go.Scatter(
                        x=year_cols,
                        y=values / 1e6,
                        mode='lines+markers',
                        name=label,
                        line=dict(color=(
                            "green" if label.lower() == "profit after tax" else
                            "orange" if label.lower() == "gross revenue" else
                            None
                        ))
                    ))
                    found = True
                    break
            if not found:
                print(f"[INFO] '{label}' not found for {target_org}")

        fig_trend.update_layout(
            title={
                'text': f"Financial Metrics Trend ({target_org})",
                'font': {
                    'size': 28,
                    'color': '#007A3D',
                    'family': 'Arial'
                }
            },
            yaxis_title="Amount (Rs. in Billions)",
            xaxis=dict(
                title="Year",
                type="category"
            ),
            height=500,
            margin=dict(t=40, b=20)
        )

        st.plotly_chart(fig_trend, use_container_width=True, key="multi_metric_trend_chart")

    else:
        st.info("Could not find information")




















































