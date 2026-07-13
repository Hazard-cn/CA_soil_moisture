# =============================================================================
# v3prhdsm_coefplots.R
# Purpose: Coefficient plots for Soil Moisture spec2/spec3/spec4 beamer report
# Input:   output/tables/v3prhdsm_results_long.csv
# Output:  output/figures/v3prhdsm_plot_*.png
# =============================================================================

set.seed(42)

library(ggplot2)
library(dplyr)

projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
tabdir  <- file.path(projdir, "output/tables")
figdir  <- file.path(projdir, "output/figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

d <- read.csv(file.path(tabdir, "v3prhdsm_results_long.csv"), stringsAsFactors = FALSE)

outcome_levels <- c(
  "gleam_sms_mean",
  "gleam_smrz_mean",
  "swsm_l1_mean",
  "swsm_l3_mean",
  "era5l_swvl1_mean",
  "era5l_swvl3_mean"
)

outcome_labels <- c(
  "gleam_sms_mean" = "GLEAM Surface",
  "gleam_smrz_mean" = "GLEAM Rootzone",
  "swsm_l1_mean" = "SWSM Layer 1",
  "swsm_l3_mean" = "SWSM Layer 3",
  "era5l_swvl1_mean" = "ERA5-Land Layer 1",
  "era5l_swvl3_mean" = "ERA5-Land Layer 3"
)

outcome_colors <- c(
  "GLEAM Surface" = "#2E8B57",
  "GLEAM Rootzone" = "#0B5D3D",
  "SWSM Layer 1" = "#F39C12",
  "SWSM Layer 3" = "#D35400",
  "ERA5-Land Layer 1" = "#3498DB",
  "ERA5-Land Layer 3" = "#1F4E79"
)

spec_labels <- c("spec2" = "Spec 2", "spec3" = "Spec 3", "spec4" = "Spec 4")
cut_labels <- c(
  "i" = "i Full",
  "ii" = "ii V3pm10 + HEpm10",
  "iii" = "iii V3HE + HEMA",
  "iv" = "iv V3pre30 + V3HE + HEMA"
)

panel_levels <- c(
  "i_full",
  "ii_v3pm10",
  "ii_hepm10",
  "iii_v3he",
  "iii_hema",
  "iv_v3pre30",
  "iv_v3he",
  "iv_hema",
  "i_overall",
  "ii_overall",
  "iii_overall",
  "iv_overall"
)

panel_labels <- c(
  "i_full" = "i | Full",
  "ii_v3pm10" = "ii | V3pm10",
  "ii_hepm10" = "ii | HEpm10",
  "iii_v3he" = "iii | V3HE",
  "iii_hema" = "iii | HEMA",
  "iv_v3pre30" = "iv | V3pre30",
  "iv_v3he" = "iv | V3HE",
  "iv_hema" = "iv | HEMA",
  "i_overall" = "i | Overall",
  "ii_overall" = "ii | Overall",
  "iii_overall" = "iii | Overall",
  "iv_overall" = "iv | Overall"
)

term_label <- function(term) {
  dplyr::case_when(
    term == "ca" ~ "SR",
    grepl("^SR_x_D_x_Heat_", term) ~ "SR x D x H",
    grepl("^D_x_Heat_", term) ~ "D x H",
    grepl("^SR_x_HotDryPr_", term) ~ "SR x HotDryPr",
    grepl("^HotDryPr_", term) ~ "HotDryPr",
    grepl("^SR_x_Heat_", term) ~ "SR x H",
    grepl("^SR_x_D_", term) ~ "SR x D",
    grepl("^hdd_ge32", term) ~ "H",
    grepl("^D_", term) ~ "D",
    TRUE ~ term
  )
}

base_theme <- theme_minimal(base_size = 12, base_family = "sans") +
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.y = element_blank(),
    panel.grid.major.x = element_line(color = "grey90", linewidth = 0.45),
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    strip.text = element_text(face = "bold", size = 11),
    legend.position = "bottom",
    legend.title = element_blank(),
    legend.text = element_text(size = 10),
    axis.text.y = element_text(size = 10.5),
    axis.text.x = element_text(size = 10),
    axis.title.x = element_text(size = 11),
    plot.title = element_text(face = "bold", size = 15)
  )

prep_common <- function(df) {
  df %>%
    mutate(
      plot_window = dplyr::case_when(
        window == "overall" & grepl("^D_full$|^SR_x_D_full$|^SR_x_Heat_full$|^D_x_Heat_full$|^SR_x_D_x_Heat_full$|^HotDryPr_full$|^SR_x_HotDryPr_full$|^hdd_ge32$", term) ~ "full",
        TRUE ~ window
      ),
      panel_key = paste(cut, plot_window, sep = "_"),
      outcome = factor(outcome, levels = rev(outcome_levels), labels = rev(outcome_labels[outcome_levels])),
      spec = factor(spec, levels = c("spec2", "spec3", "spec4"), labels = spec_labels[c("spec2", "spec3", "spec4")]),
      term_group = term_label(term),
      panel = factor(panel_key, levels = panel_levels, labels = panel_labels[panel_levels]),
      ci_lo = b - 1.96 * se,
      ci_hi = b + 1.96 * se
    )
}

