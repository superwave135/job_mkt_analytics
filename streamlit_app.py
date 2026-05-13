"""Singapore Jobs Market Analytics Dashboard
Talent Acquisition Intelligence — NTU DSAI M1 Project
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="SG Jobs Analytics Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {padding-top: 1.5rem;}
[data-testid="metric-container"] {background:#f0f4fa; padding:.75rem 1rem; border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
SALARY_BANDS = [
    "Entry (<$2.5k)",
    "Junior ($2.5k-$4.5k)",
    "Mid ($4.5k-$7.5k)",
    "Senior ($7.5k-$12k)",
    "Premium (>$12k)",
]
SENIORITY_ORDER = ["Junior", "Mid", "Senior", "Management", "Other"]
LEVEL_ORDER = [
    "Fresh/entry level", "Junior Executive", "Non-executive",
    "Executive", "Professional", "Senior Executive",
    "Manager", "Middle Management", "Senior Management",
]
BRAND_BLUE = "#003DA5"

# ── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading job data…")
def load_data() -> pd.DataFrame:
    df = pd.read_parquet("cleaned_jobs.parquet")
    df["posting_date"] = pd.to_datetime(df["posting_date"])
    df["posting_year"] = df["posting_year"].astype(int)
    return df


df_full = load_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.title("SG Jobs Analytics")
    st.caption(f"**{len(df_full):,}** postings · Oct 2022 – May 2024")
    st.divider()

    min_d = df_full["posting_date"].min().date()
    max_d = df_full["posting_date"].max().date()
    date_range = st.date_input(
        "Posting Date Range",
        value=(min_d, max_d),
        min_value=min_d,
        max_value=max_d,
    )
    # date_input may return 1 or 2 values while user is picking
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        date_start, date_end = date_range
    else:
        date_start, date_end = min_d, max_d

    industries_avail = sorted(df_full["primary_category"].dropna().unique())
    sel_industries = st.multiselect("Industry", industries_avail)

    emp_types_avail = sorted(df_full["employmentTypes"].dropna().unique())
    sel_emp = st.multiselect("Employment Type", emp_types_avail)

    sel_seniority = st.multiselect("Seniority", SENIORITY_ORDER[:4])
    sel_bands = st.multiselect("Salary Band", SALARY_BANDS)

    st.divider()
    st.caption("Source: MyCareersFuture.sg  ")

# ── Apply Filters ────────────────────────────────────────────────────────────
mask = (
    (df_full["posting_date"].dt.date >= date_start)
    & (df_full["posting_date"].dt.date <= date_end)
)
if sel_industries:
    mask &= df_full["primary_category"].isin(sel_industries)
if sel_emp:
    mask &= df_full["employmentTypes"].isin(sel_emp)
if sel_seniority:
    mask &= df_full["seniority"].isin(sel_seniority)
if sel_bands:
    mask &= df_full["salary_band"].isin(sel_bands)

df = df_full[mask].copy()

if df.empty:
    st.warning("No data matches the current filters — please widen your selection.")
    st.stop()

# ── Page Header ───────────────────────────────────────────────────────────────
st.title("Singapore Jobs Market Analytics")
st.caption(
    f"Showing **{len(df):,}** postings  ·  "
    f"**{df['posting_month'].nunique()}** months  ·  "
    f"**{df['primary_category'].nunique()}** industries"
)

tab_overview, tab_roles, tab_salary, tab_trends = st.tabs([
    "📊 Overview", "🔍 Roles & Industries", "💰 Salary Intelligence", "📈 Hiring Trends"
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════
with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Postings", f"{len(df):,}")
    c2.metric("Unique Role Titles", f"{df['title_norm'].nunique():,}")
    c3.metric("Median Salary / month", f"S${df['average_salary'].median():,.0f}")
    top_ind = df["primary_category"].value_counts().idxmax()
    c4.metric("Top Industry", top_ind)

    st.divider()

    left, right = st.columns([3, 2])
    with left:
        monthly = df.groupby("posting_month").size().reset_index(name="count")
        fig = px.area(
            monthly, x="posting_month", y="count",
            title="Monthly Job Postings",
            labels={"posting_month": "", "count": "Postings"},
            color_discrete_sequence=[BRAND_BLUE],
        )
        fig.update_layout(height=320)
        st.plotly_chart(fig, width='stretch')

    with right:
        emp_c = df["employmentTypes"].value_counts().reset_index()
        emp_c.columns = ["type", "count"]
        fig = px.pie(
            emp_c, values="count", names="type",
            title="Employment Types", hole=0.42,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(height=400, legend=dict(orientation="v", x=1.0))
        st.plotly_chart(fig, width='stretch')

    ind_c = df["primary_category"].value_counts().head(15).reset_index()
    ind_c.columns = ["industry", "count"]
    fig = px.bar(
        ind_c, x="count", y="industry", orientation="h",
        title="Top 15 Industries by Posting Volume",
        labels={"count": "Postings", "industry": ""},
        color="count", color_continuous_scale="Blues",
    )
    fig.update_layout(
        height=480, yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig, width='stretch')

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — ROLES & INDUSTRIES
# ═══════════════════════════════════════════════════════════════════════════
with tab_roles:
    n = st.slider("Number of roles to display", 10, 50, 20, key="n_roles")

    left, right = st.columns([3, 2])
    with left:
        tc = df["title_norm"].value_counts().head(n).reset_index()
        tc.columns = ["title", "count"]
        fig = px.bar(
            tc, x="count", y="title", orientation="h",
            title=f"Top {n} Job Titles",
            labels={"count": "Postings", "title": ""},
            color="count", color_continuous_scale="Greens",
        )
        fig.update_layout(
            height=max(400, n * 22),
            yaxis={"categoryorder": "total ascending"},
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig, width='stretch')

    with right:
        sc = (
            df["seniority"]
            .value_counts()
            .reindex(SENIORITY_ORDER, fill_value=0)
            .reset_index()
        )
        sc.columns = ["seniority", "count"]
        fig = px.bar(
            sc, x="seniority", y="count",
            title="Seniority Distribution",
            color="seniority",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_layout(height=280, showlegend=False)
        st.plotly_chart(fig, width='stretch')

        avail_levels = [l for l in LEVEL_ORDER if l in df["positionLevels"].values]
        pc = (
            df["positionLevels"]
            .value_counts()
            .reindex(avail_levels, fill_value=0)
            .reset_index()
        )
        pc.columns = ["level", "count"]
        fig = px.bar(
            pc, x="count", y="level", orientation="h",
            title="Position Levels",
            color="count", color_continuous_scale="Purples",
        )
        fig.update_layout(
            height=360, yaxis={"categoryorder": "total ascending"},
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig, width='stretch')

    st.subheader("Top Hiring Companies")
    co_c = df["postedCompany_name"].value_counts().head(20).reset_index()
    co_c.columns = ["Company", "Postings"]
    st.dataframe(co_c, width='stretch', height=380, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — SALARY INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════
with tab_salary:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Median Salary", f"S${df['average_salary'].median():,.0f}/mo")
    c2.metric("25th Percentile", f"S${df['average_salary'].quantile(0.25):,.0f}/mo")
    c3.metric("75th Percentile", f"S${df['average_salary'].quantile(0.75):,.0f}/mo")
    c4.metric("Top 1% Earners", f"S${df['average_salary'].quantile(0.99):,.0f}/mo")

    st.divider()

    left, right = st.columns(2)
    with left:
        band_c = (
            df["salary_band"]
            .value_counts()
            .reindex(SALARY_BANDS, fill_value=0)
            .reset_index()
        )
        band_c.columns = ["band", "count"]
        fig = px.bar(
            band_c, x="band", y="count",
            title="Postings by Salary Band",
            color="band",
            color_discrete_sequence=px.colors.sequential.Blues[1:],
        )
        fig.update_layout(height=340, xaxis_tickangle=-15, showlegend=False)
        st.plotly_chart(fig, width='stretch')

    with right:
        avail_levels = [l for l in LEVEL_ORDER if l in df["positionLevels"].values]
        sal_lvl = (
            df.groupby("positionLevels")["average_salary"]
            .median()
            .reindex(avail_levels)
            .reset_index()
        )
        sal_lvl.columns = ["level", "median_salary"]
        fig = px.bar(
            sal_lvl, x="level", y="median_salary",
            title="Median Salary by Position Level (SGD/month)",
            color="median_salary", color_continuous_scale="RdYlGn",
            labels={"median_salary": "Median (SGD)", "level": ""},
        )
        fig.update_layout(height=340, xaxis_tickangle=-25, coloraxis_showscale=False)
        st.plotly_chart(fig, width='stretch')

    sal_ind = (
        df.groupby("primary_category")["average_salary"]
        .median()
        .sort_values(ascending=False)
        .head(15)
        .reset_index()
    )
    sal_ind.columns = ["industry", "median_salary"]
    fig = px.bar(
        sal_ind, x="median_salary", y="industry", orientation="h",
        title="Median Salary by Industry (SGD/month)",
        color="median_salary", color_continuous_scale="Viridis",
        labels={"median_salary": "Median (SGD/month)", "industry": ""},
    )
    fig.update_layout(
        height=480, yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig, width='stretch')

    st.subheader("Top-Paying Roles (min. 50 postings)")
    top_roles = (
        df.groupby("title_norm")
        .agg(median_salary=("average_salary", "median"), postings=("average_salary", "count"))
        .query("postings >= 50")
        .sort_values("median_salary", ascending=False)
        .head(20)
        .reset_index()
    )
    top_roles["median_salary"] = top_roles["median_salary"].round(0).astype(int)
    top_roles.columns = ["Role", "Median Salary (SGD/month)", "Postings"]
    st.dataframe(top_roles, width='stretch', height=420, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — HIRING TRENDS
# ═══════════════════════════════════════════════════════════════════════════
with tab_trends:
    monthly_yr = (
        df.groupby(["posting_month", "posting_year"])
        .size()
        .reset_index(name="count")
    )
    monthly_yr["posting_year"] = monthly_yr["posting_year"].astype(str)
    fig = px.line(
        monthly_yr, x="posting_month", y="count", color="posting_year",
        title="Monthly Job Postings by Year",
        labels={"posting_month": "", "count": "Postings", "posting_year": "Year"},
        color_discrete_sequence=px.colors.qualitative.Set1,
        markers=True,
    )
    fig.update_layout(height=380)
    st.plotly_chart(fig, width='stretch')

    top5_ind = df["primary_category"].value_counts().head(5).index.tolist()
    ind_mth = (
        df[df["primary_category"].isin(top5_ind)]
        .groupby(["posting_month", "primary_category"])
        .size()
        .reset_index(name="count")
    )
    fig = px.line(
        ind_mth, x="posting_month", y="count", color="primary_category",
        title="Monthly Postings — Top 5 Industries",
        labels={"posting_month": "", "count": "Postings", "primary_category": "Industry"},
    )
    fig.update_layout(height=380)
    st.plotly_chart(fig, width='stretch')

    left, right = st.columns(2)
    with left:
        sal_mth = (
            df.groupby("posting_month")["average_salary"]
            .median()
            .reset_index()
        )
        sal_mth.columns = ["month", "median_salary"]
        fig = px.line(
            sal_mth, x="month", y="median_salary",
            title="Median Salary Trend (SGD/month)",
            labels={"month": "", "median_salary": "Median Salary"},
            color_discrete_sequence=["#e74c3c"],
        )
        fig.update_layout(height=320)
        st.plotly_chart(fig, width='stretch')

    with right:
        top4_emp = df["employmentTypes"].value_counts().head(4).index.tolist()
        emp_mth = (
            df[df["employmentTypes"].isin(top4_emp)]
            .groupby(["posting_month", "employmentTypes"])
            .size()
            .reset_index(name="count")
        )
        fig = px.line(
            emp_mth, x="posting_month", y="count", color="employmentTypes",
            title="Employment Type Trends",
            labels={"posting_month": "", "count": "Postings", "employmentTypes": "Type"},
        )
        fig.update_layout(height=320)
        st.plotly_chart(fig, width='stretch')

    st.subheader("Industry Growth: 2023 vs 2024 (Jan–May, normalised)")
    y23 = df[df["posting_year"] == 2023].groupby("primary_category").size()
    y24 = df[df["posting_year"] == 2024].groupby("primary_category").size()
    y23_adj = y23 * (5 / 12)  # scale 2023 to a 5-month comparable window
    growth_df = pd.DataFrame({
        "2023 Adj. (5 mo)": y23_adj.round(0),
        "2024 (Jan-May)": y24,
    }).fillna(0).astype(int)
    growth_df["Growth %"] = (
        (growth_df["2024 (Jan-May)"] - growth_df["2023 Adj. (5 mo)"])
        / growth_df["2023 Adj. (5 mo)"].replace(0, np.nan) * 100
    ).round(1)
    growth_df = (
        growth_df.sort_values("Growth %", ascending=False)
        .reset_index()
        .rename(columns={"primary_category": "Industry"})
    )
    st.dataframe(growth_df, width='stretch', height=420, hide_index=True)
