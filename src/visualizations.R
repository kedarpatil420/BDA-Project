#!/usr/bin/env Rscript
# ==============================================================================
# src/visualizations.R
# --------------------
# Publication-quality figure generation for Netflix Content Analytics using ggplot2.
# Only requires ggplot2, dplyr, and readr.
#
# Generates eight visualizations:
#   fig1 - Movies vs TV Shows (Pie / Donut chart)
#   fig2 - Top 15 Countries (Horizontal bar chart)
#   fig3 - Top 15 Genres (Horizontal bar chart)
#   fig4 - Rating Distribution (Bar chart)
#   fig5 - Content by Release Year (Line chart with shaded area, 1990-2021)
#   fig6 - Content Added Over Time (Bar chart, by year_added >= 2008)
#   fig7 - Movie Duration Distribution (Histogram + KDE curve + Mean/Median lines)
#   fig8 - TV Show Seasons Distribution (Bar chart, seasons 1-15)
#
# Output:
#   PNG images saved to output/figures/ at 150 DPI.
# ==============================================================================

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(readr)
})

# ------------------------------------------------------------------------------
# Configuration & Global Theme
# ------------------------------------------------------------------------------
args <- commandArgs(trailingOnly = TRUE)
input_path  <- if (length(args) >= 1) args[1] else "output/cleaned_netflix_titles.csv"
figures_dir <- if (length(args) >= 2) args[2] else "output/figures"

if (!dir.exists(figures_dir)) {
  dir.create(figures_dir, recursive = TRUE)
}

# Color constants matching Python Seaborn theme
COLOR_BAR   <- "#4C72B0"
COLOR_LINE  <- "#DD8452"
COLOR_ACCENT<- "#C44E52"
COLOR_GREEN <- "#55A868"
MUTED_COLORS<- c("#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
                 "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD")

custom_theme <- function() {
  theme_minimal(base_size = 11) +
    theme(
      plot.title = element_text(size = 14, face = "bold", hjust = 0, margin = margin(b = 10)),
      axis.title.x = element_text(size = 11, face = "plain", margin = margin(t = 8)),
      axis.title.y = element_text(size = 11, face = "plain", margin = margin(r = 8)),
      axis.text = element_text(size = 9, color = "#333333"),
      panel.grid.major = element_line(color = "#E0E0E0", linewidth = 0.5),
      panel.grid.minor = element_blank(),
      plot.background = element_rect(fill = "white", color = NA),
      panel.background = element_rect(fill = "white", color = NA),
      legend.position = "right",
      legend.title = element_blank(),
      legend.text = element_text(size = 9)
    )
}

# Custom comma formatting helper (avoids external dependency on scales)
comma_fmt <- function(x) {
  format(x, big.mark = ",", trim = TRUE, scientific = FALSE)
}

# ------------------------------------------------------------------------------
# Data Loading & Verification
# ------------------------------------------------------------------------------
if (!file.exists(input_path)) {
  # Fallback: check if raw data exists and clean it identically to src/preprocessing.py
  raw_path <- "data/netflix_titles.csv"
  if (file.exists(raw_path)) {
    message("Cleaned file not found at ", input_path, ". Loading and cleaning from ", raw_path, "...")
    
    # Ensure English locale for month name parsing (%B) across all operating systems
    tryCatch({
      Sys.setlocale("LC_TIME", "English")
    }, error = function(e) {
      Sys.setlocale("LC_TIME", "C")
    })
    
    df_raw <- read_csv(raw_path, col_types = cols(.default = "c"), show_col_types = FALSE)
    
    # 1. Swapped rating / duration rows fix
    swapped_idx <- df_raw$rating %in% c("74 min", "84 min", "66 min")
    df_raw$duration[swapped_idx] <- df_raw$rating[swapped_idx]
    df_raw$rating[swapped_idx] <- NA_character_
    
    # 2. Strip whitespace from all string columns
    df_raw <- df_raw %>% mutate(across(where(is.character), trimws))
    
    # 3. Fill missing values
    df_raw$director[is.na(df_raw$director)] <- "Unknown"
    df_raw$cast[is.na(df_raw$cast)]         <- "Unknown"
    df_raw$country[is.na(df_raw$country)]   <- "Unknown"
    df_raw$rating[is.na(df_raw$rating)]     <- "NR"
    
    # 4. Parse date_added (plain English string -> datetime, year_added, month_added)
    parsed_dates <- as.Date(df_raw$date_added, format = "%B %d, %Y")
    df_raw$year_added  <- as.numeric(format(parsed_dates, "%Y"))
    df_raw$month_added <- as.numeric(format(parsed_dates, "%m"))
    df_raw$date_added  <- as.character(parsed_dates)
    
    # 5. Parse duration into duration_min (Movies) and num_seasons (TV Shows)
    dur_extracted <- as.numeric(sub("^([0-9]+).*", "\\1", df_raw$duration))
    df_raw$duration_min <- ifelse(df_raw$type == "Movie", dur_extracted, NA_real_)
    df_raw$num_seasons  <- ifelse(df_raw$type == "TV Show", dur_extracted, NA_real_)
    df_raw$release_year <- as.numeric(df_raw$release_year)
    
    # 6. Drop unparseable duration (matches Python dropna subset=['duration'])
    df <- df_raw %>% filter(!is.na(duration))
  } else {
    stop("Input data file not found: ", input_path)
  }
} else {
  message("Loading preprocessed dataset from: ", input_path)
  df <- read_csv(input_path, col_types = cols(
    release_year = col_double(),
    year_added = col_double(),
    month_added = col_double(),
    duration_min = col_double(),
    num_seasons = col_double(),
    .default = col_character()
  ), show_col_types = FALSE)
}

