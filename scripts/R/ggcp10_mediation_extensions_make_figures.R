# =============================================================================
# ggcp10_mediation_extensions_make_figures.R
# Purpose: Figures for GLEAM mean, wet-state mirror, and dry top3 extensions.
# =============================================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(readr)
  library(stringr)
})

set.seed(42)

rootdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
extdir <- file.path(rootdir, "temp/2026-05-19_ggcp10_mediation_extensions")

theme_ext <- theme_minimal(base_size = 11, base_family = "sans") +
  theme(
    panel.grid.minor = element_blank(),
    strip.text = element_text(face = "bold", size = 10),
    legend.position = "bottom",
    plot.title = element_text(face = "bold", size = 13),
    plot.subtitle = element_text(size = 9.5, color = "grey35"),
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA)
  )

hazard_labels <- c(drought = "Drought", heat = "Heat", hotdry = "HotDry")
sm_colors <- c("GLEAM-Sfc" = "#2E7D32", "GLEAM-Root" = "#1565C0")
ca_colors <- c("P25" = "#D55E00", "P50" = "#009E73", "P75" = "#0072B2")
window_colors <- c("v3pre30" = "#D55E00", "v3he" = "#009E73", "hema" = "#0072B2", "fullnew" = "#CC79A7")
dry_tag_colors <- c("mdf_p10_fn" = "#D55E00", "sdf_p10_fn" = "#009E73", "dur_p10_fn" = "#0072B2")

save_plot <- function(plot, path, width = 9, height = 6.5) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  ggsave(path, plot, width = width, height = height, dpi = 300, bg = "white")
}

# -----------------------------------------------------------------------------
# Mean branch
# -----------------------------------------------------------------------------
mean_dir <- file.path(extdir, "mean")
mean_figdir <- file.path(mean_dir, "figures")
dir.create(mean_figdir, recursive = TRUE, showWarnings = FALSE)

mean_coef <- read_csv(file.path(mean_dir, "ggcp10_mean_baseline_coefficients.csv"),
                      show_col_types = FALSE) %>%
  mutate(
    hazard = factor(hazard, levels = names(hazard_labels)),
    window = factor(window, levels = c("v3pre30", "v3he", "hema", "fullnew")),
    sm_label = factor(sm_label, levels = names(sm_colors)),
    fill_group = if_else(p < 0.05, as.character(sm_label), "n.s."),
    lo = b - 1.96 * se,
    hi = b + 1.96 * se
  )

path_specs <- tibble::tribble(
  ~term,        ~equation,  ~path, ~label,
  "Main",       "mediator", "a1",  "a1: Hazard -> SM mean",
  "SR_x_Main",  "mediator", "a3",  "a3: SR x Hazard -> SM mean",
  "SR_x_Main",  "outcome",  "c3",  "c3: SR x Hazard -> ln(Y)",
  "M",          "outcome",  "b",   "b: SM mean -> ln(Y)"
)

for (hz in names(hazard_labels)) {
  for (i in seq_len(nrow(path_specs))) {
    spec <- path_specs[i, ]
    dat <- mean_coef %>%
      filter(hazard == hz, term == spec$term, equation == spec$equation)
    p <- ggplot(dat, aes(x = b, y = sm_label, color = sm_label)) +
      geom_vline(xintercept = 0, color = "black", linewidth = 0.45) +
      geom_pointrange(aes(xmin = lo, xmax = hi, fill = fill_group),
                      shape = 21, size = 0.8, stroke = 1.1, linewidth = 0.8) +
      scale_color_manual(values = sm_colors, name = "SM layer") +
      scale_fill_manual(values = c(sm_colors, "n.s." = "white"), guide = "none") +
      facet_wrap(~ window, ncol = 1, scales = "free_x") +
      labs(
        title = paste(hazard_labels[[hz]], "-", spec$label),
        subtitle = "Four windows; 95% CI; solid point = p < 0.05; hollow point = n.s.",
        x = "Coefficient",
        y = NULL
      ) +
      theme_ext +
      theme(axis.text.y = element_blank(), axis.ticks.y = element_blank())
    save_plot(p, file.path(mean_figdir, sprintf("mean_%s_%s.png", hz, spec$path)),
              width = 8.2, height = 8.2)
  }
}

mean_boot <- read_csv(file.path(mean_dir, "ggcp10_mean_bootstrap_iede.csv"),
                      show_col_types = FALSE) %>%
  mutate(
    hazard = factor(hazard, levels = names(hazard_labels)),
    window = factor(window, levels = c("v3pre30", "v3he", "hema", "fullnew")),
    sm_label = factor(sm_label, levels = names(sm_colors)),
    effect = factor(effect, levels = c("IE", "DE", "TE")),
    ca_level = factor(ca_level, levels = c("P25", "P50", "P75")),
    fill_group = if_else(ci_lo * ci_hi > 0, as.character(ca_level), "n.s.")
  )

