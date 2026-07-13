# =============================================================================
# v3prhd_coefplots.R
# Purpose: Cross-equation coefficient plots for v3prhd beamer report
# Input:   output/tables/v3prhd_results_long.csv
# Output:  output/figures/v3prhd_plot_compare_*.png
# =============================================================================

set.seed(42)

library(ggplot2)
library(dplyr)
library(patchwork)

projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
tabdir  <- file.path(projdir, "output/tables")
figdir  <- file.path(projdir, "output/figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

d <- read.csv(file.path(tabdir, "v3prhd_results_long.csv"), stringsAsFactors = FALSE)

spec_labels <- c(
  "spec1" = "Spec 1",
  "spec2" = "Spec 2",
  "spec3" = "Spec 3",
  "spec4" = "Spec 4"
)

spec_colors <- c(
  "Spec 1" = "#3C4A57",
  "Spec 2" = "#2F7ED8",
  "Spec 3" = "#35A854",
  "Spec 4" = "#8E44AD"
)

coef_colors <- c(
  "D x H" = "#F16913",
  "SR x D x H" = "#7A1FA2"
)

group_levels <- c(
  "i_full",
  "ii_hepm10",
  "ii_v3pm10",
  "iii_hema",
  "iii_v3he",
  "iv_hema",
  "iv_v3he",
  "iv_v3pre30",
  "i_overall",
  "ii_overall",
  "iii_overall",
  "iv_overall"
)

group_labels <- c(
  "i_full" = "i | Full",
  "ii_hepm10" = "ii | HEpm10",
  "ii_v3pm10" = "ii | V3pm10",
  "iii_hema" = "iii | HEMA",
  "iii_v3he" = "iii | V3HE",
  "iv_hema" = "iv | HEMA",
  "iv_v3he" = "iv | V3HE",
  "iv_v3pre30" = "iv | V3pre30",
  "i_overall" = "i | Overall",
  "ii_overall" = "ii | Overall",
  "iii_overall" = "iii | Overall",
  "iv_overall" = "iv | Overall"
)

term_class <- function(x) {
  dplyr::case_when(
    x == "ca" ~ "SR",
    grepl("^SR_x_HotDryPr_", x) ~ "SR x HotDryPr",
    grepl("^HotDryPr_", x) ~ "HotDryPr",
    grepl("^SR_x_D_x_Heat_", x) ~ "SR x D x H",
    grepl("^D_x_Heat_", x) ~ "D x H",
    grepl("^SR_x_Heat_", x) ~ "SR x H",
    grepl("^SR_x_D_", x) ~ "SR x D",
    grepl("^hdd_ge32", x) ~ "H",
    grepl("^D_", x) ~ "D",
    TRUE ~ x
  )
}

group_key_fn <- function(cut, window) {
  dplyr::case_when(
    cut == "i"   & window == "full"    ~ "i_full",
    cut == "ii"  & window == "hepm10"  ~ "ii_hepm10",
    cut == "ii"  & window == "v3pm10"  ~ "ii_v3pm10",
    cut == "iii" & window == "hema"    ~ "iii_hema",
    cut == "iii" & window == "v3he"    ~ "iii_v3he",
    cut == "iv"  & window == "hema"    ~ "iv_hema",
    cut == "iv"  & window == "v3he"    ~ "iv_v3he",
    cut == "iv"  & window == "v3pre30" ~ "iv_v3pre30",
    cut == "i"   & window == "overall" ~ "i_overall",
    cut == "ii"  & window == "overall" ~ "ii_overall",
    cut == "iii" & window == "overall" ~ "iii_overall",
    cut == "iv"  & window == "overall" ~ "iv_overall",
    TRUE ~ NA_character_
  )
}

plot_theme <- theme_minimal(base_size = 12.5, base_family = "sans") +
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.y = element_line(color = "grey88", linewidth = 0.4),
    panel.grid.major.x = element_line(color = "grey90", linewidth = 0.45),
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    legend.position = "bottom",
    legend.title = element_blank(),
    legend.text = element_text(size = 10),
    plot.title = element_text(face = "bold", size = 16),
    axis.text.y = element_text(size = 11),
    axis.text.x = element_text(size = 10.5),
    axis.title.x = element_text(size = 11.5)
  )

