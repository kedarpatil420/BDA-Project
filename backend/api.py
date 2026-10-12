import os
import sys
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Ensure root directory is in sys.path so we can import src.*
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.preprocessing import load_and_clean, dataset_summary
from src.bloom_filter import BloomFilter
from src.flajolet_martin import run_cardinality_comparison
from src.analysis import run_all as run_analysis
from src.database import DEFAULT_DB_PATH, init_db, import_titles, query_titles, get_titles_count

app = FastAPI(
    title="Netflix BDA Analytics API",
    description="Backend API for Netflix Content Analytics using Bloom Filter and Flajolet-Martin Algorithm",
    version="1.0.0"
)

# Enable CORS for local development (React Vite usually runs on http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(BASE_DIR, 'data', 'netflix_titles.csv')
DB_PATH = DEFAULT_DB_PATH
REPORT_PATH = os.path.join(BASE_DIR, 'output', 'netflix_report.pdf')

# Global cache for preprocessed data and models
data_cache = {
    "df": None,
    "titles": None,
    "summary": None,
    "analysis": None,
    "bloom_filter": None,
    "cardinality": None
}

def get_data():
    if data_cache["df"] is None:
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
        df = load_and_clean(DATA_PATH)
        titles = df['title'].tolist()
        summary = dataset_summary(df)
        analysis_data = run_analysis(df)
        
        # Build Bloom Filter with 1% target FPR
        bf = BloomFilter(n=len(titles), false_positive_rate=0.01)
        for t in titles:
            bf.add(t)
            
        # Compute Cardinality comparison (runs actual FM single, multi, and HLL)
        cardinality_data = run_cardinality_comparison(titles)
        
        # Ensure SQLite database is initialized and populated with cleaned data
        if get_titles_count(DB_PATH) == 0:
            import_titles(df, DB_PATH)
        
        data_cache["df"] = df
        data_cache["titles"] = titles
        data_cache["summary"] = summary
        data_cache["analysis"] = analysis_data
        data_cache["bloom_filter"] = bf
        data_cache["cardinality"] = cardinality_data
        
    return data_cache

@app.on_event("startup")
def startup_event():
    # Pre-load data and compute algorithms on startup
    get_data()

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Netflix BDA API is operational"}

@app.get("/api/summary")
def get_summary():
    data = get_data()
    summary = data["summary"]
    df = data["df"]
    
    unique_titles_count = int(df['title'].nunique())
    
    return {
        "total_titles": summary["total_rows"],
        "num_movies": summary["num_movies"],
        "num_tv_shows": summary["num_tv"],
        "unique_titles": unique_titles_count,
        "total_columns": summary["total_cols"],
        "min_year": summary["min_year"],
        "max_year": summary["max_year"],
        "num_countries": summary["num_countries"],
        "num_ratings": summary["num_ratings"]
    }

@app.get("/api/analytics")
def get_analytics():
    data = get_data()
    analysis = data["analysis"]
    
    # Format type split
    type_split = [
        {"name": k, "value": int(v)}
        for k, v in analysis["type_split"].items()
    ]
    
    # Format top countries
    top_countries = [
        {"country": k, "count": int(v)}
        for k, v in analysis["countries"].items()
    ]
    
    # Format top genres
    top_genres = [
        {"genre": k, "count": int(v)}
        for k, v in analysis["genres"].items()
    ]
    
    # Format release year distribution
    by_year = [
        {"year": int(k), "count": int(v)}
        for k, v in analysis["by_year"].items()
    ]
    
    # Format content added over time
    added_over_time = [
        {"year": int(k), "count": int(v)}
        for k, v in analysis["added_over_time"].items()
    ]
    
    # Ratings distribution
    ratings = [
        {"rating": str(k), "count": int(v)}
        for k, v in analysis["ratings"].items()
    ]
    
    # Movie duration statistics
    dur = analysis["movie_duration"]
    duration_stats = {
        "mean": dur["mean"],
        "median": dur["median"],
        "std": dur["std"],
        "min": dur["min"],
        "max": dur["max"]
    }
    
    return {
        "type_split": type_split,
        "top_countries": top_countries,
        "top_genres": top_genres,
        "release_year_distribution": by_year,
        "added_over_time": added_over_time,
        "ratings": ratings,
        "movie_duration_stats": duration_stats
    }

