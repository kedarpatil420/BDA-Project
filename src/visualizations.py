"""
src/visualizations.py
----------------------
Generate and save all publication-quality figures for the Netflix BDA project.

Eight figures are produced:
  fig1 – Movies vs TV Shows  (pie chart)
  fig2 – Top 15 Countries    (horizontal bar)
  fig3 – Top 15 Genres       (horizontal bar)
  fig4 – Rating Distribution (bar chart)
  fig5 – Content by Release Year  (line chart, 1990–2021)
  fig6 – Content Added Over Time  (bar chart, by year_added)
  fig7 – Movie Duration Distribution (histogram + KDE)
  fig8 – TV Show Seasons Distribution (bar chart)

All figures are saved to output/figures/ at 150 DPI.
A consistent seaborn whitegrid style is applied throughout.
"""

import os
import warnings
import matplotlib
matplotlib.use('Agg')           # non-interactive backend — must be before pyplot
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np

warnings.filterwarnings('ignore')

# ------------------------------------------------------------------ #
# Global style
# ------------------------------------------------------------------ #
sns.set_theme(style='whitegrid', palette='muted', font_scale=1.05)
FIGSIZE   = (10, 5)
DPI       = 150
TITLE_FS  = 14
LABEL_FS  = 11
TICK_FS   = 9

# Colour palette used across bar charts (Seaborn muted blue)
BAR_COLOR  = '#4C72B0'
LINE_COLOR = '#DD8452'


def _save(fig, name: str, figures_dir: str):
    """Save figure and close it."""
    path = os.path.join(figures_dir, name)
    fig.savefig(path, dpi=DPI, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# ======================================================================== #
#  Figure 1 – Movies vs TV Shows
# ======================================================================== #

def fig1_content_type(type_split, figures_dir: str) -> str:
    """Pie chart showing the Movies/TV Show split."""
    labels = type_split.index.tolist()
    sizes  = type_split.values.tolist()
    colors = ['#4C72B0', '#DD8452']
    explode = (0.04, 0)

    fig, ax = plt.subplots(figsize=(7, 5))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%',
        startangle=140, colors=colors, explode=explode,
        wedgeprops=dict(linewidth=1.2, edgecolor='white'),
        textprops=dict(fontsize=LABEL_FS),
    )
    for at in autotexts:
        at.set_fontsize(LABEL_FS)
        at.set_fontweight('bold')

    ax.set_title('Netflix Content: Movies vs TV Shows', fontsize=TITLE_FS, fontweight='bold', pad=14)

    # Annotation with counts
    legend_labels = [f"{l}: {c:,}" for l, c in zip(labels, sizes)]
    ax.legend(wedges, legend_labels, loc='lower right', fontsize=TICK_FS)

    fig.tight_layout()
    return _save(fig, 'fig1_content_type.png', figures_dir)


# ======================================================================== #
#  Figure 2 – Top 15 Countries
# ======================================================================== #

def fig2_top_countries(countries, figures_dir: str) -> str:
    """Horizontal bar chart of the top 15 content-producing countries."""
    data = countries.sort_values()   # ascending so largest is at top

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(data.index, data.values, color=BAR_COLOR, edgecolor='white', linewidth=0.5)

    # Value labels on bars
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 15, bar.get_y() + bar.get_height() / 2,
                f'{int(w):,}', va='center', ha='left', fontsize=TICK_FS)

    ax.set_xlabel('Number of Titles', fontsize=LABEL_FS)
    ax.set_title('Top 15 Countries by Number of Titles', fontsize=TITLE_FS, fontweight='bold')
    ax.set_xlim(0, data.max() * 1.15)
    ax.tick_params(axis='y', labelsize=TICK_FS)
    ax.tick_params(axis='x', labelsize=TICK_FS)
    sns.despine(left=True, bottom=True)

    fig.tight_layout()
    return _save(fig, 'fig2_top_countries.png', figures_dir)


# ======================================================================== #
#  Figure 3 – Top 15 Genres
# ======================================================================== #

