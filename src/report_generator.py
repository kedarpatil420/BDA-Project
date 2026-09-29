"""
src/report_generator.py
------------------------
Automated PDF report generation using ReportLab Platypus.

Structure (no cover page — starts from Introduction):
  Chapter 1 – Introduction & Project Overview
  Chapter 2 – Dataset Description & Preprocessing
  Chapter 3 – BDA Algorithm Design
  Chapter 4 – Results & Analysis
  Chapter 5 – Conclusion & Future Scope
"""

import os
from reportlab.lib              import colors
from reportlab.lib.pagesizes    import A4
from reportlab.lib.styles       import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units        import cm, inch
from reportlab.lib.enums        import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus         import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Image as RLImage, HRFlowable,
)
from reportlab.platypus.flowables import KeepTogether


# ======================================================================== #
#  Style helpers
# ======================================================================== #

PAGE_W, PAGE_H = A4
MARGIN         = 2.2 * cm
CONTENT_W      = PAGE_W - 2 * MARGIN

# Colour palette
C_NAVY    = colors.HexColor('#1a2744')
C_ACCENT  = colors.HexColor('#2e5090')
C_LIGHT   = colors.HexColor('#f0f4fa')
C_BORDER  = colors.HexColor('#c8d4e8')
C_WHITE   = colors.white
C_GREY    = colors.HexColor('#555555')
C_BLACK   = colors.HexColor('#1a1a1a')
C_TH_BG   = colors.HexColor('#2e5090')
C_ROW_ALT = colors.HexColor('#f5f7fb')


def _build_styles():
    base = getSampleStyleSheet()

    styles = {
        'chapter_title': ParagraphStyle(
            'ChapterTitle',
            parent    = base['Heading1'],
            fontSize  = 16,
            fontName  = 'Helvetica-Bold',
            textColor = C_NAVY,
            spaceAfter = 6,
            spaceBefore = 4,
            leading    = 20,
        ),
        'section_title': ParagraphStyle(
            'SectionTitle',
            parent    = base['Heading2'],
            fontSize  = 12,
            fontName  = 'Helvetica-Bold',
            textColor = C_ACCENT,
            spaceAfter = 4,
            spaceBefore = 10,
            leading    = 16,
        ),
        'body': ParagraphStyle(
            'Body',
            parent     = base['Normal'],
            fontSize   = 10,
            fontName   = 'Helvetica',
            textColor  = C_BLACK,
            spaceAfter = 6,
            leading    = 14,
            alignment  = TA_JUSTIFY,
        ),
        'bullet': ParagraphStyle(
            'Bullet',
            parent     = base['Normal'],
            fontSize   = 10,
            fontName   = 'Helvetica',
            textColor  = C_BLACK,
            spaceAfter = 3,
            leading    = 14,
            leftIndent = 14,
            bulletIndent = 4,
        ),
        'caption': ParagraphStyle(
            'Caption',
            parent    = base['Normal'],
            fontSize  = 9,
            fontName  = 'Helvetica-Oblique',
            textColor = C_GREY,
            spaceAfter = 8,
            alignment  = TA_CENTER,
        ),
        'table_cell': ParagraphStyle(
            'TableCell',
            parent   = base['Normal'],
            fontSize = 9,
            fontName = 'Helvetica',
            leading  = 12,
        ),
    }
    return styles


# ======================================================================== #
#  Page footer (page numbers)
# ======================================================================== #

def _add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(C_GREY)
    canvas.drawString(MARGIN, 1.2 * cm, 'Netflix Content Analytics — BDA Mini-Project')
    canvas.drawRightString(PAGE_W - MARGIN, 1.2 * cm, f'Page {doc.page}')
    # Thin rule above footer
    canvas.setStrokeColor(C_BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 1.5 * cm, PAGE_W - MARGIN, 1.5 * cm)
    canvas.restoreState()


# ======================================================================== #
#  Table factory helpers
# ======================================================================== #

