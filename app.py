import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

st.set_page_config(page_title="Trade and Customs Dashboard", layout="wide")

# ===============================
# Load Data
# ===============================
@st.cache_data
def load_data():
    return pd.read_excel("Cleaned_Trade_and_Custom.xlsx")

df = load_data()

# ===============================
# Sidebar Filters
# ===============================
st.sidebar.header("Filters")

metric = st.sidebar.selectbox(
    "Select Metric",
    ["CIF Value (N)", "FOB Value (N)", "Total Tax(N)"]
)

hs_codes = st.sidebar.multiselect(
    "Filter by HS Code",
    options=df["HS Code"].unique()
)

countries_origin = st.sidebar.multiselect(
    "Filter by Country of Origin",
    options=df["Country of Origin"].unique()
)

countries_supply = st.sidebar.multiselect(
    "Filter by Country of Supply",
    options=df["Country of Supply"].unique()
)

top_n = st.sidebar.slider("Select Top N", 5, 20, 10)

# ===============================
# Apply Filters
# ===============================
filtered_df = df.copy()

if hs_codes:
    filtered_df = filtered_df[filtered_df["HS Code"].isin(hs_codes)]

if countries_origin:
    filtered_df = filtered_df[filtered_df["Country of Origin"].isin(countries_origin)]

if countries_supply:
    filtered_df = filtered_df[filtered_df["Country of Supply"].isin(countries_supply)]

# ===============================
# Helper: Format numbers
# ===============================
def human_format(x):
    if x >= 1e9:
        return f"{x/1e9:.1f}B"
    elif x >= 1e6:
        return f"{x/1e6:.1f}M"
    else:
        return f"{x:,.0f}"

def format_axis(ax):
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: human_format(x)))
    plt.tight_layout()

# ===============================
# Streamlit App Layout
# ===============================
st.title("Trade and Customs Data Dashboard")

st.markdown("""
This interactive dashboard presents exploratory data analysis (EDA) 
on trade and customs data.  
Use the filters in the sidebar to customize the view.
""")

# ===============================
# Key Metrics
# ===============================
total_imports = filtered_df["CIF Value (N)"].sum()
total_fob = filtered_df["FOB Value (N)"].sum()
total_tax = filtered_df["Total Tax(N)"].sum()
unique_importers = filtered_df["Importer"].nunique()

st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total CIF Imports (₦)", human_format(total_imports))
col2.metric("Total FOB Value (₦)", human_format(total_fob))
col3.metric("Total Tax Revenue (₦)", human_format(total_tax))
col4.metric("Unique Importers", unique_importers)

# ===============================
# Visualizations
# ===============================

# 1. Imports by HS Code
st.subheader(f"Top {top_n} Imports by HS Code ({metric})")
imports_by_hs = filtered_df.groupby("HS Code")[metric].sum().sort_values(ascending=False).head(top_n).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="HS Code", x=metric, data=imports_by_hs, ax=ax, orient="h", palette="Blues_r")
ax.set_xlabel(metric)
ax.set_ylabel("HS Code")
format_axis(ax)
st.pyplot(fig)

# 2. Top Countries of Supply
st.subheader(f"Top {top_n} Countries of Supply ({metric})")
supply_countries = filtered_df.groupby("Country of Supply")[metric].sum().sort_values(ascending=False).head(top_n).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="Country of Supply", x=metric, data=supply_countries, ax=ax, orient="h", palette="Greens_r")
ax.set_xlabel(metric)
ax.set_ylabel("Country of Supply")
format_axis(ax)
st.pyplot(fig)

# 3. Top Countries of Origin
st.subheader(f"Top {top_n} Countries of Origin ({metric})")
origin_countries = filtered_df.groupby("Country of Origin")[metric].sum().sort_values(ascending=False).head(top_n).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="Country of Origin", x=metric, data=origin_countries, ax=ax, orient="h", palette="Oranges_r")
ax.set_xlabel(metric)
ax.set_ylabel("Country of Origin")
format_axis(ax)
st.pyplot(fig)

# 4. Tax Revenue Contributions by HS Code
st.subheader(f"Top {top_n} Tax Revenue Contributions by HS Code")
tax_by_hs = filtered_df.groupby("HS Code")["Total Tax(N)"].sum().sort_values(ascending=False).head(top_n).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="HS Code", x="Total Tax(N)", data=tax_by_hs, ax=ax, orient="h", palette="Purples_r")
ax.set_xlabel("Tax Revenue (₦)")
ax.set_ylabel("HS Code")
format_axis(ax)
st.pyplot(fig)

# 5. Top Importers by CIF Value
st.subheader(f"Top {top_n} Importers by CIF Value")
top_importers = filtered_df.groupby("Importer")["CIF Value (N)"].sum().sort_values(ascending=False).head(top_n).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="Importer", x="CIF Value (N)", data=top_importers, ax=ax, orient="h", palette="Reds_r")
ax.set_xlabel("CIF Value (₦)")
ax.set_ylabel("Importer")
format_axis(ax)
st.pyplot(fig)

# ===============================
# Data Download
# ===============================
st.subheader("Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", data=csv, file_name="filtered_trade_data.csv", mime="text/csv")

# ===============================
# Insights
# ===============================
st.subheader("Key Insights")
if not imports_by_hs.empty:
    top_hs = imports_by_hs.iloc[0]
    st.write(f" The top HS Code is **{top_hs['HS Code']}** with a value of **{human_format(top_hs[metric])}**.")
if not origin_countries.empty:
    top_country = origin_countries.iloc[0]
    st.write(f" The top country of origin is **{top_country['Country of Origin']}** with imports worth **{human_format(top_country[metric])}**.")
if not supply_countries.empty:
    top_supply = supply_countries.iloc[0]
    st.write(f" The top country of supply is **{top_supply['Country of Supply']}** contributing **{human_format(top_supply[metric])}**.")

st.markdown("---")
st.markdown(" Use filters on the left to refine the analysis and download the customized dataset.")
