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

# ------------------------------------------------------------------ #
# Ensure src/ is importable
# ------------------------------------------------------------------ #
sys.path.insert(0, os.path.dirname(__file__))

from src.preprocessing   import load_and_clean, dataset_summary
from src.bloom_filter    import run_bloom_filter_demo
from src.flajolet_martin import run_cardinality_comparison
from src.analysis        import run_all as run_analysis
from src.visualizations  import generate_all as generate_figures
from src.report_generator import generate_report

# ------------------------------------------------------------------ #
# Paths
# ------------------------------------------------------------------ #
DATA_PATH    = os.path.join('data', 'netflix_titles.csv')
OUTPUT_DIR   = 'output'
FIGURES_DIR  = os.path.join(OUTPUT_DIR, 'figures')
REPORT_PATH  = os.path.join(OUTPUT_DIR, 'netflix_report.pdf')


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
    # Step 5 — Visualisations
    # ---------------------------------------------------------------- #
    print_section(5, 'Generating visualisations')
    fig_paths = generate_figures(analysis, FIGURES_DIR)
    print(f"  {len(fig_paths)} figures saved to {FIGURES_DIR}/")

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
    print(f'  Figures : {FIGURES_DIR}/')
    print(f'  Report  : {REPORT_PATH}')
    print('=' * 60)


if __name__ == '__main__':
    main()