TABLE_HEADER_STYLE = [
    ('BACKGROUND', (0, 0), (-1, 0), C_TH_BG),
    ('TEXTCOLOR',  (0, 0), (-1, 0), C_WHITE),
    ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE',   (0, 0), (-1, 0), 9),
    ('ALIGN',      (0, 0), (-1, 0), 'CENTER'),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('LEFTPADDING',   (0, 0), (-1, -1), 6),
    ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
    ('FONTNAME',   (0, 1), (-1, -1), 'Helvetica'),
    ('FONTSIZE',   (0, 1), (-1, -1), 9),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_WHITE, C_ROW_ALT]),
    ('GRID', (0, 0), (-1, -1), 0.4, C_BORDER),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
]


def _make_table(data, col_widths=None, extra_style=None):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = list(TABLE_HEADER_STYLE)
    if extra_style:
        style_cmds += extra_style
    t.setStyle(TableStyle(style_cmds))
    return t


def _chapter_header(title: str, styles: dict) -> list:
    """Return a list of flowables forming a chapter heading."""
    return [
        HRFlowable(width='100%', thickness=2, color=C_NAVY, spaceAfter=6),
        Paragraph(title, styles['chapter_title']),
        HRFlowable(width='100%', thickness=0.5, color=C_BORDER, spaceAfter=10),
    ]


def _fig_block(path: str, caption: str, styles: dict, width_frac: float = 0.92) -> list:
    """Return [Image, Caption] flowables for embedding a figure."""
    img_w = CONTENT_W * width_frac
    img_h = img_w * 0.5          # assume 2:1 aspect ratio (10×5 inch figures)
    return [
        Spacer(1, 0.2 * cm),
        RLImage(path, width=img_w, height=img_h),
        Paragraph(caption, styles['caption']),
        Spacer(1, 0.3 * cm),
    ]


# ======================================================================== #
#  Chapter builders
# ======================================================================== #

def _chapter1(styles: dict) -> list:
    S = styles
    story = _chapter_header('Chapter 1: Introduction & Project Overview', S)

    story.append(Paragraph('Project Description', S['section_title']))
    story.append(Paragraph(
        'This project analyses the Netflix content library (8,807 titles as of mid-2021) '
        'using advanced Big Data Analytics algorithms to understand content trends and '
        'platform composition.  The project implements two probabilistic data structures — '
        'a <b>Bloom Filter</b> for efficient membership testing and the '
        '<b>Flajolet-Martin / HyperLogLog</b> algorithm for cardinality estimation — '
        'alongside a comprehensive content analysis and automated PDF reporting pipeline.',
        S['body'],
    ))

    story.append(Paragraph('Questions Answered Through the Project', S['section_title']))
    bullets = [
        'How can we efficiently determine whether a specific title is available on Netflix '
        'without scanning the entire dataset?',
        'How many unique titles does Netflix host? Can we estimate this accurately without '
        'counting every row?',
        'How has the Netflix catalog grown over time, and which years saw the highest content additions?',
        'Which countries produce the most Netflix content, and which genres are most common?',
        'What are the typical runtimes of Netflix movies, and how are TV show seasons distributed?',
        'How do TV-14 / TV-MA ratings compare to family-friendly ratings in the catalog?',
    ]
    for b in bullets:
        story.append(Paragraph(f'\u2022 {b}', S['bullet']))

    story.append(Paragraph('Tools and Technologies', S['section_title']))
    tools = [
        '<b>Python 3.x</b>  — primary programming language',
        '<b>Pandas</b>      — data ingestion, cleaning, and manipulation',
        '<b>NumPy</b>       — numerical computations',
        '<b>Matplotlib / Seaborn</b> — data visualisation',
        '<b>hashlib</b>     — SHA-256 and MD5 hashing for BDA algorithms',
        '<b>ReportLab</b>   — automated PDF report generation',
        '<b>Custom classes</b> — BloomFilter, FlajoletMartin, HyperLogLog',
    ]
    for t in tools:
        story.append(Paragraph(f'\u2022 {t}', S['bullet']))

    story.append(Spacer(1, 0.3 * cm))
    return story