def fig3_top_genres(genres, figures_dir: str) -> str:
    """Horizontal bar chart of the top 15 individual genre tags."""
    data = genres.sort_values()   # ascending so largest is at top

    palette = sns.color_palette('muted', len(data))

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(data.index, data.values, color=palette, edgecolor='white', linewidth=0.5)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 8, bar.get_y() + bar.get_height() / 2,
                f'{int(w):,}', va='center', ha='left', fontsize=TICK_FS)

    ax.set_xlabel('Number of Titles', fontsize=LABEL_FS)
    ax.set_title('Top 15 Genre Tags on Netflix', fontsize=TITLE_FS, fontweight='bold')
    ax.set_xlim(0, data.max() * 1.18)
    ax.tick_params(axis='y', labelsize=TICK_FS)
    ax.tick_params(axis='x', labelsize=TICK_FS)
    sns.despine(left=True, bottom=True)

    fig.tight_layout()
    return _save(fig, 'fig3_top_genres.png', figures_dir)


# ======================================================================== #
#  Figure 4 – Rating Distribution
# ======================================================================== #

def fig4_rating_distribution(ratings, figures_dir: str) -> str:
    """Bar chart of content rating frequencies, sorted by count."""
    # Filter out very low-frequency ratings for clarity
    data = ratings[ratings > 2].sort_values(ascending=False)

    palette = sns.color_palette('Blues_d', len(data))[::-1]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(data.index, data.values, color=palette, edgecolor='white', linewidth=0.5)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 20,
                f'{int(h):,}', ha='center', va='bottom', fontsize=TICK_FS)

    ax.set_xlabel('Content Rating', fontsize=LABEL_FS)
    ax.set_ylabel('Number of Titles', fontsize=LABEL_FS)
    ax.set_title('Distribution of Content Ratings', fontsize=TITLE_FS, fontweight='bold')
    ax.tick_params(axis='x', labelsize=TICK_FS)
    ax.tick_params(axis='y', labelsize=TICK_FS)
    ax.set_ylim(0, data.max() * 1.12)
    sns.despine()

    fig.tight_layout()
    return _save(fig, 'fig4_rating_distribution.png', figures_dir)


# ======================================================================== #
#  Figure 5 – Content by Release Year
# ======================================================================== #

def fig5_release_year(by_year, figures_dir: str) -> str:
    """Line chart: number of titles by original release year (1990–2021)."""
    fig, ax = plt.subplots(figsize=FIGSIZE)

    ax.plot(by_year.index, by_year.values, color=BAR_COLOR,
            linewidth=2, marker='o', markersize=3)
    ax.fill_between(by_year.index, by_year.values, alpha=0.15, color=BAR_COLOR)

    ax.set_xlabel('Release Year', fontsize=LABEL_FS)
    ax.set_ylabel('Number of Titles', fontsize=LABEL_FS)
    ax.set_title('Netflix Titles by Original Release Year (1990–2021)', fontsize=TITLE_FS, fontweight='bold')
    ax.tick_params(axis='x', labelsize=TICK_FS, rotation=45)
    ax.tick_params(axis='y', labelsize=TICK_FS)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    sns.despine()

    fig.tight_layout()
    return _save(fig, 'fig5_release_year.png', figures_dir)


# ======================================================================== #
#  Figure 6 – Content Added Over Time
# ======================================================================== #

def fig6_added_over_time(added_over_time, figures_dir: str) -> str:
    """Bar chart: titles added to Netflix per calendar year."""
    fig, ax = plt.subplots(figsize=FIGSIZE)

    years  = added_over_time.index.astype(int)
    counts = added_over_time.values

    palette = sns.color_palette('Blues_d', len(years))[::-1]
    bars = ax.bar(years, counts, color=palette, edgecolor='white', linewidth=0.5, width=0.7)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 10,
                f'{int(h):,}', ha='center', va='bottom', fontsize=7)

    ax.set_xlabel('Year', fontsize=LABEL_FS)
    ax.set_ylabel('Titles Added', fontsize=LABEL_FS)
    ax.set_title('Content Added to Netflix Over Time (by Year)', fontsize=TITLE_FS, fontweight='bold')
    ax.tick_params(axis='x', labelsize=TICK_FS, rotation=45)
    ax.tick_params(axis='y', labelsize=TICK_FS)
    ax.set_ylim(0, counts.max() * 1.15)
    sns.despine()

    fig.tight_layout()
    return _save(fig, 'fig6_added_over_time.png', figures_dir)


# ======================================================================== #
#  Figure 7 – Movie Duration Distribution
# ======================================================================== #

