import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# ===============================
# Load Data
# ===============================
@st.cache_data
def load_data():
    df = pd.read_excel("Cleaned_Trade_and_Custom.xlsx")
    return df

df = load_data()

# ===============================
# Streamlit App Layout
# ===============================
st.title("Trade and Customs Data Dashboard")

st.markdown("""
This dashboard presents exploratory data analysis (EDA) on trade and customs data.
The focus is on imports, tax revenue, and country contributions.
""")

# ===============================
# Key Metrics
# ===============================
total_imports = df["CIF Value (N)"].sum()
total_fob = df["FOB Value (N)"].sum()
total_tax = df["Total Tax(N)"].sum()
unique_importers = df["Importer"].nunique()

st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total CIF Imports (₦)", f"{total_imports:,.0f}")
col2.metric("Total FOB Value (₦)", f"{total_fob:,.0f}")
col3.metric("Total Tax Revenue (₦)", f"{total_tax:,.0f}")
col4.metric("Unique Importers", unique_importers)

# ===============================
# Visualization Functions
# ===============================
def format_axis(ax):
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.tight_layout()

# 1. Imports by HS Code
st.subheader("Top 10 Imports by HS Code")
imports_by_hs = df.groupby("HS Code")["CIF Value (N)"].sum().sort_values(ascending=False).head(10).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="HS Code", x="CIF Value (N)", data=imports_by_hs, ax=ax, orient="h", palette="Blues_r")
ax.set_xlabel("CIF Value (₦)")
ax.set_ylabel("HS Code")
format_axis(ax)
st.pyplot(fig)

# 2. Top Countries of Supply
st.subheader("Top 10 Countries of Supply")
supply_countries = df.groupby("Country of Supply")["CIF Value (N)"].sum().sort_values(ascending=False).head(10).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="Country of Supply", x="CIF Value (N)", data=supply_countries, ax=ax, orient="h", palette="Greens_r")
ax.set_xlabel("CIF Value (₦)")
ax.set_ylabel("Country of Supply")
format_axis(ax)
st.pyplot(fig)

# 3. Top Countries of Origin
st.subheader("Top 10 Countries of Origin")
origin_countries = df.groupby("Country of Origin")["CIF Value (N)"].sum().sort_values(ascending=False).head(10).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="Country of Origin", x="CIF Value (N)", data=origin_countries, ax=ax, orient="h", palette="Oranges_r")
ax.set_xlabel("CIF Value (₦)")
ax.set_ylabel("Country of Origin")
format_axis(ax)
st.pyplot(fig)

# 4. Tax Revenue Contributions by HS Code
st.subheader("Top 10 Tax Revenue Contributions by HS Code")
tax_by_hs = df.groupby("HS Code")["Total Tax(N)"].sum().sort_values(ascending=False).head(10).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="HS Code", x="Total Tax(N)", data=tax_by_hs, ax=ax, orient="h", palette="Purples_r")
ax.set_xlabel("Tax Revenue (₦)")
ax.set_ylabel("HS Code")
format_axis(ax)
st.pyplot(fig)

# 5. Top Importers by CIF Value
st.subheader("Top 10 Importers by CIF Value")
top_importers = df.groupby("Importer")["CIF Value (N)"].sum().sort_values(ascending=False).head(10).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="Importer", x="CIF Value (N)", data=top_importers, ax=ax, orient="h", palette="Reds_r")
ax.set_xlabel("CIF Value (₦)")
ax.set_ylabel("Importer")
format_axis(ax)
st.pyplot(fig)

# ===============================
# Notes
# ===============================
st.markdown("""
**Notes:**
- All figures are in Nigerian Naira (₦).
- Only top 10 categories are displayed in charts for clarity.
- Charts use horizontal orientation for readability.
""")