# ------------------------------------------------------------------------------
# Figure 1: Movies vs TV Shows (Pie Chart with counts and percentages)
# ------------------------------------------------------------------------------
message("Generating Figure 1: Content Type Split...")
type_counts <- df %>%
  count(type) %>%
  mutate(
    pct = n / sum(n) * 100,
    label_pct = sprintf("%.1f%%", pct),
    legend_label = sprintf("%s: %s", type, format(n, big.mark = ","))
  )

p1 <- ggplot(type_counts, aes(x = "", y = n, fill = type)) +
  geom_bar(stat = "identity", width = 1, color = "white", linewidth = 1.2) +
  coord_polar(theta = "y", start = 0) +
  scale_fill_manual(
    values = c("Movie" = "#4C72B0", "TV Show" = "#DD8452"),
    labels = type_counts$legend_label
  ) +
  geom_text(
    aes(label = label_pct),
    position = position_stack(vjust = 0.5),
    color = "white",
    size = 4.5,
    fontface = "bold"
  ) +
  labs(
    title = "Netflix Content: Movies vs TV Shows",
    x = NULL, y = NULL
  ) +
  theme_void(base_size = 11) +
  theme(
    plot.title = element_text(size = 14, face = "bold", hjust = 0.5, margin = margin(t = 10, b = 15)),
    legend.position = "right",
    legend.title = element_blank(),
    legend.text = element_text(size = 9),
    plot.background = element_rect(fill = "white", color = NA)
  )

ggsave(file.path(figures_dir, "fig1_content_type.png"), plot = p1,
       width = 7, height = 5, dpi = 150)


# ------------------------------------------------------------------------------
# Figure 2: Top 15 Countries (Horizontal bar chart)
# ------------------------------------------------------------------------------
message("Generating Figure 2: Top 15 Countries...")
top_countries <- df %>%
  filter(country != "Unknown", !is.na(country)) %>%
  count(country, sort = TRUE) %>%
  slice_head(n = 15) %>%
  mutate(country = reorder(country, n))

p2 <- ggplot(top_countries, aes(x = n, y = country)) +
  geom_col(fill = COLOR_BAR, color = "white", linewidth = 0.5, width = 0.7) +
  geom_text(aes(label = format(n, big.mark = ",")),
            hjust = -0.15, size = 3.2, color = "#222222") +
  scale_x_continuous(
    labels = comma_fmt,
    expand = expansion(mult = c(0, 0.15))
  ) +
  labs(
    title = "Top 15 Countries by Number of Titles",
    x = "Number of Titles",
    y = NULL
  ) +
  custom_theme() +
  theme(
    panel.grid.major.y = element_blank(),
    axis.text.y = element_text(size = 9)
  )

ggsave(file.path(figures_dir, "fig2_top_countries.png"), plot = p2,
       width = 10, height = 6, dpi = 150)


# ------------------------------------------------------------------------------
# Figure 3: Top 15 Genres (Horizontal bar chart with palette)
# ------------------------------------------------------------------------------
message("Generating Figure 3: Top 15 Genres...")
raw_genres <- df$listed_in[!is.na(df$listed_in)]
split_genres <- trimws(unlist(strsplit(raw_genres, ",")))
top_genres <- as.data.frame(table(genre = split_genres), stringsAsFactors = FALSE) %>%
  rename(n = Freq) %>%
  arrange(desc(n)) %>%
  slice_head(n = 15) %>%
  mutate(genre = reorder(genre, n))