def _chapter2(df_summary: dict, styles: dict) -> list:
    S = styles
    story = _chapter_header('Chapter 2: Dataset Description & Preprocessing', S)

    story.append(Paragraph('Dataset Overview', S['section_title']))
    story.append(Paragraph(
        'The dataset is the publicly available Netflix Movies and TV Shows dataset, '
        'containing metadata for every title available on the platform as of mid-2021. '
        f'It comprises <b>{df_summary["total_rows"]:,} rows</b> and '
        '<b>12 original columns</b>. During preprocessing, four derived columns were '
        'added for analysis, resulting in 16 columns in the processed dataset. '
        f'The dataset contains <b>{df_summary["num_movies"]:,} Movies</b> and '
        f'<b>{df_summary["num_tv"]:,} TV Shows</b>. '
        f'Content spans release years from {df_summary["min_year"]} to {df_summary["max_year"]}.',
        S['body'],
    ))

    # Column descriptions table
    story.append(Paragraph('Column Descriptions', S['section_title']))
    col_data = [
        ['Column', 'Type', 'Description'],
        ['show_id',      'String',  'Unique identifier for each title'],
        ['type',         'String',  'Content type: Movie or TV Show'],
        ['title',        'String',  'Title of the content'],
        ['director',     'String',  'Director name(s); 29.9 % missing'],
        ['cast',         'String',  'Comma-separated cast list; 9.4 % missing'],
        ['country',      'String',  'Country of origin; 9.4 % missing'],
        ['date_added',   'String',  'Date added to Netflix (raw string)'],
        ['release_year', 'Integer', 'Original release year'],
        ['rating',       'String',  'Content rating (TV-MA, PG-13, etc.)'],
        ['duration',     'String',  'Runtime ("90 min") or seasons ("2 Seasons")'],
        ['listed_in',    'String',  'Comma-separated genre tags'],
        ['description',  'String',  'Short plot description'],
    ]
    col_widths = [CONTENT_W * w for w in [0.18, 0.12, 0.70]]
    story.append(_make_table(col_data, col_widths=col_widths))
    story.append(Spacer(1, 0.3 * cm))

    # Missing values table
    story.append(Paragraph('Missing Values (Before Cleaning)', S['section_title']))
    mv_data = [['Column', 'Missing Count', 'Missing %']]
    mv_raw  = df_summary['missing_before']
    total   = df_summary['total_rows']
    for col, cnt in mv_raw.items():
        mv_data.append([col, f'{cnt:,}', f'{cnt/total*100:.2f} %'])
    col_widths2 = [CONTENT_W * w for w in [0.45, 0.28, 0.27]]
    story.append(_make_table(mv_data, col_widths=col_widths2))
    story.append(Spacer(1, 0.3 * cm))

    # Preprocessing steps
    story.append(Paragraph('Preprocessing Steps', S['section_title']))
    steps = [
        '<b>Swap Fix:</b> Three rows contained duration values (74 min, 84 min, 66 min) '
        'in the rating column — a known dataset bug.  Values were moved to the correct column.',
        '<b>Whitespace Stripping:</b> Applied str.strip() to all string columns to eliminate '
        'leading/trailing spaces (one near-duplicate title was resolved this way).',
        '<b>Missing Value Imputation:</b> director, cast, country filled with "Unknown"; '
        'rating filled with "NR" (Not Rated).',
        '<b>Date Parsing:</b> date_added converted from plain English strings '
        '(e.g., "September 25, 2021") to datetime; year_added and month_added extracted.',
        '<b>Duration Parsing:</b> The mixed-format duration column was split into '
        'duration_min (Movies, integer minutes) and num_seasons (TV Shows, integer count).',
        '<b>Row Removal:</b> No rows were removed during preprocessing; '
        'the three affected rows were corrected by moving their duration values '
        'from the rating column to the correct duration column.',
    ]
    for s in steps:
        story.append(Paragraph(f'\u2022 {s}', S['bullet']))

    story.append(Spacer(1, 0.3 * cm))
    return story