for (hz in names(hazard_labels)) {
  dat <- mean_boot %>% filter(hazard == hz)
  p <- ggplot(dat, aes(x = window, y = point_est, color = ca_level, group = ca_level)) +
    geom_hline(yintercept = 0, color = "black", linewidth = 0.4) +
    geom_pointrange(aes(ymin = ci_lo, ymax = ci_hi, fill = fill_group),
                    shape = 21, size = 0.75, stroke = 1.05,
                    position = position_dodge(width = 0.35), linewidth = 0.7) +
    scale_color_manual(values = ca_colors, name = "SR level") +
    scale_fill_manual(values = c(ca_colors, "n.s." = "white"), guide = "none") +
    facet_grid(effect ~ sm_label, scales = "free_y") +
    labs(
      title = paste(hazard_labels[[hz]], "- bootstrap IE / DE / TE"),
      subtitle = "Bias-corrected bootstrap interval when available; solid point = CI excludes 0; hollow point = CI crosses 0.",
      x = NULL,
      y = "Effect",
      color = "SR level"
    ) +
    theme_ext
  save_plot(p, file.path(mean_figdir, sprintf("mean_%s_bootstrap.png", hz)))
}

mean_het <- read_csv(file.path(mean_dir, "ggcp10_mean_heterogeneity_effects.csv"),
                     show_col_types = FALSE) %>%
  mutate(
    hazard = factor(hazard, levels = names(hazard_labels)),
    window = factor(window, levels = c("v3pre30", "v3he", "hema", "fullnew")),
    sm_label = factor(sm_label, levels = names(sm_colors)),
    effect = factor(effect, levels = c("IE", "DE")),
    fill_group = "n.s."
  )

for (hz in names(hazard_labels)) {
  for (sp in c("irr", "zone")) {
    dat <- mean_het %>% filter(hazard == hz, split_type == sp)
    p <- ggplot(dat, aes(x = subgroup, y = value, color = window, group = window)) +
      geom_hline(yintercept = 0, color = "black", linewidth = 0.4) +
      geom_point(aes(fill = fill_group), shape = 21, stroke = 1.05,
                 position = position_dodge(width = 0.45), size = 2.5) +
      scale_color_manual(values = window_colors, name = "Window") +
      scale_fill_manual(values = c("n.s." = "white"), guide = "none") +
      facet_grid(effect ~ sm_label, scales = "free_y") +
      labs(
        title = paste(hazard_labels[[hz]], "-", ifelse(sp == "irr", "Irrigation heterogeneity", "Maize-zone heterogeneity")),
        subtitle = "Conditional effects at subgroup-specific SR median; IE/DE effect CSV has no inference interval, so points are shown hollow.",
        x = NULL,
        y = "Effect",
        color = "Window"
      ) +
      theme_ext
    save_plot(p, file.path(mean_figdir, sprintf("mean_%s_het_%s.png", hz, sp)))
  }
}

# -----------------------------------------------------------------------------
# Wet mirror branch
# -----------------------------------------------------------------------------
wet_dir <- file.path(extdir, "wet_mirror")
wet_figdir <- file.path(wet_dir, "figures")
dir.create(wet_figdir, recursive = TRUE, showWarnings = FALSE)

wet_coef <- read_csv(file.path(wet_dir, "ggcp10_wet_mirror_baseline_coefficients.csv"),
                     show_col_types = FALSE) %>%
  mutate(
    hazard = factor(hazard, levels = names(hazard_labels)),
    sm_label = factor(sm_label, levels = names(sm_colors)),
    fill_group = if_else(p < 0.05, as.character(sm_label), "n.s."),
    row_lbl = case_when(
      metric_family == "mdduration_wet" ~ "md-duration   | md",
      metric_family == "mddurshare_wet" ~ "md-durshare   | md",
      metric_family == "mdseverity_wet" ~ "md-severity   | md",
      metric_family == "blduration_wet" & wet_pct == "p90" ~ "bl-duration   | p90",
      metric_family == "blduration_wet" & wet_pct == "p80" ~ "bl-duration   | p80",
      metric_family == "bldurshare_wet" & wet_pct == "p90" ~ "bl-durshare   | p90",
      metric_family == "bldurshare_wet" & wet_pct == "p80" ~ "bl-durshare   | p80",
      metric_family == "blseveritymean_wet" & wet_pct == "p90" ~ "bl-sev-mean   | p90",
      metric_family == "blseveritymean_wet" & wet_pct == "p80" ~ "bl-sev-mean   | p80",
      metric_family == "blseveritysum_wet" & wet_pct == "p90" ~ "bl-sev-sum    | p90",
      metric_family == "blseveritysum_wet" & wet_pct == "p80" ~ "bl-sev-sum    | p80",
      TRUE ~ NA_character_
    ),
    row_lbl = factor(row_lbl, levels = c(
      "bl-duration   | p90", "bl-duration   | p80",
      "bl-durshare   | p90", "bl-durshare   | p80",
      "bl-sev-mean   | p90", "bl-sev-mean   | p80",
      "bl-sev-sum    | p90", "bl-sev-sum    | p80",
      "md-duration   | md", "md-durshare   | md", "md-severity   | md"
    )),
    lo = b - 1.96 * se,
    hi = b + 1.96 * se
  )