def fig7_movie_duration(movie_dur_stats: dict, figures_dir: str) -> str:
    """Histogram + KDE curve for movie runtime in minutes."""
    series = movie_dur_stats['series']
    mean   = movie_dur_stats['mean']
    median = movie_dur_stats['median']

    fig, ax = plt.subplots(figsize=FIGSIZE)

    # Histogram
    ax.hist(series, bins=40, color=BAR_COLOR, alpha=0.7, edgecolor='white', linewidth=0.4)

    # KDE line
    from scipy.stats import gaussian_kde
    kde_x = np.linspace(series.min(), series.max(), 300)
    kde   = gaussian_kde(series, bw_method=0.3)
    # Scale KDE to histogram height
    bin_width = (series.max() - series.min()) / 40
    scale = len(series) * bin_width
    ax2 = ax.twinx()
    ax2.plot(kde_x, kde(kde_x), color=LINE_COLOR, linewidth=2, label='KDE')
    ax2.set_ylabel('Density', fontsize=LABEL_FS, color=LINE_COLOR)
    ax2.tick_params(axis='y', labelcolor=LINE_COLOR, labelsize=TICK_FS)
    ax2.set_ylim(bottom=0)

    # Mean / median lines
    ax.axvline(mean,   color='red',    linestyle='--', linewidth=1.5, label=f'Mean: {mean} min')
    ax.axvline(median, color='green',  linestyle=':',  linewidth=1.5, label=f'Median: {median} min')

    ax.set_xlabel('Duration (minutes)', fontsize=LABEL_FS)
    ax.set_ylabel('Number of Movies', fontsize=LABEL_FS)
    ax.set_title('Movie Duration Distribution', fontsize=TITLE_FS, fontweight='bold')
    ax.tick_params(axis='both', labelsize=TICK_FS)

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=TICK_FS, loc='upper right')

    sns.despine()
    fig.tight_layout()
    return _save(fig, 'fig7_movie_duration.png', figures_dir)


# ======================================================================== #
#  Figure 8 – TV Show Seasons Distribution
# ======================================================================== #

def fig8_tv_seasons(tv_seasons, figures_dir: str) -> str:
    """Bar chart of TV show season counts."""
    data = tv_seasons

    palette = sns.color_palette('muted', len(data))

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(data.index.astype(int), data.values,
                  color=palette, edgecolor='white', linewidth=0.5, width=0.7)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 5,
                f'{int(h):,}', ha='center', va='bottom', fontsize=TICK_FS)

    ax.set_xlabel('Number of Seasons', fontsize=LABEL_FS)
    ax.set_ylabel('Number of TV Shows', fontsize=LABEL_FS)
    ax.set_title('TV Show Seasons Distribution', fontsize=TITLE_FS, fontweight='bold')
    ax.set_xticks(data.index.astype(int))
    ax.tick_params(axis='both', labelsize=TICK_FS)
    ax.set_ylim(0, data.max() * 1.12)
    sns.despine()

    fig.tight_layout()
    return _save(fig, 'fig8_tv_seasons.png', figures_dir)


# ======================================================================== #
#  Master function
# ======================================================================== #

def generate_all(analysis: dict, figures_dir: str) -> dict:
    """
    Generate all 8 figures and return a dict mapping figure names to file paths.

    Parameters
    ----------
    analysis : dict
        Output of analysis.run_all(df).
    figures_dir : str
        Directory where PNG files will be saved.

    Returns
    -------
    dict
        {figure_key: absolute_file_path}
    """
    os.makedirs(figures_dir, exist_ok=True)

    paths = {}
    paths['fig1'] = fig1_content_type(analysis['type_split'],      figures_dir)
    paths['fig2'] = fig2_top_countries(analysis['countries'],       figures_dir)
    paths['fig3'] = fig3_top_genres(analysis['genres'],             figures_dir)
    paths['fig4'] = fig4_rating_distribution(analysis['ratings'],   figures_dir)
    paths['fig5'] = fig5_release_year(analysis['by_year'],          figures_dir)
    paths['fig6'] = fig6_added_over_time(analysis['added_over_time'], figures_dir)
    paths['fig7'] = fig7_movie_duration(analysis['movie_duration'], figures_dir)
    paths['fig8'] = fig8_tv_seasons(analysis['tv_seasons'],         figures_dir)

    return paths