def _chapter3(bf_info: dict, fm_results: dict, styles: dict) -> list:
    S = styles
    story = _chapter_header('Chapter 3: BDA Algorithm Design', S)

    # ---- Bloom Filter ----
    story.append(Paragraph('3.1  Bloom Filter', S['section_title']))
    story.append(Paragraph(
        'A Bloom Filter is a space-efficient probabilistic data structure used to test '
        'set membership.  It can definitively answer "NO" (the element is not in the set) '
        'but may occasionally answer "YES" even when the element is absent '
        '(a <i>false positive</i>).  There are <b>no false negatives</b>.',
        S['body'],
    ))
    story.append(Paragraph(
        '<b>Double Hashing:</b>  To generate k independent bit positions from a single item x, '
        'we use two base hash functions h1 (SHA-256) and h2 (MD5) and compute: '
        '<i>h_i(x) = (h1(x) + i × h2(x))  mod  m</i>  for i = 0, 1, …, k−1.  '
        'This avoids storing k separate hash functions while still producing k '
        'independently distributed positions.',
        S['body'],
    ))
    story.append(Paragraph(
        '<b>Optimal Parameters:</b> Given n expected items and desired false-positive rate p: '
        '<i>m = -n ln(p) / (ln(2))^2</i> (bit array size) and '
        '<i>k = (m/n) ln(2)</i> (number of hash functions).',
        S['body'],
    ))
    bf_table = [
        ['Parameter', 'Value'],
        ['Expected items (n)',          f'{bf_info["items_inserted"]:,}'],
        ['Bit array size (m)',          f'{bf_info["bit_array_size_bits"]:,} bits  ({bf_info["bit_array_size_bytes"]:,} bytes)'],
        ['Hash functions (k)',          str(bf_info['num_hash_functions'])],
        ['Target false-positive rate',  f'{bf_info["target_fpr_pct"]} %'],
        ['Actual false-positive rate',  f'{bf_info["actual_fpr_pct"]} %'],
    ]
    col_widths3 = [CONTENT_W * 0.55, CONTENT_W * 0.45]
    story.append(_make_table(bf_table, col_widths=col_widths3))
    story.append(Spacer(1, 0.3 * cm))

    # ---- Flajolet-Martin ----
    story.append(Paragraph('3.2  Flajolet-Martin Algorithm', S['section_title']))
    story.append(Paragraph(
        'The Flajolet-Martin (FM) algorithm estimates the number of distinct elements '
        'in a data stream in a single pass, using sub-linear memory. '
        'Each item is hashed to a large integer; the number of trailing zeros in its '
        'binary representation is recorded. '
        'If R is the maximum trailing-zero count across all items, the estimate is '
        '<i>n_hat = phi x 2^R</i>, where phi is approximately 0.7735.',
        S['body'],
    ))
    story.append(Paragraph(
        '<b>Multi-Run Bias Correction (Log-Space Aggregation):</b>  '
        'A single FM run has high variance: its estimate is always a power of 2 scaled by '
        'phi, so consecutive possible values jump by a factor of 2 (e.g. 6,337 to 12,674).  '
        'To reduce variance, 32 independent trials are run (each using a differently salted '
        'SHA-256 hash).  The 32 raw R values (small integers, typically 11-16 for this '
        'dataset) are grouped into 4 groups of 8.  <b>The mean is computed on R values '
        '(in log-space) within each group</b>, and the median of those four R-means is '
        'taken as R*.  The final estimate is phi x 2^(R*).',
        S['body'],
    ))
    story.append(Paragraph(
        '<b>Why log-space?</b> Averaging the full estimates phi x 2^R_i in linear space '
        'can be strongly affected by trials with large R values. Averaging the R values '
        'instead keeps the aggregation bounded and produced a 2.55 % error for this dataset.',
        S['body'],
    ))

    # ---- HyperLogLog ----
    story.append(Paragraph('3.3  HyperLogLog', S['section_title']))
    story.append(Paragraph(
        'HyperLogLog (HLL) is an improved cardinality estimator that partitions the hash '
        'space into m = 2^b buckets (registers).  Each register stores the maximum ρ seen '
        'for hashes mapped to that bucket.  The estimate uses the harmonic mean of '
        '2^(−M[j]) across all registers, scaled by a bias-correction constant α_m: '
        '<i>E = α_m × m² × (Σ 2^(−M[j]))^(−1)</i>.',
        S['body'],
    ))
    story.append(Paragraph(
        'This project uses <b>b = 8</b> (m = 256 registers), giving a theoretical '
        'standard relative error of approximately 6.5 %. Small-range and large-range '
        'corrections are also applied.',
        S['body'],
    ))

    story.append(Spacer(1, 0.3 * cm))
    return story


