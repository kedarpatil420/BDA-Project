"""
main.py
-------
Netflix Content Analytics Using Bloom Filter and Flajolet-Martin Algorithm
BDA Mini-Project — Single entry point.

Run:
    python main.py

Output:
    output/figures/   — 8 PNG visualisations
    output/netflix_report.pdf — complete automated PDF report
"""

import os
import sys
import subprocess

# ------------------------------------------------------------------ #
# Ensure src/ is importable
# ------------------------------------------------------------------ #
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.preprocessing   import load_and_clean, dataset_summary
from src.bloom_filter    import run_bloom_filter_demo
from src.flajolet_martin import run_cardinality_comparison
from src.analysis        import run_all as run_analysis
from src.report_generator import generate_report
from src.database        import DEFAULT_DB_PATH, import_titles

# ------------------------------------------------------------------ #
# Paths
# ------------------------------------------------------------------ #
DATA_PATH    = os.path.join(PROJECT_ROOT, 'data', 'netflix_titles.csv')
DB_PATH      = DEFAULT_DB_PATH
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, 'output')
FIGURES_DIR  = os.path.join(OUTPUT_DIR, 'figures')
REPORT_PATH  = os.path.join(OUTPUT_DIR, 'netflix_report.pdf')
CLEANED_DATA_PATH = os.path.join(OUTPUT_DIR, 'cleaned_netflix_titles.csv')
RSCRIPT_PATH = r"C:/Program Files/R/R-4.6.1/bin/Rscript.exe"



def print_section(n: int, title: str):
    print(f'\n[{n}/6] {title}')
    print('      ' + '-' * (len(title) + 4))