make_compare_plot <- function(data, specs_keep, term_keep, plot_title, color_map) {
  dd <- data %>%
    filter(spec %in% specs_keep, term_class == term_keep) %>%
    mutate(
      spec_label = factor(spec, levels = specs_keep, labels = spec_labels[specs_keep]),
      group_key = group_key_fn(cut, window),
      group = factor(group_key, levels = rev(group_levels), labels = rev(group_labels[group_levels])),
      ci_lo = b - 1.96 * se,
      ci_hi = b + 1.96 * se
    ) %>%
    filter(!is.na(group))

  dodge_pos <- position_dodge(width = 0.72)

  ggplot(dd, aes(x = b, y = group, color = spec_label)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.55) +
    geom_errorbar(
      aes(xmin = ci_lo, xmax = ci_hi),
      width = 0.14,
      orientation = "y",
      position = dodge_pos,
      linewidth = 0.72
    ) +
    geom_point(position = dodge_pos, size = 2.85) +
    scale_color_manual(values = color_map, breaks = names(color_map)) +
    labs(title = plot_title, x = "Coefficient (95% CI)", y = NULL) +
    plot_theme
}

make_term_plot <- function(data, spec_keep, terms_keep, plot_title) {
  dd <- data %>%
    filter(spec == spec_keep, term_class %in% terms_keep) %>%
    mutate(
      term_class = factor(term_class, levels = terms_keep),
      group_key = group_key_fn(cut, window),
      group = factor(group_key, levels = rev(group_levels), labels = rev(group_labels[group_levels])),
      ci_lo = b - 1.96 * se,
      ci_hi = b + 1.96 * se
    ) %>%
    filter(!is.na(group))

  dodge_pos <- position_dodge(width = 0.72)

  ggplot(dd, aes(x = b, y = group, color = term_class)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.55) +
    geom_errorbar(
      aes(xmin = ci_lo, xmax = ci_hi),
      width = 0.14,
      orientation = "y",
      position = dodge_pos,
      linewidth = 0.72
    ) +
    geom_point(position = dodge_pos, size = 2.85) +
    scale_color_manual(values = coef_colors[terms_keep], breaks = terms_keep) +
    labs(title = plot_title, x = "Coefficient (95% CI)", y = NULL) +
    plot_theme
}

d_plot <- d %>%
  mutate(term_class = term_class(term))

p_srd <- make_compare_plot(
  d_plot,
  specs_keep = c("spec1", "spec2", "spec3"),
  term_keep = "SR x D",
  plot_title = "SR x D",
  color_map = spec_colors[c("Spec 1", "Spec 2", "Spec 3")]
)

p_srh <- make_compare_plot(
  d_plot,
  specs_keep = c("spec1", "spec2", "spec3"),
  term_keep = "SR x H",
  plot_title = "SR x H",
  color_map = spec_colors[c("Spec 1", "Spec 2", "Spec 3")]
)

p_compound <- make_term_plot(
  d_plot,
  spec_keep = "spec2",
  terms_keep = c("D x H", "SR x D x H"),
  plot_title = "Spec 2: D x H and SR x D x H"
)

p_hotdry <- make_compare_plot(
  d_plot,
  specs_keep = c("spec3", "spec4"),
  term_keep = "HotDryPr",
  plot_title = "HotDryPr",
  color_map = spec_colors[c("Spec 3", "Spec 4")]
)

p_sr_hotdry <- make_compare_plot(
  d_plot,
  specs_keep = c("spec3", "spec4"),
  term_keep = "SR x HotDryPr",
  plot_title = "SR x HotDryPr",
  color_map = spec_colors[c("Spec 3", "Spec 4")]
)

p_sr_paths <- (p_srd | p_srh) + plot_layout(guides = "collect") &
  theme(legend.position = "bottom")

p_hotdry_compare <- (p_hotdry | p_sr_hotdry) + plot_layout(guides = "collect") &
  theme(legend.position = "bottom")

ggsave(file.path(figdir, "v3prhd_plot_compare_sr_paths.png"), p_sr_paths,
       width = 14.8, height = 6.2, dpi = 300, bg = "white")
ggsave(file.path(figdir, "v3prhd_plot_compound_spec2.png"), p_compound,
       width = 10.8, height = 5.6, dpi = 300, bg = "white")
ggsave(file.path(figdir, "v3prhd_plot_compare_hotdry.png"), p_hotdry_compare,
       width = 14.8, height = 6.2, dpi = 300, bg = "white")

cat("Saved v3prhd comparison plots to:", figdir, "\n")