wet_specs <- tibble::tribble(
  ~term,        ~equation,  ~path, ~label,
  "Main",       "mediator", "a1",  "a1: Hazard -> M_wet",
  "SR_x_Main",  "mediator", "a3",  "a3: SR x Hazard -> M_wet",
  "SR_x_Main",  "outcome",  "c3",  "c3: SR x Hazard -> ln(Y)",
  "M",          "outcome",  "b",   "b: M_wet -> ln(Y)"
)

for (hz in names(hazard_labels)) {
  for (i in seq_len(nrow(wet_specs))) {
    spec <- wet_specs[i, ]
    dat <- wet_coef %>% filter(hazard == hz, term == spec$term, equation == spec$equation)
    p <- ggplot(dat, aes(x = b, y = sm_label, color = sm_label)) +
      geom_vline(xintercept = 0, color = "black", linewidth = 0.45) +
      geom_pointrange(aes(xmin = lo, xmax = hi, fill = fill_group),
                      shape = 21, size = 0.8, stroke = 1.1, linewidth = 0.8) +
      scale_color_manual(values = sm_colors, name = "SM layer") +
      scale_fill_manual(values = c(sm_colors, "n.s." = "white"), guide = "none") +
      facet_wrap(~ row_lbl, ncol = 1, scales = "free_x", strip.position = "left") +
      labs(
        title = paste(hazard_labels[[hz]], "-", spec$label),
        subtitle = "GLEAM wet-state full-family; full-season only; solid point = p < 0.05; hollow point = n.s.",
        x = "Coefficient",
        y = NULL
      ) +
      theme_ext +
      theme(
        strip.placement = "outside",
        strip.text.y.left = element_text(angle = 0, hjust = 1, family = "mono", size = 9),
        axis.text.y = element_blank(),
        axis.ticks.y = element_blank()
      )
    save_plot(p, file.path(wet_figdir, sprintf("wet_%s_%s.png", hz, spec$path)),
              width = 8.5, height = 9)
  }
}

# -----------------------------------------------------------------------------
# Dry top3 branch
# -----------------------------------------------------------------------------
dry_dir <- file.path(extdir, "dry_top3")
dry_figdir <- file.path(dry_dir, "figures")
dir.create(dry_figdir, recursive = TRUE, showWarnings = FALSE)

dry_coef <- read_csv(file.path(dry_dir, "ggcp10_dry_top3_baseline_coefficients.csv"),
                     show_col_types = FALSE) %>%
  mutate(
    hazard = factor(hazard, levels = names(hazard_labels)),
    sample_tag = factor(sample_tag, levels = c("mdf_p10_fn", "sdf_p10_fn", "dur_p10_fn")),
    row_lbl = recode(sample_tag,
      "mdf_p10_fn" = "bl-sev-mean | p10 | GLEAM-Sfc",
      "sdf_p10_fn" = "bl-sev-sum  | p10 | GLEAM-Root",
      "dur_p10_fn" = "bl-duration | p10 | GLEAM-Sfc"
    ),
    fill_group = if_else(p < 0.05, as.character(sample_tag), "n.s."),
    lo = b - 1.96 * se,
    hi = b + 1.96 * se
  )

dry_specs <- tibble::tribble(
  ~term,        ~equation,  ~path, ~label,
  "Main",       "mediator", "a1",  "a1: Hazard -> M_dry",
  "SR_x_Main",  "mediator", "a3",  "a3: SR x Hazard -> M_dry",
  "SR_x_Main",  "outcome",  "c3",  "c3: SR x Hazard -> ln(Y)",
  "M",          "outcome",  "b",   "b: M_dry -> ln(Y)"
)