def main():
    print('=' * 60)
    print('  Netflix Content Analytics - BDA Mini-Project')
    print('=' * 60)

    os.makedirs(FIGURES_DIR, exist_ok=True)

    # ---------------------------------------------------------------- #
    # Step 1 — Preprocessing
    # ---------------------------------------------------------------- #
    print_section(1, 'Preprocessing data')
    df = load_and_clean(DATA_PATH)
    summary = dataset_summary(df)

    # Initialize / update SQLite database with cleaned dataset
    imported = import_titles(df, DB_PATH)
    print(f"  SQLite database : {DB_PATH} ({imported:,} records synced)")

    # ---------------------------------------------------------------- #
    # Step 2 — Bloom Filter
    # ---------------------------------------------------------------- #
    print_section(2, 'Running Bloom Filter')
    titles = df['title'].tolist()
    bf_results = run_bloom_filter_demo(titles)

    info = bf_results['filter_info']
    print(f"  Bit array size  : {info['bit_array_size_bits']:,} bits  "
          f"({info['bit_array_size_bytes']:,} bytes)")
    print(f"  Hash functions  : {info['num_hash_functions']}")
    print(f"  Items inserted  : {info['items_inserted']:,}")
    print(f"  Target FPR      : {info['target_fpr_pct']} %")
    print(f"  Actual FPR      : {info['actual_fpr_pct']} %")
    print()
    print('  Known title tests (expected: True / Present):')
    for title, result in bf_results['known_results']:
        status = 'PRESENT [OK]' if result else 'ABSENT  [MISS]'
        print(f"    {status}  {title}")
    print('  Unknown title tests (expected: False / Absent):')
    for title, result in bf_results['unknown_results']:
        status = 'PRESENT [FP]' if result else 'ABSENT  [OK]'
        print(f"    {status}  {title}")

    # ---------------------------------------------------------------- #
    # Step 3 — Flajolet-Martin & HyperLogLog
    # ---------------------------------------------------------------- #
    print_section(3, 'Cardinality estimation (FM + HyperLogLog)')
    fm_results = run_cardinality_comparison(titles)

    print(f"  Actual unique titles    : {fm_results['actual']:,}")
    print(f"  FM  Single Run estimate : {fm_results['fm_single']:,}  "
          f"(error: {fm_results['fm_single_error']} %)")
    print(f"  FM  Multi-Run estimate  : {fm_results['fm_multi']:,}  "
          f"(error: {fm_results['fm_multi_error']} %)")
    print(f"  HyperLogLog estimate    : {fm_results['hll']:,}  "
          f"(error: {fm_results['hll_error']} %)")

    # ---------------------------------------------------------------- #
    # Step 4 — Content Analysis
    # ---------------------------------------------------------------- #
    print_section(4, 'Content analysis')
    analysis = run_analysis(df)

    ts = analysis['type_split']
    print(f"  Movies   : {int(ts.get('Movie',   0)):,}")
    print(f"  TV Shows : {int(ts.get('TV Show', 0)):,}")
    print(f"  Top country : {analysis['countries'].index[0]}  "
          f"({int(analysis['countries'].iloc[0]):,} titles)")
    print(f"  Top genre   : {analysis['genres'].index[0]}  "
          f"({int(analysis['genres'].iloc[0]):,} titles)")
    md = analysis['movie_duration']
    print(f"  Movie duration — mean: {md['mean']} min, median: {md['median']} min")

    # ---------------------------------------------------------------- #
    # Step 5 — Visualisations (via R / ggplot2)
    # ---------------------------------------------------------------- #
    print_section(5, 'Generating visualisations (R / ggplot2)')
    
    # Save cleaned dataset for R to consume
    df.to_csv(CLEANED_DATA_PATH, index=False)
    print(f"  Exported cleaned dataset for R: {CLEANED_DATA_PATH}")

    r_script_path = os.path.join('src', 'visualizations.R')
    if not os.path.exists(RSCRIPT_PATH):
        raise FileNotFoundError(f"Rscript executable not found at: {RSCRIPT_PATH}")
    if not os.path.exists(r_script_path):
        raise FileNotFoundError(f"R visualization script not found at: {r_script_path}")

    cmd = [
        RSCRIPT_PATH,
        r_script_path,
        CLEANED_DATA_PATH,
        FIGURES_DIR
    ]

    try:
        proc = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        if proc.stdout:
            for line in proc.stdout.strip().splitlines():
                print(f"  [R] {line}")
    except subprocess.CalledProcessError as exc:
        print(f"\n[ERROR] R script execution failed with exit code {exc.returncode}!")
        if exc.stdout:
            print(f"[R stdout]:\n{exc.stdout}")
        if exc.stderr:
            print(f"[R stderr]:\n{exc.stderr}", file=sys.stderr)
        raise RuntimeError(f"Chart generation failed in R script: {exc}") from exc

    fig_names = [
        ('fig1', 'fig1_content_type.png'),
        ('fig2', 'fig2_top_countries.png'),
        ('fig3', 'fig3_top_genres.png'),
        ('fig4', 'fig4_rating_distribution.png'),
        ('fig5', 'fig5_release_year.png'),
        ('fig6', 'fig6_added_over_time.png'),
        ('fig7', 'fig7_movie_duration.png'),
        ('fig8', 'fig8_tv_seasons.png'),
    ]
    fig_paths = {}
    for key, filename in fig_names:
        p = os.path.join(FIGURES_DIR, filename)
        if not os.path.exists(p):
            raise FileNotFoundError(f"Expected generated figure missing: {p}")
        fig_paths[key] = p

    print(f"  {len(fig_paths)} figures verified in {FIGURES_DIR}/")

    # ---------------------------------------------------------------- #
    # Step 6 — PDF Report
    # ---------------------------------------------------------------- #
    print_section(6, 'Generating PDF report')
    generate_report(
        output_path = REPORT_PATH,
        df_summary  = summary,
        bf_results  = bf_results,
        fm_results  = fm_results,
        analysis    = analysis,
        fig_paths   = fig_paths,
    )

    # ---------------------------------------------------------------- #
    # Done
    # ---------------------------------------------------------------- #
    print()
    print()
    print('=' * 60)
    print('  ALL DONE')
    print(f'  Database: {DB_PATH}')
    print(f'  Figures : {FIGURES_DIR}/')
    print(f'  Report  : {REPORT_PATH}')
    print('=' * 60)


if __name__ == '__main__':
    main()