@app.get("/api/cardinality")
def get_cardinality():
    data = get_data()
    card = data["cardinality"]
    return {
        "actual": card["actual"],
        "fm_single": card["fm_single"],
        "fm_single_error": card["fm_single_error"],
        "fm_multi": card["fm_multi"],
        "fm_multi_error": card["fm_multi_error"],
        "hll": card["hll"],
        "hll_error": card["hll_error"],
        "methods": [
            {
                "method": "Exact Count",
                "estimate": card["actual"],
                "error_pct": 0.0,
                "description": "True distinct title count computed via exact set cardinality (ground truth)."
            },
            {
                "method": "Flajolet-Martin (Single Run)",
                "estimate": card["fm_single"],
                "error_pct": card["fm_single_error"],
                "description": "Standard FM using maximum trailing zeros R and scaling factor phi = 0.7735 * 2^R. Subject to high discrete variance."
            },
            {
                "method": "Flajolet-Martin (Multi-Run)",
                "estimate": card["fm_multi"],
                "error_pct": card["fm_multi_error"],
                "description": "32 independent hash trials grouped into batches of 8 with log-space averaging and median selection to eliminate exponential outlier bias."
            },
            {
                "method": "HyperLogLog (HLL)",
                "estimate": card["hll"],
                "error_pct": card["hll_error"],
                "description": "Uses 256 registers (b=8) with harmonic mean aggregation and linear counting bias corrections."
            }
        ]
    }

@app.get("/api/bloom-check")
def bloom_check(title: str = Query(..., description="Netflix title to check membership for")):
    clean_title = title.strip()
    if not clean_title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
        
    data = get_data()
    bf = data["bloom_filter"]
    is_present = bf.check(clean_title)
    
    # Check exact dataset membership to provide full educational feedback for demonstration
    exact_present = clean_title in set(data["titles"])
    
    return {
        "title": clean_title,
        "bloom_result": is_present,
        "membership_status": "PROBABLY IN SET" if is_present else "DEFINITELY NOT IN SET",
        "exact_in_dataset": exact_present,
        "is_false_positive": is_present and not exact_present,
        "explanation": (
            "The Bloom Filter returned positive (all k hashed bit positions are 1). "
            "Because Bloom filters never produce false negatives, any title present in Netflix will always return positive. "
            "However, due to hash collisions, there is a theoretical ~1% probability of false positives."
            if is_present else
            "The Bloom Filter returned negative (at least one hashed bit position is 0). "
            "Because Bloom filters guarantee zero false negatives, this title is DEFINITELY NOT in the Netflix dataset."
        ),
        "filter_info": bf.info()
    }

@app.get("/api/titles")
def get_titles(
    search: Optional[str] = Query(None, description="Search keyword in title"),
    type: Optional[str] = Query(None, description="Filter by type: Movie or TV Show"),
    country: Optional[str] = Query(None, description="Filter by country"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(15, ge=1, le=100, description="Items per page")
):
    get_data()
    return query_titles(
        db_path=DB_PATH,
        search=search,
        content_type=type,
        country=country,
        genre=genre,
        page=page,
        limit=limit
    )

@app.get("/api/report/status")
def report_status():
    exists = os.path.exists(REPORT_PATH)
    file_size = os.path.getsize(REPORT_PATH) if exists else 0
    return {
        "available": exists,
        "filename": "netflix_report.pdf",
        "size_bytes": file_size
    }

@app.head("/api/report")
@app.get("/api/report")
def download_report():
    if not os.path.exists(REPORT_PATH):
        raise HTTPException(
            status_code=404, 
            detail="PDF report has not been generated yet. Please run 'python main.py' to generate it."
        )
    return FileResponse(
        path=REPORT_PATH,
        filename="netflix_report.pdf",
        media_type="application/pdf"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api:app", host="127.0.0.1", port=8000, reload=True)