for (hz in names(hazard_labels)) {
  for (i in seq_len(nrow(dry_specs))) {
    spec <- dry_specs[i, ]
    dat <- dry_coef %>% filter(hazard == hz, term == spec$term, equation == spec$equation)
    p <- ggplot(dat, aes(x = b, y = row_lbl, color = sample_tag)) +
      geom_vline(xintercept = 0, color = "black", linewidth = 0.45) +
      geom_pointrange(aes(xmin = lo, xmax = hi, fill = fill_group),
                      shape = 21, size = 0.8, stroke = 1.1, linewidth = 0.8) +
      scale_color_manual(values = dry_tag_colors, name = NULL) +
      scale_fill_manual(values = c(dry_tag_colors, "n.s." = "white"), guide = "none") +
      labs(
        title = paste(hazard_labels[[hz]], "-", spec$label),
        subtitle = "Selected three dry-state mediators; solid point = p < 0.05; hollow point = n.s.",
        x = "Coefficient",
        y = NULL,
        color = NULL
      ) +
      theme_ext
    save_plot(p, file.path(dry_figdir, sprintf("dry_top3_%s_%s.png", hz, spec$path)),
              width = 8.2, height = 4.8)
  }
}

dry_boot <- read_csv(file.path(dry_dir, "ggcp10_dry_top3_bootstrap_iede.csv"),
                     show_col_types = FALSE) %>%
  mutate(
    hazard = factor(hazard, levels = names(hazard_labels)),
    sample_tag = factor(sample_tag, levels = c("mdf_p10_fn", "sdf_p10_fn", "dur_p10_fn")),
    effect = factor(effect, levels = c("IE", "DE")),
    ca_level = factor(ca_level, levels = c("P25", "P50", "P75")),
    fill_group = if_else(ci_lo * ci_hi > 0, as.character(sample_tag), "n.s.")
  )

for (hz in names(hazard_labels)) {
  dat <- dry_boot %>% filter(hazard == hz)
  p <- ggplot(dat, aes(x = ca_level, y = point_est, color = sample_tag, group = sample_tag)) +
    geom_hline(yintercept = 0, color = "black", linewidth = 0.4) +
    geom_pointrange(aes(ymin = ci_lo, ymax = ci_hi, fill = fill_group),
                    shape = 21, size = 0.75, stroke = 1.05,
                    position = position_dodge(width = 0.4), linewidth = 0.7) +
    scale_color_manual(values = dry_tag_colors, name = "Mediator") +
    scale_fill_manual(values = c(dry_tag_colors, "n.s." = "white"), guide = "none") +
    facet_wrap(~ effect, scales = "free_y", ncol = 1) +
    labs(
      title = paste(hazard_labels[[hz]], "- bootstrap IE / DE"),
      subtitle = "Bias-corrected bootstrap interval when available; solid point = CI excludes 0; hollow point = CI crosses 0.",
      x = "SR level",
      y = "Effect",
      color = "Mediator"
    ) +
    theme_ext
  save_plot(p, file.path(dry_figdir, sprintf("dry_top3_%s_bootstrap.png", hz)))
}

dry_het <- read_csv(file.path(dry_dir, "ggcp10_dry_top3_heterogeneity_effects.csv"),
                    show_col_types = FALSE) %>%
  mutate(
    hazard = factor(hazard, levels = names(hazard_labels)),
    sample_tag = factor(sample_tag, levels = c("mdf_p10_fn", "sdf_p10_fn", "dur_p10_fn")),
    effect = factor(effect, levels = c("IE", "DE")),
    fill_group = "n.s."
  )

for (hz in names(hazard_labels)) {
  for (sp in c("irr", "zone")) {
    dat <- dry_het %>% filter(hazard == hz, split_type == sp)
    p <- ggplot(dat, aes(x = subgroup, y = value, color = sample_tag, group = sample_tag)) +
      geom_hline(yintercept = 0, color = "black", linewidth = 0.4) +
      geom_point(aes(fill = fill_group), shape = 21, stroke = 1.05,
                 position = position_dodge(width = 0.45), size = 2.5) +
      scale_color_manual(values = dry_tag_colors, name = "Mediator") +
      scale_fill_manual(values = c("n.s." = "white"), guide = "none") +
      facet_wrap(~ effect, scales = "free_y", ncol = 1) +
      labs(
        title = paste(hazard_labels[[hz]], "-", ifelse(sp == "irr", "Irrigation heterogeneity", "Maize-zone heterogeneity")),
        subtitle = "Conditional effects at subgroup-specific SR median; IE/DE effect CSV has no inference interval, so points are shown hollow.",
        x = NULL,
        y = "Effect",
        color = "Mediator"
      ) +
      theme_ext
    save_plot(p, file.path(dry_figdir, sprintf("dry_top3_%s_het_%s.png", hz, sp)))
  }
}

cat("=== ggcp10_mediation_extensions_make_figures.R COMPLETE ===\n")
quit(save = "no", status = 0, runLast = FALSE)
