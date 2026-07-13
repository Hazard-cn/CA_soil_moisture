# =============================================================================
# v6gleambl_agg_fullfamily_make_figures.R
# Purpose: Full-family coefficient figures for the GGCP10 aggregated-area rerun.
# Scope: fullnew only, 22 dry-side GLEAM spec cells, three stressor groups.
# =============================================================================

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(readr)
  library(stringr)
  library(tibble)
})

set.seed(42)

rundir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR/temp/2026-05-18_ggcp10_harvarea_agg_v6gleambl_fullfamily"
figdir <- file.path(rundir, "figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

old_pngs <- list.files(figdir, pattern = "^v6gleambl_agg_", full.names = TRUE)
if (length(old_pngs)) file.remove(old_pngs)

sm_levels <- c("GLEAM-Sfc", "GLEAM-Root")
sm_colors <- c("GLEAM-Sfc" = "#2E7D32", "GLEAM-Root" = "#66BB6A")

row_levels <- c(
  "bl-duration   | p10",
  "bl-duration   | p20",
  "bl-durshare   | p10",
  "bl-durshare   | p20",
  "bl-sev-mean   | p10",
  "bl-sev-mean   | p20",
  "bl-sev-sum    | p10",
  "bl-sev-sum    | p20",
  "md-duration   | md",
  "md-durshare   | md",
  "md-severity   | md"
)

metric_row <- function(metric_family, dry_pct) {
  key <- paste(metric_family, ifelse(is.na(dry_pct), "md", dry_pct), sep = "_")
  dplyr::recode(
    key,
    "blduration_dry_p10"     = row_levels[1],
    "blduration_dry_p20"     = row_levels[2],
    "bldurshare_dry_p10"     = row_levels[3],
    "bldurshare_dry_p20"     = row_levels[4],
    "blseveritymean_ddf_p10" = row_levels[5],
    "blseveritymean_ddf_p20" = row_levels[6],
    "blseveritysum_ddf_p10"  = row_levels[7],
    "blseveritysum_ddf_p20"  = row_levels[8],
    "mdduration_dry_md"      = row_levels[9],
    "mddurshare_dry_md"      = row_levels[10],
    "mdseverity_dry_md"      = row_levels[11]
  )
}

theme_v6 <- theme_minimal(base_size = 11, base_family = "sans") +
  theme(
    panel.grid.minor = element_blank(),
    strip.text = element_text(face = "bold", size = 11),
    legend.position = "bottom",
    plot.title = element_text(face = "bold", size = 13),
    plot.subtitle = element_text(size = 9.5, color = "grey35"),
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA)
  )

plot_group <- function(csv_file, tag, stressor_label, a1_term, a3_term, c3_term) {
  path_spec <- tribble(
    ~path, ~equation, ~term,    ~title_txt,
    "a1",  "mediator","a1_term", sprintf("a1: %s -> M_dry", stressor_label),
    "a3",  "mediator","a3_term", sprintf("a3: SR x %s -> M_dry", stressor_label),
    "c3",  "outcome", "c3_term", sprintf("c3: SR x %s -> ln(Y)", stressor_label),
    "b",   "outcome", "M_dry",   "b: M_dry -> ln(Y)"
  )
  term_lookup <- c(a1_term = a1_term, a3_term = a3_term, c3_term = c3_term)
  path_spec$term <- ifelse(
    path_spec$term %in% names(term_lookup),
    term_lookup[path_spec$term],
    path_spec$term
  )

  raw <- read_csv(file.path(rundir, csv_file), show_col_types = FALSE) %>%
    mutate(term = str_trim(term)) %>%
    filter(window == "fullnew") %>%
    mutate(
      dry_pct = ifelse(dry_pct %in% c(".", "", NA), NA_character_, dry_pct),
      row_lbl = metric_row(metric_family, dry_pct),
      sm_label = factor(sm_label, levels = sm_levels),
      row_lbl = factor(row_lbl, levels = row_levels)
    )

  paths <- raw %>%
    semi_join(path_spec, by = c("equation", "term")) %>%
    left_join(path_spec %>% select(equation, term, path, title_txt),
              by = c("equation", "term")) %>%
    mutate(
      b = as.numeric(b),
      se = as.numeric(se),
      lo = b - 1.96 * se,
      hi = b + 1.96 * se
    )

  stopifnot(paths %>% distinct(row_lbl, sm_label) %>% nrow() == 22)

  for (pth in c("a1", "a3", "c3", "b")) {
    dat <- paths %>% filter(path == pth)
    meta <- path_spec %>% filter(path == pth)
    rng <- dat %>%
      group_by(row_lbl) %>%
      summarise(xm = max(abs(c(lo, hi)), na.rm = TRUE) * 1.10, .groups = "drop")
    blank <- bind_rows(
      rng %>% transmute(row_lbl, b = -xm, lo = -xm, hi = -xm,
                        sm_label = factor("GLEAM-Sfc", levels = sm_levels)),
      rng %>% transmute(row_lbl, b =  xm, lo =  xm, hi =  xm,
                        sm_label = factor("GLEAM-Sfc", levels = sm_levels))
    )

    p <- ggplot(dat, aes(x = b, y = sm_label, color = sm_label)) +
      geom_vline(xintercept = 0, color = "black", linewidth = 0.5) +
      geom_pointrange(aes(xmin = lo, xmax = hi),
                      size = 0.55, linewidth = 0.8) +
      geom_blank(data = blank) +
      scale_color_manual(values = sm_colors, name = "SM layer") +
      facet_wrap(~ row_lbl, ncol = 1, scales = "free_x",
                 strip.position = "left") +
      labs(
        title = meta$title_txt,
        subtitle = "GLEAM dry-side full-family, full-season only. Per-panel x-axis symmetric around 0.",
        x = "Coefficient (95% CI)",
        y = NULL
      ) +
      theme_v6 +
      theme(
        strip.placement = "outside",
        strip.text.y.left = element_text(angle = 0, hjust = 1, family = "mono", size = 9),
        panel.spacing.y = unit(0.25, "lines"),
        axis.text.y = element_blank(),
        axis.ticks.y = element_blank(),
        panel.grid.major.y = element_blank()
      )

    outfile <- file.path(figdir, sprintf("v6gleambl_agg_%s_fig_%s.png", tag, pth))
    ggsave(outfile, p, width = 8.5, height = 9, dpi = 300, bg = "white")
  }
}

plot_group(
  "v6gleambl_agg_nomwet_baseline_coefficients.csv",
  "drought",
  "D",
  "D_w",
  "SR_x_D_w",
  "SR_x_D_w"
)

plot_group(
  "v6gleambl_agg_heatctrl_baseline_coefficients.csv",
  "heat",
  "H",
  "H_main",
  "SR_x_H",
  "SR_x_H"
)

plot_group(
  "v6gleambl_agg_hotdryctrl_baseline_coefficients.csv",
  "hotdry",
  "HotDry",
  "HotDry_main",
  "SR_x_HotDry",
  "SR_x_HotDry"
)

cat("=== v6gleambl_agg_fullfamily_make_figures.R COMPLETE ===\n")
