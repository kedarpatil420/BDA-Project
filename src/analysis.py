"""
src/analysis.py
---------------
Statistical and content analysis functions for the Netflix dataset.

Each function takes the cleaned DataFrame and returns either a
pandas Series/DataFrame or a dict that can be passed directly
to the visualisation and report-generation modules.
"""

import pandas as pd
import numpy as np


def content_type_split(df: pd.DataFrame) -> pd.Series:
    """
    Count of Movies vs TV Shows.

    Returns
    -------
    pd.Series
        Index: ['Movie', 'TV Show']   Values: counts
    """
    return df['type'].value_counts()


def content_by_release_year(df: pd.DataFrame,
                             start_year: int = 1990) -> pd.Series:
    """
    Number of titles by release year, from start_year onwards.
    Older titles are filtered to keep the chart readable.

    Returns
    -------
    pd.Series
        Index: year (int)   Values: count
    """
    filtered = df[df['release_year'] >= start_year]
    return filtered.groupby('release_year').size().sort_index()


def content_added_over_time(df: pd.DataFrame) -> pd.Series:
    """
    Number of titles added to Netflix each calendar year.

    Returns
    -------
    pd.Series
        Index: year_added (int)   Values: count
    """
    yearly = (
        df.dropna(subset=['year_added'])
          .groupby('year_added')
          .size()
          .sort_index()
    )
    # Keep only years with meaningful data (Netflix started adding in 2008)
    return yearly[yearly.index >= 2008].astype(int)


def top_countries(df: pd.DataFrame, n: int = 15) -> pd.Series:
    """
    Top n countries by number of titles, excluding 'Unknown'.

    Returns
    -------
    pd.Series
        Index: country name   Values: count  (sorted descending)
    """
    filtered = df[df['country'] != 'Unknown']
    return filtered['country'].value_counts().head(n)


def top_genres(df: pd.DataFrame, n: int = 15) -> pd.Series:
    """
    Top n individual genre tags after exploding the comma-separated
    'listed_in' column.

    Returns
    -------
    pd.Series
        Index: genre string   Values: count  (sorted descending)
    """
    all_genres = (
        df['listed_in']
          .dropna()
          .str.split(',')
          .explode()
          .str.strip()
    )
    return all_genres.value_counts().head(n)


def rating_distribution(df: pd.DataFrame) -> pd.Series:
    """
    Frequency of each content rating, excluding 'NR'/'UR' noise if desired.

    Returns
    -------
    pd.Series
        Index: rating string   Values: count  (sorted descending)
    """
    # Include all ratings; 'NR'/'UR' are legitimate categories
    return df['rating'].value_counts()


def movie_duration_stats(df: pd.DataFrame) -> dict:
    """
    Descriptive statistics and raw values for movie runtimes.

    Returns
    -------
    dict
        'series': pd.Series of duration_min for all Movies
        'mean', 'median', 'std', 'min', 'max': float statistics
    """
    movies = df[(df['type'] == 'Movie') & df['duration_min'].notna()]
    s = movies['duration_min']
    return {
        'series': s,
        'mean'  : round(s.mean(), 1),
        'median': round(s.median(), 1),
        'std'   : round(s.std(), 1),
        'min'   : int(s.min()),
        'max'   : int(s.max()),
    }


def tv_seasons_stats(df: pd.DataFrame) -> pd.Series:
    """
    Distribution of the number of seasons across TV Shows.

    Returns
    -------
    pd.Series
        Index: num_seasons (int)   Values: count  (sorted by season count)
    """
    tv = df[(df['type'] == 'TV Show') & df['num_seasons'].notna()]
    dist = tv['num_seasons'].value_counts().sort_index()
    # Cap at 15 seasons for readability (very few shows exceed this)
    return dist[dist.index <= 15]


def top_directors(df: pd.DataFrame, n: int = 10) -> pd.Series:
    """
    Top n most prolific directors, excluding 'Unknown'.

    Returns
    -------
    pd.Series
        Index: director name   Values: title count  (sorted descending)
    """
    filtered = df[df['director'] != 'Unknown']
    return filtered['director'].value_counts().head(n)


def run_all(df: pd.DataFrame) -> dict:
    """
    Run every analysis function and bundle results into a single dict.
    Called by main.py so values can be shared across vis and report modules.
    """
    return {
        'type_split'    : content_type_split(df),
        'by_year'       : content_by_release_year(df),
        'added_over_time': content_added_over_time(df),
        'countries'     : top_countries(df),
        'genres'        : top_genres(df),
        'ratings'       : rating_distribution(df),
        'movie_duration': movie_duration_stats(df),
        'tv_seasons'    : tv_seasons_stats(df),
        'directors'     : top_directors(df),
    }