def _chapter4(bf_results: dict, fm_results: dict, analysis: dict,
               fig_paths: dict, styles: dict) -> list:
    S = styles
    story = _chapter_header('Chapter 4: Results & Analysis', S)

    # ---- 4.1 Bloom Filter results ----
    story.append(Paragraph('4.1  Bloom Filter — Membership Test Results', S['section_title']))
    story.append(Paragraph(
        'The Bloom Filter was built from all 8,807 cleaned Netflix titles and then '
        'tested against five known titles (expected: Present) and five non-existent '
        'titles (expected: Absent).',
        S['body'],
    ))

    mem_data = [['Title', 'Expected', 'Filter Result', 'Correct?']]
    for title, result in bf_results['known_results']:
        mem_data.append([
            title,
            'Present',
            'PRESENT' if result else 'ABSENT',
            '✓' if result else '✗',
        ])
    for title, result in bf_results['unknown_results']:
        mem_data.append([
            title,
            'Absent',
            'PRESENT (FP)' if result else 'ABSENT',
            '✗ FP' if result else '✓',
        ])

    col_widths4 = [CONTENT_W * w for w in [0.40, 0.15, 0.25, 0.20]]
    extra = [
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (3, 1), (3, 5),  colors.HexColor('#1a7a3a')),   # green ticks
        ('TEXTCOLOR', (3, 6), (3, -1), colors.HexColor('#1a7a3a')),
    ]
    story.append(_make_table(mem_data, col_widths=col_widths4, extra_style=extra))
    story.append(Spacer(1, 0.3 * cm))

    # ---- 4.2 Cardinality estimation ----
    story.append(Paragraph('4.2  Cardinality Estimation — FM vs HyperLogLog', S['section_title']))
    story.append(Paragraph(
        'Three methods were applied to estimate the number of unique Netflix titles: '
        'a single-pass FM run, the multi-run bias-corrected FM (32 trials), '
        'and HyperLogLog with 256 registers.  Results are compared against the exact count.',
        S['body'],
    ))

    card_data = [
        ['Method', 'Estimate', 'Exact Count', '% Error'],
        ['Exact Count (Pandas)',      f'{fm_results["actual"]:,}',       f'{fm_results["actual"]:,}', '0.00 %'],
        ['FM — Single Run',           f'{fm_results["fm_single"]:,}',    f'{fm_results["actual"]:,}', f'{fm_results["fm_single_error"]} %'],
        ['FM — Multi-Run (32 trials)',f'{fm_results["fm_multi"]:,}',     f'{fm_results["actual"]:,}', f'{fm_results["fm_multi_error"]} %'],
        ['HyperLogLog (256 registers)',f'{fm_results["hll"]:,}',         f'{fm_results["actual"]:,}', f'{fm_results["hll_error"]} %'],
    ]
    col_widths5 = [CONTENT_W * w for w in [0.38, 0.18, 0.18, 0.26]]
    story.append(_make_table(card_data, col_widths=col_widths5))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        '<b>Observation:</b>  The single FM run shows high error (~64%) because its '
        'estimate is constrained to discrete values of the form phi x 2^R — '
        'consecutive estimates differ by a factor of 2, so even a well-implemented '
        'single run is typically 30-80% off.  The multi-run FM (32 trials, log-space '
        'aggregation) reduces error to ~3% by averaging the R exponents before '
        'exponentiating, preventing large R outliers from dominating.  '
        'HyperLogLog achieves similar accuracy using 256 parallel registers '
        'and the harmonic mean estimator, which has a theoretical relative '
        'standard error of 1.04/sqrt(256) approx 6.5%.',
        S['body'],
    ))

    # ---- 4.3 Content Analysis ----
    story.append(Paragraph('4.3  Content Analysis & Visualisations', S['section_title']))

    type_split = analysis['type_split']
    story.append(Paragraph(
        f'The Netflix dataset contains <b>{int(type_split.get("Movie", 0)):,} Movies '
        f'({int(type_split.get("Movie", 0)) / type_split.sum() * 100:.1f} %)</b> and '
        f'<b>{int(type_split.get("TV Show", 0)):,} TV Shows '
        f'({int(type_split.get("TV Show", 0)) / type_split.sum() * 100:.1f} %)</b>.  '
        f'This shows that Movies represent the larger share of titles in the dataset, '
        f'while TV Shows account for the remaining portion.',
        S['body'],
    ))

    # Embed each figure with a caption and insight
    figures_meta = [
        ('fig1', 'Figure 1: Movies vs TV Shows — Pie Chart.',
         None),
        ('fig2', 'Figure 2: Top 15 Countries by Number of Titles.',
         'The United States has the largest number of titles in the dataset, followed '
         'by India and the United Kingdom. South Korea, Japan, and other countries also '
         'contribute substantial numbers of titles.'),
        ('fig3', 'Figure 3: Top 15 Genre Tags on Netflix.',
        'International Movies and Dramas are among the most frequent genre tags in '
        'the dataset. Stand-Up Comedy and Documentaries are also among the more '
        'frequently occurring genre tags.'),
        ('fig4', 'Figure 4: Distribution of Content Ratings.',
        'TV-MA is the most frequently occurring content rating in the dataset. '
        'TV-14 and R are also among the more frequent ratings.'),
        ('fig5', 'Figure 5: Netflix Titles by Original Release Year (1990–2021).',
         'The number of titles by original release year increased substantially in the '
         'later years, with 2018 representing the highest point in this dataset.'),
        ('fig6', 'Figure 6: Content Added to Netflix Over Time (by Year).',
         'The number of titles added to Netflix increased substantially from 2015 to 2019, '
         'with 2019 representing the peak year for additions in this dataset. The number '
         'of additions decreased in the following years.'),
        ('fig7', 'Figure 7: Movie Duration Distribution.',
         f'Most Netflix movies fall between 80 and 120 minutes.  '
         f'The distribution is approximately normal with a slight right skew.  '
         f'Mean runtime is approximately {analysis["movie_duration"]["mean"]} min '
         f'and median is {analysis["movie_duration"]["median"]} min.'),
        ('fig8', 'Figure 8: TV Show Seasons Distribution.',
        'A majority of Netflix TV Shows have only 1 season, while relatively few '
        'shows have more than 5 seasons.'),
    ]

    for key, caption, insight in figures_meta:
        if key in fig_paths and os.path.exists(fig_paths[key]):
            story += _fig_block(fig_paths[key], caption, S)
            if insight:
                story.append(Paragraph(f'<b>Insight:</b> {insight}', S['body']))
                story.append(Spacer(1, 0.2 * cm))

    return story


