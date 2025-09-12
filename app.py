import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Load dataset
df = pd.read_excel("Cleaned_Custom_Import_Dataset.xlsx")

# Convert Receipt Date to datetime
df['Receipt Date'] = pd.to_datetime(df['Receipt Date'], errors='coerce')

# Set Streamlit page layout
st.set_page_config(page_title="Trade & Customs Dashboard", layout="wide")

# Title
st.title("📊 Trade & Customs Dashboard")
st.markdown("An interactive dashboard to explore trade and customs data.")

# Sidebar filters
st.sidebar.header("🔍 Filter Data")
countries = st.sidebar.multiselect("Select Country of Origin", options=df["Country of Origin"].dropna().unique())
products = st.sidebar.multiselect("Select Product", options=df["HS Product"].dropna().unique())

filtered_df = df.copy()
if countries:
    filtered_df = filtered_df[filtered_df["Country of Origin"].isin(countries)]
if products:
    filtered_df = filtered_df[filtered_df["HS Product"].isin(products)]

# ============================
# Top Stats
# ============================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🌍 Unique Countries", filtered_df["Country of Origin"].nunique())
with col2:
    st.metric("📦 Unique Products", filtered_df["HS Product"].nunique())
with col3:
    st.metric("💰 Total FOB Value (N)", f"{filtered_df['FOB Value (N)'].sum():,.0f}")

st.markdown("---")

# ============================
# 1. Vertical Bar Chart – Top Countries
# ============================
st.subheader("🌍 Top 10 Trading Countries by FOB Value")
top_countries = filtered_df.groupby("Country of Origin")["FOB Value (N)"].sum().nlargest(10).reset_index()
fig_countries = px.bar(top_countries, x="Country of Origin", y="FOB Value (N)",
                       text="FOB Value (N)", color="FOB Value (N)",
                       color_continuous_scale="Blues", height=500)
fig_countries.update_traces(texttemplate='%{text:,.0f}', textposition="outside")
st.plotly_chart(fig_countries, use_container_width=True)

# ============================
# 2. Vertical Bar Chart – Top Products
# ============================
st.subheader("📦 Top 10 Products by CIF Value")
top_products = filtered_df.groupby("HS Product")["CIF Value (N)"].sum().nlargest(10).reset_index()
fig_products = px.bar(top_products, x="HS Product", y="CIF Value (N)",
                      text="CIF Value (N)", color="CIF Value (N)",
                      color_continuous_scale="Greens", height=500)
fig_products.update_traces(texttemplate='%{text:,.0f}', textposition="outside")
st.plotly_chart(fig_products, use_container_width=True)

# ============================
# 3. Correlation Heatmap
# ============================
st.subheader("📈 Correlation between Trade Variables")
numeric_cols = ['CIF Value (N)', 'Total Tax(N)', 'FOB Value (N)']
corr_matrix = filtered_df[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
st.pyplot(fig)

# ============================
# 4. Monthly Trade Volume (Line Chart)
# ============================
st.subheader("📅 Monthly Trade Volume (FOB Value)")
monthly_volume = filtered_df.groupby(filtered_df['Receipt Date'].dt.to_period('M'))['FOB Value (N)'].sum().reset_index()
monthly_volume['Receipt Date'] = monthly_volume['Receipt Date'].astype(str)

fig_line = px.line(monthly_volume, x="Receipt Date", y="FOB Value (N)",
                   markers=True, line_shape="spline", height=400)
fig_line.update_traces(line=dict(width=3, color="royalblue"), marker=dict(size=8, color="orange"))
fig_line.update_layout(
    xaxis_title="Month",
    yaxis_title="Total FOB Value (N)",
    plot_bgcolor="white",
    font=dict(size=14),
    margin=dict(l=40, r=40, t=40, b=40)
)
st.plotly_chart(fig_line, use_container_width=True)