genre_palette <- colorRampPalette(c("#4C72B0", "#64B5CD", "#55A868", "#CCB974", "#DD8452", "#C44E52"))(15)

p3 <- ggplot(top_genres, aes(x = n, y = genre, fill = genre)) +
  geom_col(color = "white", linewidth = 0.5, width = 0.7, show.legend = FALSE) +
  scale_fill_manual(values = genre_palette) +
  geom_text(aes(label = format(n, big.mark = ",")),
            hjust = -0.15, size = 3.2, color = "#222222") +
  scale_x_continuous(
    labels = comma_fmt,
    expand = expansion(mult = c(0, 0.18))
  ) +
  labs(
    title = "Top 15 Genre Tags on Netflix",
    x = "Number of Titles",
    y = NULL
  ) +
  custom_theme() +
  theme(
    panel.grid.major.y = element_blank(),
    axis.text.y = element_text(size = 9)
  )

ggsave(file.path(figures_dir, "fig3_top_genres.png"), plot = p3,
       width = 10, height = 6, dpi = 150)


# ------------------------------------------------------------------------------
# Figure 4: Rating Distribution (Vertical bar chart, descending)
# ------------------------------------------------------------------------------
message("Generating Figure 4: Rating Distribution...")
ratings_data <- df %>%
  filter(!is.na(rating)) %>%
  count(rating, sort = TRUE) %>%
  filter(n > 2) %>%
  mutate(rating = reorder(rating, -n))

n_ratings <- nrow(ratings_data)
ratings_blues <- colorRampPalette(c("#1a3b6e", "#3a6ea5", "#6c9cd2", "#a6c8e0", "#cfe2f3"))(n_ratings)

p4 <- ggplot(ratings_data, aes(x = rating, y = n, fill = rating)) +
  geom_col(color = "white", linewidth = 0.5, width = 0.7, show.legend = FALSE) +
  scale_fill_manual(values = ratings_blues) +
  geom_text(aes(label = format(n, big.mark = ",")),
            vjust = -0.5, size = 3.2, color = "#222222") +
  scale_y_continuous(
    labels = comma_fmt,
    expand = expansion(mult = c(0, 0.12))
  ) +
  labs(
    title = "Distribution of Content Ratings",
    x = "Content Rating",
    y = "Number of Titles"
  ) +
  custom_theme() +
  theme(
    panel.grid.major.x = element_blank(),
    axis.text.x = element_text(size = 9, angle = 0)
  )

ggsave(file.path(figures_dir, "fig4_rating_distribution.png"), plot = p4,
       width = 10, height = 5, dpi = 150)


# ------------------------------------------------------------------------------
# Figure 5: Content by Release Year (1990-2021)
# ------------------------------------------------------------------------------
message("Generating Figure 5: Content by Release Year...")
by_year <- df %>%
  filter(!is.na(release_year), release_year >= 1990) %>%
  count(release_year) %>%
  arrange(release_year)

p5 <- ggplot(by_year, aes(x = release_year, y = n)) +
  geom_area(fill = COLOR_BAR, alpha = 0.15) +
  geom_line(color = COLOR_BAR, linewidth = 1.0) +
  geom_point(color = COLOR_BAR, size = 1.8) +
  scale_x_continuous(breaks = seq(1990, max(by_year$release_year, na.rm = TRUE), by = 5)) +
  scale_y_continuous(labels = comma_fmt, expand = expansion(mult = c(0, 0.08))) +
  labs(
    title = "Netflix Titles by Original Release Year (1990–2021)",
    x = "Release Year",
    y = "Number of Titles"
  ) +
  custom_theme() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1)
  )

ggsave(file.path(figures_dir, "fig5_release_year.png"), plot = p5,
       width = 10, height = 5, dpi = 150)


# ------------------------------------------------------------------------------
# Figure 6: Content Added Over Time (by year_added >= 2008)
# ------------------------------------------------------------------------------
message("Generating Figure 6: Content Added Over Time...")
added_over_time <- df %>%
  filter(!is.na(year_added), year_added >= 2008) %>%
  count(year_added) %>%
  arrange(year_added) %>%
  mutate(year_factor = factor(year_added))

n_years <- nrow(added_over_time)
years_blues <- colorRampPalette(c("#d0e1f9", "#8bb4e7", "#4b86c8", "#2c5d9e", "#1b3864"))(n_years)