def _chapter5(styles: dict) -> list:
    S = styles
    story = _chapter_header('Chapter 5: Conclusion & Future Scope', S)

    story.append(Paragraph('Conclusion', S['section_title']))
    story.append(Paragraph(
        'This project successfully demonstrated the application of two classical Big Data '
        'algorithms — the Bloom Filter and the Flajolet-Martin / HyperLogLog algorithm — '
        'on a real-world content dataset.',
        S['body'],
    ))
    story.append(Paragraph(
        'The Bloom Filter provided O(k) membership testing with a configured '
        '1 % false-positive rate, using an 84,416-bit (10,552-byte) bit array '
        'for nearly 9,000 titles. '
        'All five tested known Netflix titles were correctly identified as present, '
        'while all five tested non-existent titles returned absent.',
        S['body'],
    ))
    story.append(Paragraph(
        'The <b>Flajolet-Martin algorithm</b> with multi-run bias correction and '
        '<b>HyperLogLog</b> both produced cardinality estimates close to the exact unique '
        'count in this dataset. The multi-run FM produced a 2.55 % error, while HyperLogLog '
        'produced a 3.67 % error. The single-run FM showed substantially higher error, '
        'demonstrating the benefit of multiple trials and aggregation.',
        S['body'],
    ))
    story.append(Paragraph(
        'The content analysis shows that the United States has the largest number of '
        'titles in the dataset, while International Movies and Dramas are among the '
        'most common genre tags. TV-MA is the most frequent content rating. '
        'The number of titles added to Netflix increased substantially from 2015 to 2019, '
        'while the typical movie runtime is approximately 90–100 minutes.',
        S['body'],
    ))

    story.append(Paragraph('Future Scope', S['section_title']))
    future = [
        'Extend the Bloom Filter to support <b>Counting Bloom Filters</b> for deletion support.',
        'Apply FM / HLL across sub-groups (per country, per genre) to compare cardinality across segments.',
        'Use <b>MinHash / LSH</b> for near-duplicate description detection across titles.',
        'Integrate real-time Netflix API data for live catalog monitoring.',
        'Apply <b>Count-Min Sketch</b> for streaming frequency estimation of genre/country combinations.',
        'Build a time-series model to predict content addition trends for upcoming years.',
    ]
    for f in future:
        story.append(Paragraph(f'\u2022 {f}', S['bullet']))

    story.append(Spacer(1, 0.5 * cm))
    return story


