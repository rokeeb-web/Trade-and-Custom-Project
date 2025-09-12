import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title="Trade and Customs Dashboard", layout="wide")

# ===============================
# Load Data
# ===============================
@st.cache_data
def load_data():
    return pd.read_excel("Cleaned_Custom_Import_Dataset.xlsx")

df = load_data()

# Ensure date column is datetime
if "Receipt Date" in df.columns:
    df["Receipt Date"] = pd.to_datetime(df["Receipt Date"], errors="coerce")

# ===============================
# Sidebar Filters
# ===============================
st.sidebar.header("Filters")

metric = st.sidebar.selectbox(
    "Select Metric",
    ["CIF Value (N)", "FOB Value (N)", "Total Tax(N)"]
)

hs_products = st.sidebar.multiselect(
    "Filter by HS Product",
    options=df["HS Product"].dropna().unique()
)

countries_origin = st.sidebar.multiselect(
    "Filter by Country of Origin",
    options=df["Country of Origin"].dropna().unique()
)

countries_supply = st.sidebar.multiselect(
    "Filter by Country of Supply",
    options=df["Country of Supply"].dropna().unique()
)

top_n = st.sidebar.slider("Select Top N", 5, 20, 10)

# ===============================
# Apply Filters
# ===============================
filtered_df = df.copy()

if hs_products:
    filtered_df = filtered_df[filtered_df["HS Product"].isin(hs_products)]

if countries_origin:
    filtered_df = filtered_df[filtered_df["Country of Origin"].isin(countries_origin)]

if countries_supply:
    filtered_df = filtered_df[filtered_df["Country of Supply"].isin(countries_supply)]

# ===============================
# Helper: Format numbers
# ===============================
def human_format(x):
    if x >= 1e9:
        return f"{x/1e9:.2f}"
    elif x >= 1e6:
        return f"{x/1e6:.2f}"
    else:
        return f"{x:,.0f}"

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
col1.metric("Total CIF Imports (₦)", f"{human_format(total_imports)}B")
col2.metric("Total FOB Value (₦)", f"{human_format(total_fob)}B")
col3.metric("Total Tax Revenue (₦)", f"{human_format(total_tax)}B")
col4.metric("Unique Importers", unique_importers)

# ===============================
# Visualization Function
# ===============================
def plot_bar(data, x_col, y_col, xlabel, ylabel, palette):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x=x_col, y=y_col, data=data, ax=ax, palette=palette,
        order=data.sort_values(x_col, ascending=False)[x_col]
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    st.pyplot(fig)

# ===============================
# Visualizations
# ===============================

# 1. Imports by HS Product
st.subheader(f"Top {top_n} Imports by HS Product ({metric})")
imports_by_hs = (
    filtered_df.groupby("HS Product")[metric].sum().sort_values(ascending=False).head(top_n).reset_index()
)
imports_by_hs["Scaled"] = imports_by_hs[metric] / 1e9
plot_bar(imports_by_hs, "Scaled", "HS Product", f"{metric} in Billions (₦)", "HS Product", "Blues_r")

# 2. Top Countries of Supply
st.subheader(f"Top {top_n} Countries of Supply ({metric})")
supply_countries = (
    filtered_df.groupby("Country of Supply")[metric].sum().sort_values(ascending=False).head(top_n).reset_index()
)
supply_countries["Scaled"] = supply_countries[metric] / 1e9
plot_bar(supply_countries, "Scaled", "Country of Supply", f"{metric} in Billions (₦)", "Country of Supply", "Greens_r")

# 3. Top Countries of Origin
st.subheader(f"Top {top_n} Countries of Origin ({metric})")
origin_countries = (
    filtered_df.groupby("Country of Origin")[metric].sum().sort_values(ascending=False).head(top_n).reset_index()
)
origin_countries["Scaled"] = origin_countries[metric] / 1e9
plot_bar(origin_countries, "Scaled", "Country of Origin", f"{metric} in Billions (₦)", "Country of Origin", "Oranges_r")

# 4. Tax Revenue Contributions by HS Product
st.subheader(f"Top {top_n} Tax Revenue Contributions by HS Product")
tax_by_hs = (
    filtered_df.groupby("HS Product")["Total Tax(N)"].sum().sort_values(ascending=False).head(top_n).reset_index()
)
tax_by_hs["Scaled"] = tax_by_hs["Total Tax(N)"] / 1e9
plot_bar(tax_by_hs, "Scaled", "HS Product", "Tax Revenue in Billions (₦)", "HS Product", "Purples_r")

# 5. Top Importers by CIF Value
st.subheader(f"Top {top_n} Importers by CIF Value")
top_importers = (
    filtered_df.groupby("Importer")["CIF Value (N)"].sum().sort_values(ascending=False).head(top_n).reset_index()
)
top_importers["Scaled"] = top_importers["CIF Value (N)"] / 1e9
plot_bar(top_importers, "Scaled", "Importer", "CIF Value in Billions (₦)", "Importer", "Reds_r")

# 6. Correlation Heatmap
st.subheader("Correlation between Trade Variables")
numeric_cols = ["CIF Value (N)", "FOB Value (N)", "Total Tax(N)"]
corr_matrix = filtered_df[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(8,6))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
ax.set_title("Correlation Heatmap of Trade Variables")
st.pyplot(fig)

# 7. Choropleth Map
st.subheader(f"Trade Imports by Country of Origin ({metric})")

trade_map = filtered_df.groupby("Country of Origin")[metric].sum().reset_index()
trade_map[metric + "_Billions"] = trade_map[metric] / 1e9

fig = px.choropleth(
    trade_map,
    locations="Country of Origin",
    locationmode="country names",
    color=metric + "_Billions",
    hover_name="Country of Origin",
    color_continuous_scale="YlGnBu",
    title=f"Trade Imports by Country of Origin ({metric} in Billions ₦)",
    projection="natural earth"
)

fig.update_layout(
    geo=dict(showframe=False, showcoastlines=True),
    coloraxis_colorbar=dict(title=f"{metric} (₦ Billions)")
)

st.plotly_chart(fig, use_container_width=True)

# 8. Monthly Trade Volume
if "Receipt Date" in filtered_df.columns:
    st.subheader("Monthly Trade Volume (FOB Value)")
    monthly_volume = filtered_df.groupby(filtered_df["Receipt Date"].dt.to_period("M"))["FOB Value (N)"].sum()
    monthly_volume.index = monthly_volume.index.to_timestamp()

    fig, ax = plt.subplots(figsize=(12,6))
    monthly_volume.plot(ax=ax, marker="o")
    ax.set_title("Monthly Trade Volume (FOB Value)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total FOB Value")
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
    st.write(f"The top HS Product is **{top_hs['HS Product']}** with a value of **{top_hs['Scaled']:.2f}B ₦**.")
if not origin_countries.empty:
    top_country = origin_countries.iloc[0]
    st.write(f"The top country of origin is **{top_country['Country of Origin']}** with imports worth **{top_country['Scaled']:.2f}B ₦**.")
if not supply_countries.empty:
    top_supply = supply_countries.iloc[0]
    st.write(f"The top country of supply is **{top_supply['Country of Supply']}** contributing **{top_supply['Scaled']:.2f}B ₦**.")

st.markdown("---")
st.markdown("Use filters on the left to refine the analysis and download the customized dataset.")
