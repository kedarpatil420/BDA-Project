# Netflix Content Analytics — Big Data Analytics (BDA) Project

A comprehensive Big Data Analytics (BDA) system for analyzing 8,807 Netflix titles using probabilistic data structures, relational querying via SQLite, statistical visualization with R (ggplot2), an interactive React frontend, and a high-performance FastAPI backend.

---

## 🏛️ System Architecture

- **Data Ingestion & Cleaning**: Python (`src/preprocessing.py`) handles dirty dataset repairs (e.g. rating/duration swaps, whitespace stripping, missing value imputation, date parsing).
- **Relational Storage**: SQLite (`data/netflix_analytics.db`) stores 8,807 cleaned titles in the `titles` table with indexed fields for fast, parameterized catalog queries.
- **Probabilistic Algorithms (BDA)**:
  - **Bloom Filter**: Space-efficient probabilistic set membership testing with 1% false positive rate using double-hashing (SHA-256 and MD5).
  - **Flajolet–Martin (FM)**: Stream cardinality estimation using trailing zero counts, enhanced with 32-trial log-space averaging to achieve ~2.5% relative error.
  - **HyperLogLog (HLL)**: Cardinality estimation with 256 registers ($b=8$) and harmonic mean aggregation.
- **Visualizations**: R 4.6.1 (`src/visualizations.R`) with `ggplot2`, `dplyr`, and `readr` generates 8 publication-quality charts saved to `output/figures/`.
- **Automated Reporting**: ReportLab (`src/report_generator.py`) compiles a structured 10-page PDF report (`output/netflix_report.pdf`).
- **REST API**: FastAPI (`backend/api.py`) exposes analytical summaries, algorithm execution, and SQLite-backed search/filter endpoints.
- **User Interface**: React + Vite (`frontend/`) featuring a Neo-Brutalist dashboard, interactive catalog explorer, live Bloom Filter tester, and PDF report viewer.

---

## 💾 SQLite Database Integration

The SQLite database is located at:
```
data/netflix_analytics.db
```

### Table Schema: `titles`

| Column | Type | Description |
|---|---|---|
| `show_id` | `TEXT PRIMARY KEY` | Unique title identifier (e.g., `s1`, `s2`) |
| `type` | `TEXT NOT NULL` | Content type (`Movie` or `TV Show`) |
| `title` | `TEXT NOT NULL` | Title name |
| `director` | `TEXT` | Director name(s) or `Unknown` |
| `"cast"` | `TEXT` | Cast member list or `Unknown` |
| `country` | `TEXT` | Country of origin or `Unknown` |
| `date_added` | `TEXT` | Date added to Netflix (ISO format `YYYY-MM-DD`) |
| `release_year` | `INTEGER` | Original release year |
| `rating` | `TEXT` | Age rating (`TV-MA`, `PG-13`, `NR`, etc.) |
| `duration` | `TEXT` | Runtime string (e.g., `90 min`, `2 Seasons`) |
| `listed_in` | `TEXT` | Comma-separated genre categories |
| `description` | `TEXT` | Synopsis / plot description |
| `year_added` | `INTEGER` | Parsed calendar year added |
| `month_added` | `INTEGER` | Parsed calendar month added (1–12) |
| `duration_min` | `REAL` | Movie duration in integer minutes |
| `num_seasons` | `REAL` | TV Show duration in integer seasons |

Indexes:
- `idx_titles_type` on `type`
- `idx_titles_release_year` on `release_year`
- `idx_titles_rating` on `rating`

### Idempotency
Records are imported using parameterized `INSERT OR REPLACE INTO titles`, guaranteeing that re-running the database initialization or pipeline updates records safely without creating duplicate rows.

---

## 🚀 Setup and Run Instructions

### 1. Prerequisites
- **Python 3.10+**
- **R 4.6.1** with packages `ggplot2`, `dplyr`, `readr` installed
- **Node.js 18+** & npm (for frontend)

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```
*(Note: `sqlite3` is included natively in Python's standard library).*

### 3. Initialize / Sync the SQLite Database
To independently initialize the database and import the 8,807 cleaned titles:
```bash
python src/database.py
```

### 4. Run the Full Analytics Pipeline
To run the complete pipeline end-to-end (preprocessing, database sync, Bloom Filter, Cardinality estimation, R ggplot2 charts, and PDF report):
```bash
python main.py
```
Outputs:
- SQLite Database: `data/netflix_analytics.db` (8,807 records)
- Cleaned CSV: `output/cleaned_netflix_titles.csv`
- R Figures: `output/figures/*.png` (8 charts)
- PDF Report: `output/netflix_report.pdf`

### 5. Start the Backend API
```bash
uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```
API Documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 6. Start the Frontend Application
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 📡 REST API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | `GET` | Health status of API service |
| `/api/summary` | `GET` | Dataset overview statistics |
| `/api/titles` | `GET` | Parameterized SQLite search and filter with pagination (`search`, `type`, `country`, `genre`, `page`, `limit`) |
| `/api/analytics` | `GET` | Aggregated statistical breakdowns (ratings, genres, release years, duration) |
| `/api/bloom-check` | `GET` | Tests membership for a given title using the Bloom Filter |
| `/api/cardinality` | `GET` | Comparison between exact count, single FM, multi-run FM, and HyperLogLog |
| `/api/report/status` | `GET` | Verification of PDF report readiness and byte size |
| `/api/report` | `GET` | Downloads the generated PDF report |

---

## 🧪 Testing

- **Full Pipeline Verification**: `python main.py`
- **Database Standalone Check**: `python src/database.py`
- **Backend API Check**: Query `/api/titles?search=Stranger+Things` or run `pytest` / test client.
- **Frontend Build**: `cd frontend && npm run build`