# ======================================================================== #
#  Master generate function
# ======================================================================== #

def generate_report(
    output_path : str,
    df_summary  : dict,
    bf_results  : dict,
    fm_results  : dict,
    analysis    : dict,
    fig_paths   : dict,
) -> None:
    """
    Build and save the complete PDF report.

    Parameters
    ----------
    output_path : str
        Full path where the PDF should be saved.
    df_summary  : dict   From preprocessing.dataset_summary().
    bf_results  : dict   From bloom_filter.run_bloom_filter_demo().
    fm_results  : dict   From flajolet_martin.run_cardinality_comparison().
    analysis    : dict   From analysis.run_all().
    fig_paths   : dict   From visualizations.generate_all().
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize    = A4,
        leftMargin  = MARGIN,
        rightMargin = MARGIN,
        topMargin   = 2 * cm,
        bottomMargin= 2 * cm,
    )

    styles = _build_styles()

    story = []

    # Chapter 1
    story += _chapter1(styles)
    story.append(PageBreak())

    # Chapter 2
    story += _chapter2(df_summary, styles)
    story.append(PageBreak())

    # Chapter 3
    story += _chapter3(bf_results['filter_info'], fm_results, styles)
    story.append(PageBreak())

    # Chapter 4
    story += _chapter4(bf_results, fm_results, analysis, fig_paths, styles)
    story.append(PageBreak())

    # Chapter 5
    story += _chapter5(styles)

    doc.build(story, onFirstPage=_add_footer, onLaterPages=_add_footer)
    print(f"  PDF report saved: {output_path}")
