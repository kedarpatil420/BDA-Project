"""
src/database.py
---------------
SQLite database initialization, schema definition, data ingestion,
and parameterized querying for the Netflix Content Analytics project.
"""

import os
import sys
import sqlite3
import math
from typing import Optional, Dict, Any, List
import pandas as pd

# Default paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'netflix_analytics.db')
DEFAULT_CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'netflix_titles.csv')


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Create and return a SQLite database connection with row factory configured.
    """
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Create the 'titles' table and associated indexes if they do not exist.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS titles (
                show_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                director TEXT,
                "cast" TEXT,
                country TEXT,
                date_added TEXT,
                release_year INTEGER,
                rating TEXT,
                duration TEXT,
                listed_in TEXT,
                description TEXT,
                year_added INTEGER,
                month_added INTEGER,
                duration_min REAL,
                num_seasons REAL
            );
        """)
        
        # Indexes for frequent filtering and search
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_titles_type ON titles(type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_titles_release_year ON titles(release_year);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_titles_rating ON titles(rating);")
        conn.commit()


def import_titles(df: pd.DataFrame, db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Import cleaned Netflix DataFrame records into SQLite.
    Uses INSERT OR REPLACE to be idempotent when rerun.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned Netflix records.
    db_path : str
        Path to the SQLite database.

    Returns
    -------
    int
        Number of records inserted / updated.
    """
    init_db(db_path)

    columns = [
        'show_id', 'type', 'title', 'director', 'cast', 'country',
        'date_added', 'release_year', 'rating', 'duration', 'listed_in',
        'description', 'year_added', 'month_added', 'duration_min', 'num_seasons'
    ]

    # Prepare DataFrame with matching columns and handle NaN
    insert_df = df.copy()
    for col in columns:
        if col not in insert_df.columns:
            insert_df[col] = None

    # Replace pandas NaN / NaT / Timestamps for clean SQL insertion
    records = []
    for _, row in insert_df[columns].iterrows():
        rec_vals = []
        for col_name, val in row.items():
            if pd.isna(val):
                rec_vals.append(None)
            elif isinstance(val, pd.Timestamp):
                rec_vals.append(val.strftime('%Y-%m-%d'))
            elif hasattr(val, 'item'):  # numpy scalar conversion
                rec_vals.append(val.item())
            else:
                rec_vals.append(val)
        records.append(tuple(rec_vals))

    quoted_columns = [f'"{c}"' for c in columns]
    insert_sql = f"""
        INSERT OR REPLACE INTO titles (
            {', '.join(quoted_columns)}
        ) VALUES (
            {', '.join(['?'] * len(columns))}
        );
    """

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(insert_sql, records)
        conn.commit()

    return len(records)


def get_titles_count(db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Return total count of rows in the titles table.
    """
    if not os.path.exists(db_path):
        return 0
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM titles;")
        return cursor.fetchone()[0]


def query_titles(
    db_path: str = DEFAULT_DB_PATH,
    search: Optional[str] = None,
    content_type: Optional[str] = None,
    country: Optional[str] = None,
    genre: Optional[str] = None,
    page: int = 1,
    limit: int = 15
) -> Dict[str, Any]:
    """
    Query titles from SQLite using parameterized queries with filtering and pagination.

    Returns
    -------
    dict
        {
            'page': int,
            'limit': int,
            'total_items': int,
            'total_pages': int,
            'items': list of dicts
        }
    """
    where_clauses = ["1=1"]
    params: List[Any] = []

    if search and search.strip():
        where_clauses.append("LOWER(title) LIKE ?")
        params.append(f"%{search.strip().lower()}%")

    if content_type and content_type.strip().lower() != 'all':
        where_clauses.append("LOWER(type) = LOWER(?)")
        params.append(content_type.strip())

    if country and country.strip().lower() != 'all':
        where_clauses.append("LOWER(country) LIKE ?")
        params.append(f"%{country.strip().lower()}%")

    if genre and genre.strip().lower() != 'all':
        where_clauses.append("LOWER(listed_in) LIKE ?")
        params.append(f"%{genre.strip().lower()}%")

    where_str = " AND ".join(where_clauses)

    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Get total matching items
        count_query = f"SELECT COUNT(*) FROM titles WHERE {where_str};"
        cursor.execute(count_query, params)
        total_items = cursor.fetchone()[0]

        total_pages = max(1, math.ceil(total_items / limit))
        page = max(1, page)
        offset = (page - 1) * limit

        # 2. Get paginated rows
        data_query = f"""
            SELECT show_id, type, title, director, "cast", country, date_added,
                   release_year, rating, duration, listed_in, description,
                   year_added, month_added, duration_min, num_seasons
            FROM titles
            WHERE {where_str}
            ORDER BY show_id
            LIMIT ? OFFSET ?;
        """
        cursor.execute(data_query, params + [limit, offset])
        rows = cursor.fetchall()

        items = []
        for r in rows:
            d = dict(r)
            # Normalize None to empty string for textual compatibility with frontend expectations
            for k in ['director', 'cast', 'country', 'rating', 'duration', 'listed_in', 'description']:
                if d.get(k) is None:
                    d[k] = ''
            items.append(d)

    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "items": items
    }


if __name__ == '__main__':
    # Standalone execution: load data, clean it, and import into SQLite
    from src.preprocessing import load_and_clean
    print(f"Initializing SQLite database at: {DEFAULT_DB_PATH}")
    df_clean = load_and_clean(DEFAULT_CSV_PATH)
    count = import_titles(df_clean, DEFAULT_DB_PATH)
    print(f"Successfully imported {count:,} titles into SQLite.")
    total = get_titles_count(DEFAULT_DB_PATH)
    print(f"Total records in titles table: {total:,}")
    
    # Test sample search
    sample = query_titles(DEFAULT_DB_PATH, search="Stranger Things", limit=5)
    print(f"Sample search ('Stranger Things'): found {sample['total_items']} items.")
    for item in sample['items']:
        print(f"  - [{item['type']}] {item['title']} ({item['release_year']})")
