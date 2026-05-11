# DuckDB + SQL Lesson Plan (Using SGJobData.csv)

## 🎯 Learning Objectives

By the end of this lesson, students should be able to:

- Load CSV data into DuckDB
- Perform string manipulation in SQL
- Use regular expressions (regex) in SQL
- Write subqueries
- Use Common Table Expressions (CTEs)
- Apply window functions for analysis

---

# 📦 Part 1 — Setup & Data Loading

## 1. Create project folder

Create an empty folder and place the file `sgJobData.csv` inside it.

## 3. Set up conda environment

```bash
conda activate ddb
```

**Alternative** (if the `ddb` conda environment is not yet set up)

```bash
pip install duckdb
```

## 4. Create and load database

```python
import duckdb

con = duckdb.connect("sgJobData.db")

con.sql(
    "CREATE TABLE sg_job_data AS SELECT * FROM read_csv_auto('sgJobData.csv', HEADER=TRUE);"
)
```

## 5. Connect to db using DBGate

## 6. Preview Data

```sql
SELECT * FROM sg_job_data LIMIT 5;
```

---

# 🔤 Part 2 — String Manipulation (Data Formatting)

## Exercise: Filter by Keyword in Title

Return all rows where `title` contains the word `data` (case-insensitive).

**Using `LIKE`:**

```sql
SELECT *
FROM sg_job_data
WHERE LOWER(title) LIKE '%data%';
```

**Alternative — using regex:**

```sql
SELECT *
FROM sg_job_data
WHERE regexp_matches(title, '(?i)data');
```

> 💡 `(?i)` is a regex flag that enables **case-insensitive** matching — it will match `data`, `Data`, `DATA`, etc.

---

# 🔍 Part 3 — Regex (Regular Expressions)

## Exercise: Extract First Job Category

```sql
SELECT 
  categories,
  regexp_extract(categories, '"category":"([^"]+)"', 1) AS first_category
FROM sg_job_data;
```

> 💡 Breaking down the regex `"category":"([^"]+)"`:
> - `"category":"` — matches the literal text `"category":"`
> - `(` `)` — captures the group inside as the result
> - `[^"]+` — matches one or more characters that are **not** a double quote `"`. Breaking this down further: `[^"]` is a **negated character class** — the `[` `]` defines a set of characters to match, and the `^` at the start negates it, meaning "match anything that is NOT in this set". So `[^"]` means "any character except `"`", and the `+` means "one or more of those"
> - The `1` at the end tells DuckDB to return the **first capture group**. A capture group is the part of a regex pattern wrapped in parentheses `(` `)` — it "captures" whatever was matched inside it so you can extract it separately from the full match. For example, in `"category":"([^"]+)"`, the full match might be `"category":"Information Technology"`, but the capture group `([^"]+)` isolates just `Information Technology`. If you had multiple pairs of parentheses in your pattern, you would use `1`, `2`, `3`, etc. to refer to each group in order. For example:
>
> ```sql
> -- Pattern: "id":(\d+),"category":"([^"]+)"
... (87 lines left)