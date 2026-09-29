"""
src/preprocessing.py
--------------------
Data loading, cleaning and feature engineering for the Netflix dataset.

Key cleaning steps (based on dataset inspection):
  1. Fix 3 rows where duration values appear in the 'rating' column (known data error).
  2. Strip whitespace from all string columns.
  3. Fill missing categorical values with 'Unknown' or 'NR'.
  4. Parse 'date_added' string -> datetime, extract year_added and month_added.
  5. Parse 'duration' text -> numeric columns: duration_min (Movies), num_seasons (TV Shows).
  6. Drop the 3 rows that still have null duration after the fix.
"""

import pandas as pd
import numpy as np


def load_and_clean(filepath: str = 'data/netflix_titles.csv') -> pd.DataFrame:
    """
    Load the Netflix CSV and return a fully cleaned DataFrame.

    Parameters
    ----------
    filepath : str
        Path to netflix_titles.csv.

    Returns
    -------
    pd.DataFrame
        Cleaned and enriched DataFrame ready for analysis.
    """

    # ------------------------------------------------------------------ #
    # 1. Load raw data
    # ------------------------------------------------------------------ #
    df = pd.read_csv(filepath)
    original_shape = df.shape
    print(f"  Loaded {original_shape[0]:,} rows × {original_shape[1]} columns")

    # ------------------------------------------------------------------ #
    # 2. Fix the 3 swapped rating / duration rows
    #    (Known dataset bug: rows where duration values like '74 min'
    #     ended up in the 'rating' column.)
    # ------------------------------------------------------------------ #
    swapped_mask = df['rating'].isin(['74 min', '84 min', '66 min'])
    if swapped_mask.sum() > 0:
        df.loc[swapped_mask, 'duration'] = df.loc[swapped_mask, 'rating']
        df.loc[swapped_mask, 'rating']   = np.nan
        print(f"  Fixed {swapped_mask.sum()} swapped rating/duration rows")

    # ------------------------------------------------------------------ #
    # 3. Strip leading/trailing whitespace from all string columns
    # ------------------------------------------------------------------ #
    str_cols = df.select_dtypes(include='object').columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    # ------------------------------------------------------------------ #
    # 4. Fill missing values
    # ------------------------------------------------------------------ #
    df['director'] = df['director'].fillna('Unknown')
    df['cast']     = df['cast'].fillna('Unknown')
    df['country']  = df['country'].fillna('Unknown')
    df['rating']   = df['rating'].fillna('NR')

    # ------------------------------------------------------------------ #
    # 5. Parse date_added (stored as plain English string) -> datetime
    # ------------------------------------------------------------------ #
    df['date_added']  = pd.to_datetime(df['date_added'], format='%B %d, %Y', errors='coerce')
    df['year_added']  = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month

    # ------------------------------------------------------------------ #
    # 6. Parse 'duration' into two numeric columns
    #    Movies  : "90 min"    -> duration_min = 90
    #    TV Shows: "2 Seasons" -> num_seasons  = 2
    # ------------------------------------------------------------------ #
    # Extract the leading integer from duration text
    duration_int = df['duration'].str.extract(r'(\d+)').astype(float)

    movie_mask   = df['type'] == 'Movie'
    tv_mask      = df['type'] == 'TV Show'

    df['duration_min'] = np.nan
    df['num_seasons']  = np.nan

    df.loc[movie_mask, 'duration_min'] = duration_int.loc[movie_mask, 0]
    df.loc[tv_mask,  'num_seasons']    = duration_int.loc[tv_mask,   0]

    # ------------------------------------------------------------------ #
    # 7. Drop the few rows that still have null duration
    # ------------------------------------------------------------------ #
    before = len(df)
    df = df.dropna(subset=['duration']).reset_index(drop=True)
    dropped = before - len(df)
    if dropped:
        print(f"  Dropped {dropped} row(s) with unparseable duration")

    print(f"  Clean dataset: {len(df):,} rows remaining")
    return df


def get_genres_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Explode the comma-separated 'listed_in' column into individual genre rows.
    Useful for per-genre frequency analysis.

    Returns
    -------
    pd.DataFrame
        Long-form DataFrame with one row per (show_id, genre) pair.
    """
    genres = df[['show_id', 'type', 'title', 'listed_in']].copy()
    genres['genre'] = genres['listed_in'].str.split(',')
    genres = genres.explode('genre')
    genres['genre'] = genres['genre'].str.strip()
    return genres.reset_index(drop=True)


def dataset_summary(df: pd.DataFrame) -> dict:
    """
    Return a dict of summary statistics used in the PDF report.
    """
    return {
        'total_rows'    : len(df),
        'total_cols'    : df.shape[1],
        'num_movies'    : int((df['type'] == 'Movie').sum()),
        'num_tv'        : int((df['type'] == 'TV Show').sum()),
        'min_year'      : int(df['release_year'].min()),
        'max_year'      : int(df['release_year'].max()),
        'num_countries' : int(df['country'].nunique()),
        'num_ratings'   : int(df['rating'].nunique()),
        'missing_before': {
            'director'   : 2634,
            'cast'       : 825,
            'country'    : 831,
            'date_added' : 10,
            'rating'     : 4,
            'duration'   : 3,
        },
    }
