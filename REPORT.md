# Singapore Jobs Analytics — Project Report

**Module 1 Assignment · NTU DSAI**
**Dataset:** SGJobData.duckdb — ~1,048,585 job postings from MyCareersFuture.sg (Oct 2022 – May 2024)

---

## 1. Business Case

- **Scenario:** Talent acquisition teams and recruitment agencies in Singapore need to prioritise sourcing and calibrate salary offers in a competitive, data-rich market.
- **Objective:** Surface the most in-demand job roles, competitive salary benchmarks by position level and industry, fastest-growing sectors, and hiring seasonality from ~1M real job postings.
- **Target users & value:** Recruiters and hiring managers — the dashboard answers the three questions they ask most often: *Which roles should I source for? What salary should I offer? Is this industry growing?* It replaces ad-hoc spreadsheet research with a filterable, always-current view of the whole market.

---

## 2. Data Handling & Process

- **Tools:** Python (Pandas), DuckDB (fast SQL reads on the ~70 MB binary), Plotly (EDA charts), Streamlit (dashboard). All dependencies managed in a `.venv`.
- **Loading:** DuckDB opened in `read_only=True` mode to avoid file-lock conflicts. Full 1M-row table loaded into a Pandas DataFrame (~350 MB in-memory) for cleaning and feature engineering.
- **Key quality issues found:**
  - **~3,988 blank rows** — all fields null/zero; caused by padding in the source CSV. Removed by filtering `WHERE title IS NOT NULL`.
  - **3,987 exact duplicate rows** — all the same blank record. Removed with `drop_duplicates()`.
  - **`occupationId`** — 100% null across all rows. Dropped.
  - **Salary outliers** — `average_salary` is pre-computed as `(salary_minimum + salary_maximum) / 2`. Roughly 840 rows show maximums in the millions of SGD/month (e.g. S$25 M/month for a clinic assistant) — clearly data-entry errors. Filtered to `500 ≤ average_salary ≤ 50,000 SGD/month`.
- **Cleaning decisions:**
  - `categories` stored as a JSON array of `{id, category}` objects — parsed with `json.loads()` to extract the first (primary) category as a plain string.
  - `title` normalised to lowercase + stripped of whitespace to collapse case-variant duplicates (`SUPERVISOR` / `Supervisor` / `supervisor` → `supervisor`).
  - Date columns (`metadata_originalPostingDate`) cast to `datetime64` and used to derive `posting_month` and `posting_year`.
- **Feature engineering:**

  | Feature | Logic |
  |---|---|
  | `primary_category` | First category object from JSON array |
  | `title_norm` | `title.lower().strip()` |
  | `posting_month` | `YYYY-MM` period string from posting date |
  | `posting_year` | Integer year |
  | `seniority` | 4-tier mapping from `positionLevels`: Junior / Mid / Senior / Management |
  | `salary_band` | Singapore-market tiers: Entry (<$2.5k) / Junior / Mid / Senior / Premium (>$12k) |
  | `is_repost` | `repostCount > 0` |

- **EDA highlights (that shaped dashboard design):**
  - Admin/Secretarial, IT, and Sales account for >30% of all postings → industry filter is a core UI element.
  - Permanent + Full Time = ~81% of postings; part-time is minor but still worth filtering.
  - Median salary rises from ~S$2,500 (entry) to ~S$8,000+ (Senior Management) — a salary-by-level chart is a must-have.
  - ~55% of postings fall in the Junior ($2.5k–$4.5k) band — the market skews mid-level.
  - Posting volume stabilised at ~75k/month from mid-2023; no sharp seasonality found.
  - Title normalisation collapsed ~15% of title variants, making the top-N ranking more meaningful.
- **Clean dataset:** 1,040,000+ rows exported to `cleaned_jobs.parquet` (~50 MB). The Streamlit app reads this file directly — no DuckDB dependency at runtime.

---

## 3. Dashboard / App

- **Type:** Streamlit single-page dashboard (`streamlit_app.py`), runs locally or on Streamlit Cloud.
- **Sidebar filters:** Date range, Industry (multi-select), Employment Type, Seniority, Salary Band. All filters compose (AND logic) and update all four tabs simultaneously.
- **Tab 1 — Overview:**
  - 4 KPI cards: total postings, unique role titles, median salary, top industry.
  - Area chart: monthly posting volume over time.
  - Donut chart: employment type split.
  - Horizontal bar: top 15 industries by volume.
  - *Supports*: quick market-sizing and industry prioritisation for a new search engagement.
- **Tab 2 — Roles & Industries:**
  - Interactive slider selects top N job titles (10–50); horizontal bar chart ordered by demand.
  - Seniority distribution bar chart.
  - Position levels bar chart.
  - Top 20 hiring companies (sortable table).
  - *Supports*: deciding which roles to source for and which companies are most active.
- **Tab 3 — Salary Intelligence:**
  - 4 KPI cards: median, P25, P75, top-1% salary.
  - Salary band distribution bar.
  - Median salary by position level (colour-coded low→high).
  - Median salary by industry (horizontal bar, sorted descending).
  - Top-paying roles table (filtered to roles with ≥50 postings for statistical reliability).
  - *Supports*: crafting competitive salary offers and setting realistic expectations with hiring managers.
- **Tab 4 — Hiring Trends:**
  - Monthly postings by year (line chart, colour-coded by year) — reveals year-over-year growth.
  - Top 5 industry trend lines — shows relative momentum.
  - Median salary trend over time.
  - Employment type trends.
  - Industry growth table: 2023 vs 2024 (Jan–May), with 2023 normalised to a 5-month window for fair comparison.
  - *Supports*: timing hiring campaigns and spotting growing/declining sectors.
- **Design choices:** Two-column layouts to maximise information density; Plotly for interactive hover/zoom; consistent blue palette with RdYlGn accent for salary gradients; `st.cache_data` ensures the 1M-row parquet is loaded only once per session (~2 s startup).

---

## 4. Presentation Flow (10 mins)

1. **Business case & objective (2–3 mins)** — scenario, target users, the three business questions the dashboard answers, success criteria (time-to-insight < 5 mins).
2. **Process & data handling (3–4 mins)** — show `analysis.ipynb`: loading from DuckDB, the salary outlier issue and how we capped it, categories JSON parsing, feature engineering table above.
3. **Dashboard walkthrough (3–4 mins)** — live demo or screenshots: Overview (KPIs + trend), Salary tab (salary-by-level chart, top-paying roles), Trends tab (YoY growth table). Apply a filter (e.g. IT industry) and show all tabs update.
4. **Challenges & learnings (1–2 mins):**
   - DuckDB file-locking in Jupyter required `read_only=True` and a copy of the database.
   - Salary data had millions-of-SGD outliers with no obvious pattern — required a cap rather than a model-based correction.
   - Title normalisation (lowercase) alone collapsed a large fraction of duplicates; fuzzy clustering would further improve role grouping.
   - **Next steps:** skill-tag extraction from descriptions, role taxonomy clustering, predictive salary-band model.

---

## Deliverables

| File | Description |
|---|---|
| `analysis.ipynb` | Data cleaning, feature engineering, and EDA notebook |
| `streamlit_app.py` | Streamlit dashboard (4 tabs, sidebar filters) |
| `cleaned_jobs.parquet` | Cleaned dataset (~1M rows) produced by the notebook |
| `REPORT.md` | This file |
| `README.md` | Setup and run instructions |
| `requirements.txt` | Python dependencies |
