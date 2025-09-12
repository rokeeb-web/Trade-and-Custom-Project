import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# ===============================
# Streamlit Page Config
# ===============================
st.set_page_config(page_title="Trade and Customs Dashboard", layout="wide")

# ===============================
# Load Data
# ===============================
@st.cache_data
def load_data(path="Cleaned_Custom_Import_Dataset.xlsx"):
    return pd.read_excel(path)

try:
    df = load_data()
except FileNotFoundError:
    st.error("Default dataset not found. Please upload your dataset.")
    df = None

# ===============================
# Sidebar Upload & Filters
# ===============================
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

if df is not None:
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
    # Layout Header
    # ===============================
    st.title("Trade and Customs Data Dashboard")
    st.markdown("""
    This interactive dashboard presents exploratory data analysis (EDA) on trade and customs data.  
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

    st.markdown("---")

    # ===============================
    # Visualization Helper
    # ===============================
    def plot_bar(data, x_col, y_col, xlabel, ylabel, palette):
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(
            y=y_col,
            x=x_col,
            data=data,
            ax=ax,
            orient="h",
            palette=palette,
            order=list(data.sort_values(x_col, ascending=False)[y_col]),
        )
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(ylabel, fontsize=13, weight="bold")
        plt.tight_layout()
        st.pyplot(fig)

    # ===============================
    # Visualizations
    # ===============================
    # 1. Imports by HS Product
    st.subheader(f"Top {top_n} Imports by HS Product ({metric})")
    imports_by_hs = (
        filtered_df.groupby("HS Product")[metric]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    imports_by_hs["Scaled"] = imports_by_hs[metric] / 1e9
    plot_bar(imports_by_hs, "Scaled", "HS Product", f"{metric} in Billions (₦)", "HS Product", "Blues_r")

    # 2. Top Countries of Supply
    st.subheader(f"Top {top_n} Countries of Supply ({metric})")
    supply_countries = (
        filtered_df.groupby("Country of Supply")[metric]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    supply_countries["Scaled"] = supply_countries[metric] / 1e9
    plot_bar(supply_countries, "Scaled", "Country of Supply", f"{metric} in Billions (₦)", "Country of Supply", "Greens_r")

    # 3. Top Countries of Origin
    st.subheader(f"Top {top_n} Countries of Origin ({metric})")
    origin_countries = (
        filtered_df.groupby("Country of Origin")[metric]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    origin_countries["Scaled"] = origin_countries[metric] / 1e9
    plot_bar(origin_countries, "Scaled", "Country of Origin", f"{metric} in Billions (₦)", "Country of Origin", "Oranges_r")

    # 4. Tax Revenue Contributions by HS Product
    st.subheader(f"Top {top_n} Tax Revenue Contributions by HS Product")
    tax_by_hs = (
        filtered_df.groupby("HS Product")["Total Tax(N)"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    tax_by_hs["Scaled"] = tax_by_hs["Total Tax(N)"] / 1e9
    plot_bar(tax_by_hs, "Scaled", "HS Product", "Tax Revenue in Billions (₦)", "HS Product", "Purples_r")

    # 5. Top Importers by CIF Value
    st.subheader(f"Top {top_n} Importers by CIF Value")
    top_importers = (
        filtered_df.groupby("Importer")["CIF Value (N)"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    top_importers["Scaled"] = top_importers["CIF Value (N)"] / 1e9
    plot_bar(top_importers, "Scaled", "Importer", "CIF Value in Billions (₦)", "Importer", "Reds_r")

    # 6. Correlation Heatmap
    st.subheader("Correlation between Trade Variables")
    numeric_cols = ["CIF Value (N)", "FOB Value (N)", "Total Tax(N)"]
    corr_matrix = filtered_df[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    ax.set_title("Correlation Heatmap of Trade Variables", fontsize=13, weight="bold")
    st.pyplot(fig)

    # 7. Monthly Trade Volume (Line Chart)
    st.subheader("Monthly Trade Volume (Aggregated)")

    date_candidates = ["Receipt Date", "Receipt_Date", "Date", "date", "receipt_date"]
    date_col = next((c for c in date_candidates if c in filtered_df.columns), None)

    if date_col is None:
        st.info("No date column (e.g., 'Receipt Date') found in dataset — monthly trend can't be shown.")
    else:
        filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors="coerce")
        trend_df = filtered_df.dropna(subset=[date_col, metric]).copy()

        if trend_df.empty:
            st.info("No valid rows with both date and metric values to plot.")
        else:
            monthly_volume = (
                trend_df.groupby(trend_df[date_col].dt.to_period("M"))[metric]
                .sum()
                .reset_index()
            )
            monthly_volume[date_col] = monthly_volume[date_col].dt.to_timestamp()
            monthly_volume[metric + "_Billions"] = monthly_volume[metric] / 1e9

            fig_trend = px.line(
                monthly_volume,
                x=date_col,
                y=metric + "_Billions",
                markers=True,
                title=f"Monthly {metric} (₦ Billions)",
                labels={metric + "_Billions": f"{metric} (₦ Billions)", date_col: "Month"},
            )
            fig_trend.update_layout(
                height=400,  # shorter height
                xaxis_tickformat="%b %Y",
                hovermode="x unified",
                title_font=dict(size=16, family="Arial", color="black"),
                margin=dict(l=40, r=20, t=50, b=40),
            )
            st.plotly_chart(fig_trend, use_container_width=True)

    # ===============================
    # Data Download
    # ===============================
    st.subheader("Download Filtered Data")
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        data=csv,
        file_name="filtered_trade_data.csv",
        mime="text/csv",
    )
# ===============================
# Insights
# ===============================
st.subheader("Key Insights")

if not imports_by_hs.empty:
    top_hs = imports_by_hs.iloc[0]
    st.write(
        f"The top HS Product is **{top_hs['HS Product']}** with a value of **₦{top_hs['Scaled']:.2f}B**."
    )

if not origin_countries.empty:
    top_country = origin_countries.iloc[0]
    st.write(
        f"The top country of origin is **{top_country['Country of Origin']}** with imports worth **₦{top_country['Scaled']:.2f}B**."
    )

if not supply_countries.empty:
    top_supply = supply_countries.iloc[0]
    st.write(
        f"The top country of supply is **{top_supply['Country of Supply']}** contributing **₦{top_supply['Scaled']:.2f}B**."
    )

st.markdown("---")
st.markdown("Use filters on the left to refine the analysis and download the customized dataset.")