plot_compare_single_term <- function(df, term_keep, specs_keep, plot_title) {
  dd <- df %>%
    prep_common() %>%
    filter(term_group == term_keep, spec %in% specs_keep)

  dodge_pos <- position_dodge(width = 0.62)

  ggplot(dd, aes(x = b, y = outcome, color = outcome)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
    geom_linerange(
      aes(xmin = ci_lo, xmax = ci_hi, group = interaction(outcome, spec)),
      position = dodge_pos,
      orientation = "y",
      linewidth = 0.8
    ) +
    geom_point(aes(shape = spec), position = dodge_pos, size = 2.5, stroke = 0.4, fill = "white") +
    scale_color_manual(values = outcome_colors, breaks = names(outcome_colors)) +
    scale_shape_manual(values = c("Spec 2" = 16, "Spec 3" = 17, "Spec 4" = 15)) +
    facet_wrap(~panel, ncol = 4, scales = "free_x") +
    labs(
      title = plot_title,
      x = "Coefficient (95% CI)",
      y = NULL
    ) +
    guides(
      color = guide_legend(order = 1, nrow = 2),
      shape = guide_legend(order = 2, nrow = 1)
    ) +
    base_theme
}

plot_compare_terms <- function(df, terms_keep, plot_title) {
  dd <- df %>%
    prep_common() %>%
    filter(term_group %in% terms_keep, spec %in% c("Spec 3", "Spec 4"))

  dodge_pos <- position_dodge(width = 0.62)

  ggplot(dd, aes(x = b, y = outcome, color = outcome, shape = spec)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
    geom_linerange(
      aes(xmin = ci_lo, xmax = ci_hi),
      position = dodge_pos,
      orientation = "y",
      linewidth = 0.8,
      alpha = 0.95
    ) +
    geom_point(position = dodge_pos, size = 2.5, stroke = 0.4, fill = "white") +
    scale_color_manual(values = outcome_colors, breaks = names(outcome_colors)) +
    scale_shape_manual(values = c("Spec 3" = 16, "Spec 4" = 17)) +
    facet_grid(term_group ~ panel, scales = "free_x") +
    labs(
      title = plot_title,
      x = "Coefficient (95% CI)",
      y = NULL
    ) +
    guides(
      color = guide_legend(order = 1, nrow = 2),
      shape = guide_legend(order = 2, nrow = 1)
    ) +
    base_theme
}

plot_spec2_compound <- function(df) {
  dd <- df %>%
    prep_common() %>%
    filter(spec == "Spec 2", term_group %in% c("D x H", "SR x D x H"))

  ggplot(dd, aes(x = b, y = outcome, color = outcome)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
    geom_linerange(aes(xmin = ci_lo, xmax = ci_hi), orientation = "y", linewidth = 0.8) +
    geom_point(size = 2.6) +
    scale_color_manual(values = outcome_colors, breaks = names(outcome_colors)) +
    facet_grid(term_group ~ panel, scales = "free_x") +
    labs(
      title = "Spec 2: D x H and SR x D x H",
      x = "Coefficient (95% CI)",
      y = NULL
    ) +
    base_theme
}

p1 <- plot_compare_single_term(d, "SR x D", c("Spec 2", "Spec 3"),
                               "SR x D: Spec 2 vs Spec 3")
p2 <- plot_compare_single_term(d, "SR x H", c("Spec 2", "Spec 3"),
                               "SR x H: Spec 2 vs Spec 3")
p3 <- plot_spec2_compound(d)
p4 <- plot_compare_terms(d, c("HotDryPr", "SR x HotDryPr"),
                         "HotDryPr Terms: Spec 3 vs Spec 4")
p5 <- plot_compare_terms(d, c("SR"),
                         "SR Main Effect: Spec 3 vs Spec 4")

ggsave(file.path(figdir, "v3prhdsm_plot_srd_compare.png"), p1,
       width = 15.6, height = 4.8, dpi = 300, bg = "white")
ggsave(file.path(figdir, "v3prhdsm_plot_srh_compare.png"), p2,
       width = 15.6, height = 4.8, dpi = 300, bg = "white")
ggsave(file.path(figdir, "v3prhdsm_plot_compound_spec2.png"), p3,
       width = 16, height = 7.4, dpi = 300, bg = "white")
ggsave(file.path(figdir, "v3prhdsm_plot_hotdry_compare.png"), p4,
       width = 16, height = 7.4, dpi = 300, bg = "white")
ggsave(file.path(figdir, "v3prhdsm_plot_sr_compare.png"), p5,
       width = 16, height = 4.8, dpi = 300, bg = "white")

cat("Saved v3prhdsm plots to:", figdir, "\n")
