# Singapore Jobs Analytics

Talent-acquisition intelligence dashboard built on ~1M job postings from MyCareersFuture.sg.

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the data-cleaning notebook (first time only)
#    Opens analysis.ipynb — run all cells to produce cleaned_jobs.parquet
jupyter notebook analysis.ipynb

# 4. Launch the Streamlit dashboard
streamlit run streamlit_app.py

# 5 Streamlit URL 
https://jobmktanalytics-geeky.streamlit.app/
```

The dashboard opens at `http://localhost:8501`.

## Files

| File | Description |
|---|---|
| `analysis.ipynb` | Data loading, cleaning, feature engineering, EDA, and parquet export |
| `streamlit_app.py` | Streamlit dashboard — 4 tabs, sidebar filters |
| `cleaned_jobs.parquet` | Cleaned dataset produced by the notebook (created on first run) |
| `SGJobData.duckdb` | Source database (~70 MB DuckDB binary) |
| `REPORT.md` | Full written report following assignment Sections 1–4 |
| `requirements.txt` | Python dependencies |

## Notes

- The notebook connects to `SGJobData.duckdb` with `read_only=True`
- The dashboard reads only `cleaned_jobs.parquet` — no DuckDB connection needed at runtime.
- First load of the parquet takes ~2 s; subsequent tab switches are instant thanks to `@st.cache_data`.