p6 <- ggplot(added_over_time, aes(x = year_factor, y = n, fill = year_factor)) +
  geom_col(color = "white", linewidth = 0.5, width = 0.7, show.legend = FALSE) +
  scale_fill_manual(values = years_blues) +
  geom_text(aes(label = format(n, big.mark = ",")),
            vjust = -0.4, size = 2.7, color = "#222222") +
  scale_y_continuous(labels = comma_fmt, expand = expansion(mult = c(0, 0.15))) +
  labs(
    title = "Content Added to Netflix Over Time (by Year)",
    x = "Year",
    y = "Titles Added"
  ) +
  custom_theme() +
  theme(
    panel.grid.major.x = element_blank(),
    axis.text.x = element_text(angle = 45, hjust = 1)
  )

ggsave(file.path(figures_dir, "fig6_added_over_time.png"), plot = p6,
       width = 10, height = 5, dpi = 150)


# ------------------------------------------------------------------------------
# Figure 7: Movie Duration Distribution (Histogram + KDE curve + Mean/Median)
# ------------------------------------------------------------------------------
message("Generating Figure 7: Movie Duration Distribution...")
movie_durations <- df %>%
  filter(type == "Movie", !is.na(duration_min)) %>%
  pull(duration_min)

mean_dur   <- round(mean(movie_durations), 1)
median_dur <- round(median(movie_durations), 1)

movie_df <- data.frame(duration = movie_durations)
bin_width <- (max(movie_durations) - min(movie_durations)) / 40

p7 <- ggplot(movie_df, aes(x = duration)) +
  geom_histogram(aes(y = after_stat(count)),
                 bins = 40, fill = COLOR_BAR, alpha = 0.7,
                 color = "white", linewidth = 0.4) +
  geom_density(aes(y = after_stat(density) * length(movie_durations) * bin_width, color = "KDE"),
               linewidth = 1.0) +
  geom_vline(aes(xintercept = mean_dur, linetype = "Mean"), color = "red", linewidth = 0.9) +
  geom_vline(aes(xintercept = median_dur, linetype = "Median"), color = "green", linewidth = 0.9) +
  scale_color_manual(
    name = "",
    values = c("KDE" = COLOR_LINE)
  ) +
  scale_linetype_manual(
    name = "",
    values = c("Mean" = "dashed", "Median" = "dotted"),
    labels = c(paste0("Mean: ", mean_dur, " min"),
               paste0("Median: ", median_dur, " min"))
  ) +
  scale_y_continuous(
    name = "Number of Movies",
    labels = comma_fmt,
    sec.axis = sec_axis(~ . / (length(movie_durations) * bin_width),
                        name = "Density")
  ) +
  labs(
    title = "Movie Duration Distribution",
    x = "Duration (minutes)"
  ) +
  custom_theme() +
  theme(
    axis.title.y.right = element_text(color = COLOR_LINE, margin = margin(l = 8)),
    axis.text.y.right = element_text(color = COLOR_LINE),
    legend.position = c(0.85, 0.85),
    legend.background = element_rect(fill = "white", color = "#D0D0D0", linewidth = 0.3),
    legend.key = element_blank()
  )

ggsave(file.path(figures_dir, "fig7_movie_duration.png"), plot = p7,
       width = 10, height = 5, dpi = 150)


# ------------------------------------------------------------------------------
# Figure 8: TV Show Seasons Distribution (1 to 15 seasons)
# ------------------------------------------------------------------------------
message("Generating Figure 8: TV Show Seasons Distribution...")
tv_seasons <- df %>%
  filter(type == "TV Show", !is.na(num_seasons), num_seasons <= 15) %>%
  count(num_seasons) %>%
  mutate(season_factor = factor(num_seasons, levels = 1:15))

palette_seasons <- colorRampPalette(MUTED_COLORS)(nrow(tv_seasons))

p8 <- ggplot(tv_seasons, aes(x = season_factor, y = n, fill = season_factor)) +
  geom_col(color = "white", linewidth = 0.5, width = 0.7, show.legend = FALSE) +
  scale_fill_manual(values = palette_seasons) +
  geom_text(aes(label = format(n, big.mark = ",")),
            vjust = -0.5, size = 3.2, color = "#222222") +
  scale_y_continuous(labels = comma_fmt, expand = expansion(mult = c(0, 0.12))) +
  labs(
    title = "TV Show Seasons Distribution",
    x = "Number of Seasons",
    y = "Number of TV Shows"
  ) +
  custom_theme() +
  theme(
    panel.grid.major.x = element_blank()
  )

ggsave(file.path(figures_dir, "fig8_tv_seasons.png"), plot = p8,
       width = 9, height = 5, dpi = 150)

message("All 8 visualizations successfully generated and saved to: ", figures_dir)
