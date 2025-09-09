import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

st.set_page_config(page_title="Trade and Customs Dashboard", layout="wide")

# ----------------------------
# Load Data
# ----------------------------
@st.cache_data
def load_data():
    return pd.read_excel("Cleaned_Trade_and_Custom.xlsx")

df = load_data()

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

# Metric selection
metric = st.sidebar.selectbox(
    "Select Metric",
    ["CIF Value (N)", "FOB Value (N)", "Total Tax(N)"]
)

# HS Code filter
hs_codes = st.sidebar.multiselect(
    "Select HS Codes",
    options=df["HS Code"].unique(),
    default=None
)

# Country filter
countries = st.sidebar.multiselect(
    "Select Country of Origin",
    options=df["Country of Origin"].unique(),
    default=None
)

# Top N selector
top_n = st.sidebar.slider("Select Top N", 5, 20, 10)

# ----------------------------
# Apply Filters
# ----------------------------
filtered_df = df.copy()

if hs_codes:
    filtered_df = filtered_df[filtered_df["HS Code"].isin(hs_codes)]

if countries:
    filtered_df = filtered_df[filtered_df["Country of Origin"].isin(countries)]

# ----------------------------
# Aggregation
# ----------------------------
agg_data = filtered_df.groupby("HS Code")[[metric]].sum().reset_index()
top_imports = agg_data.sort_values(by=metric, ascending=False).head(top_n)

# ----------------------------
# Chart
# ----------------------------
st.subheader(f"Top {top_n} HS Codes by {metric}")

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="HS Code", x=metric, data=top_imports, palette="Blues_r", ax=ax)

# Format axis in billions or millions
def format_billions(x, pos):
    if x >= 1e9:
        return f'{x*1e-9:.1f}B'
    elif x >= 1e6:
        return f'{x*1e-6:.1f}M'
    else:
        return f'{x:,.0f}'

ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_billions))
ax.set_xlabel(metric)
ax.set_ylabel("HS Code")

st.pyplot(fig)

# ----------------------------
# Key Insights
# ----------------------------
st.subheader("Key Insights")

total_value = filtered_df[metric].sum()
top_hs_code = top_imports.iloc[0]["HS Code"] if not top_imports.empty else "N/A"
top_hs_value = top_imports.iloc[0][metric] if not top_imports.empty else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total " + metric, format_billions(total_value, None))

with col2:
    st.metric("Top HS Code", top_hs_code)

with col3:
    st.metric("Top HS Code Value", format_billions(top_hs_value, None))

st.markdown("---")
st.write(" Use the filters on the left to explore trade data by HS Code, Country, and Value Metric.")
