# =============================================================================
# v3med_plots.R
# Purpose: Coefficient plots, conditional effect plots, and heterogeneity plots
#          for Model 8 moderated mediation analysis.
# Author:  YangSu + Claude
# Date:    2026-04-16
# Input:   output/tables/v3med_*.csv
# Output:  output/figures/v3med_*.png
# =============================================================================

library(ggplot2)
library(dplyr)
library(tidyr)
library(readr)
library(stringr)
library(patchwork)

set.seed(42)

# --- Paths ---
projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
outdir  <- file.path(projdir, "output/tables")
figdir  <- file.path(projdir, "output/figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

# =============================================================================
# THEME & PALETTE
# =============================================================================

theme_coef <- theme_minimal(base_size = 12, base_family = "sans") +
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.y = element_blank(),
    strip.text = element_text(face = "bold", size = 11),
    legend.position = "bottom",
    plot.title = element_text(face = "bold", size = 13),
    plot.subtitle = element_text(size = 10, color = "grey40"),
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    axis.title.y = element_blank()
  )

sig_colors <- c(
  "***" = "#1a237e",
  "**"  = "#1565c0",
  "*"   = "#64b5f6",
  "n.s."= "grey60"
)

sm_colors <- c(
  "GLEAM-Sfc"  = "#2E7D32",
  "GLEAM-Root" = "#66BB6A",
  "SWSM-L1"   = "#E65100",
  "SWSM-L3"   = "#FF9800",
  "ERA5L-L1"   = "#1565C0",
  "ERA5L-L3"   = "#64B5F6"
)

effect_colors <- c(
  "IE" = "#D95F0E",
  "DE" = "#2C7FB8",
  "TE" = "#238443"
)

sig_star <- function(p) {
  case_when(
    p < 0.01 ~ "***",
    p < 0.05 ~ "**",
    p < 0.10 ~ "*",
    TRUE     ~ "n.s."
  )
}

# =============================================================================
# 1. LOAD DATA
# =============================================================================

# Set 0 baseline
baseline <- read_csv(file.path(outdir, "v3med_set0_baseline.csv"),
                     show_col_types = FALSE)

# Drought Model 8 coefficients
drought_coef <- read_csv(file.path(outdir, "v3med_drought_model8_coefficients.csv"),
                         show_col_types = FALSE)
drought_ce <- read_csv(file.path(outdir, "v3med_drought_conditional_effects.csv"),
                       show_col_types = FALSE)

# Heat Model 8 coefficients
heat_coef <- read_csv(file.path(outdir, "v3med_heat_model8_coefficients.csv"),
                      show_col_types = FALSE)
heat_ce <- read_csv(file.path(outdir, "v3med_heat_conditional_effects.csv"),
                    show_col_types = FALSE)

# Bootstrap (may not exist yet)
bs_drought <- tryCatch(
  read_csv(file.path(outdir, "v3med_bootstrap_drought.csv"), show_col_types = FALSE),
  error = function(e) NULL
)
bs_heat <- tryCatch(
  read_csv(file.path(outdir, "v3med_bootstrap_heat.csv"), show_col_types = FALSE),
  error = function(e) NULL
)

# Heterogeneity
het_coef <- read_csv(file.path(outdir, "v3med_heterogeneity_results.csv"),
                     show_col_types = FALSE)
het_ce <- read_csv(file.path(outdir, "v3med_heterogeneity_conditional_effects.csv"),
                   show_col_types = FALSE)

cat("Data loaded.\n")

# =============================================================================
# 2. SET 0: BASELINE COEFFICIENT PLOT
# =============================================================================

p_baseline <- baseline %>%
  filter(term %in% c("SR_x_D_full", "SR_x_Heat_full")) %>%
  mutate(
    sig = sig_star(p),
    ci_lo = b - 1.96 * se,
    ci_hi = b + 1.96 * se,
    module_lbl = if_else(term == "SR_x_D_full",
                         "SR \u00d7 Drought (D\u00d7ca)",
                         "SR \u00d7 Heat (H\u00d7ca)"),
    ctrl_lbl = if_else(ctrl_version == "full",
                       "Full controls", "Reduced controls")
  ) %>%
  ggplot(aes(x = b, y = ctrl_lbl, color = sig)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey45") +
  geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi),
                  size = 0.6, linewidth = 0.7) +
  scale_color_manual(values = sig_colors, name = "Significance") +
  facet_wrap(~module_lbl, scales = "free_x", nrow = 1) +
  labs(title = "Set 0: Total SR Buffering (no SM control)",
       subtitle = "Grid + Year FE, cluster by grid",
       x = "Coefficient (95% CI)") +
  theme_coef

ggsave(file.path(figdir, "v3med_plot_set0_baseline.png"),
       p_baseline, width = 12, height = 4, dpi = 300, bg = "white")
cat("Plot: Set 0 baseline saved.\n")

# =============================================================================
# 3. SM SOURCE COMPARISON — DROUGHT MODULE
# =============================================================================

# Key coefficients for cross-SM comparison
key_terms_drought <- c("D_full", "SR_x_D_full", "hdd_ge32", "SM")
term_labels_drought <- c(
  "D_full"       = "a1: D \u2192 SM / c1: D \u2192 Y",
  "SR_x_D_full"  = "a3: D\u00d7ca \u2192 SM / c3: D\u00d7ca \u2192 Y",
  "SM"           = "b: SM \u2192 Y"
)

plot_sm_comparison <- function(coef_data, module_name, key_terms, term_labels) {

  # a-path coefficients (mediator eq)
  d_med <- coef_data %>%
    filter(fe_level == "L0", ctrl_version == "reduced",
           equation == "mediator",
           term %in% c("D_full", "SR_x_D_full", "hdd_ge32")) %>%
    mutate(path = "a-path (Mediator eq)")

  # b-path and c'-path (outcome eq)
  d_out <- coef_data %>%
    filter(fe_level == "L0", ctrl_version == "reduced",
           equation == "outcome",
           term %in% c("D_full", "SR_x_D_full", "SM", "hdd_ge32")) %>%
    mutate(path = "c'/b-path (Outcome eq)")

  d_plot <- bind_rows(d_med, d_out) %>%
    filter(term %in% names(term_labels)) %>%
    mutate(
      sig = sig_star(p),
      ci_lo = b - 1.96 * se,
      ci_hi = b + 1.96 * se,
      term_lbl = term_labels[term],
      sm_label = factor(sm_label, levels = names(sm_colors))
    )

  ggplot(d_plot, aes(x = b, y = sm_label, color = sm_label, shape = sig)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45") +
    geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi),
                    size = 0.5, linewidth = 0.6,
                    position = position_dodge(width = 0.4)) +
    scale_color_manual(values = sm_colors, name = "SM Source") +
    scale_shape_manual(values = c("***" = 16, "**" = 17, "*" = 15, "n.s." = 1),
                       name = "Significance") +
    facet_grid(path ~ term_lbl, scales = "free_x") +
    labs(title = paste0(module_name, " Module: Key Coefficients by SM Source"),
         subtitle = "Grid + Year FE, reduced controls, cluster by grid",
         x = "Coefficient (95% CI)") +
    theme_coef +
    theme(strip.text.y = element_text(angle = 0, hjust = 0))
}

p_sm_drought <- plot_sm_comparison(
  drought_coef, "Drought",
  key_terms_drought,
  c("D_full" = "a1/c1: Drought",
    "SR_x_D_full" = "a3/c3: Drought \u00d7 SR",
    "SM" = "b: SM \u2192 Yield")
)

ggsave(file.path(figdir, "v3med_plot_sm_comparison_drought.png"),
       p_sm_drought, width = 14, height = 6, dpi = 300, bg = "white")
cat("Plot: SM comparison drought saved.\n")

# =============================================================================
# 4. SM SOURCE COMPARISON — HEAT MODULE
# =============================================================================

p_sm_heat <- plot_sm_comparison(
  heat_coef, "Heat",
  c("hdd_ge32", "SR_x_Heat_full", "SM"),
  c("hdd_ge32" = "a1h/c1h: Heat",
    "SR_x_Heat_full" = "a3h/c3h: Heat \u00d7 SR",
    "SM" = "b_h: SM \u2192 Yield")
)

ggsave(file.path(figdir, "v3med_plot_sm_comparison_heat.png"),
       p_sm_heat, width = 14, height = 6, dpi = 300, bg = "white")
cat("Plot: SM comparison heat saved.\n")

# =============================================================================
# 5. CTRL VERSION COMPARISON (full vs reduced)
# =============================================================================

plot_ctrl_comparison <- function(coef_data, module_name, interact_term) {
  d <- coef_data %>%
    filter(fe_level == "L0", equation %in% c("mediator", "outcome"),
           term %in% c(interact_term, "SM")) %>%
    mutate(
      sig = sig_star(p),
      ci_lo = b - 1.96 * se,
      ci_hi = b + 1.96 * se,
      ctrl_lbl = if_else(ctrl_version == "full", "Full controls", "Reduced controls"),
      eq_lbl = if_else(equation == "mediator", "Mediator eq", "Outcome eq"),
      term_lbl = case_when(
        term == interact_term ~ paste0("Interaction (", interact_term, ")"),
        term == "SM" ~ "SM \u2192 Yield (b)",
        TRUE ~ term
      )
    )

  ggplot(d, aes(x = b, y = sm_label, color = ctrl_lbl, shape = sig)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45") +
    geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi),
                    size = 0.5, linewidth = 0.6,
                    position = position_dodge(width = 0.5)) +
    scale_color_manual(values = c("Full controls" = "#7B1FA2",
                                  "Reduced controls" = "#F57F17"),
                       name = "Controls") +
    scale_shape_manual(values = c("***" = 16, "**" = 17, "*" = 15, "n.s." = 1),
                       name = "Significance") +
    facet_grid(eq_lbl ~ term_lbl, scales = "free_x") +
    labs(title = paste0(module_name, " Module: Full vs Reduced Controls"),
         subtitle = "Grid + Year FE, cluster by grid",
         x = "Coefficient (95% CI)") +
    theme_coef +
    theme(strip.text.y = element_text(angle = 0, hjust = 0))
}

p_ctrl_drought <- plot_ctrl_comparison(drought_coef, "Drought", "SR_x_D_full")
ggsave(file.path(figdir, "v3med_plot_ctrl_comparison_drought.png"),
       p_ctrl_drought, width = 13, height = 5.5, dpi = 300, bg = "white")

p_ctrl_heat <- plot_ctrl_comparison(heat_coef, "Heat", "SR_x_Heat_full")
ggsave(file.path(figdir, "v3med_plot_ctrl_comparison_heat.png"),
       p_ctrl_heat, width = 13, height = 5.5, dpi = 300, bg = "white")
cat("Plot: Control version comparisons saved.\n")

# =============================================================================
# 6. CONDITIONAL EFFECTS (IE / DE / TE) — Point estimates
# =============================================================================

plot_conditional_effects <- function(ce_data, module_name, bs_data = NULL) {

  d <- ce_data %>%
    filter(fe_level == "L0", ctrl_version == "reduced",
           effect %in% c("IE", "DE", "TE"),
           ca_level %in% c("P25", "P50", "P75")) %>%
    mutate(
      effect = factor(effect, levels = c("IE", "DE", "TE")),
      ca_level = factor(ca_level, levels = c("P25", "P50", "P75")),
      sm_label = factor(sm_label, levels = names(sm_colors))
    )

  # If bootstrap CI available, merge
  if (!is.null(bs_data)) {
    bs_ci <- bs_data %>%
      filter(stat %in% c("IE", "DE", "TE"),
             ca_level %in% c("P25", "P50", "P75")) %>%
      select(sm_source, stat, ca_level, ci_lo, ci_hi) %>%
      rename(effect = stat)

    d <- d %>%
      left_join(bs_ci, by = c("sm_source", "effect", "ca_level"))
  } else {
    d <- d %>% mutate(ci_lo = NA_real_, ci_hi = NA_real_)
  }

  ggplot(d, aes(x = ca_level, y = value, fill = effect)) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "grey45") +
    geom_col(position = position_dodge(width = 0.7), width = 0.6, alpha = 0.85) +
    {if (any(!is.na(d$ci_lo)))
      geom_errorbar(aes(ymin = ci_lo, ymax = ci_hi),
                    position = position_dodge(width = 0.7),
                    width = 0.2, linewidth = 0.5)} +
    scale_fill_manual(values = effect_colors, name = "Effect") +
    facet_wrap(~sm_label, nrow = 1, scales = "free_y") +
    labs(title = paste0(module_name, " Module: Conditional Effects at ca Percentiles"),
         subtitle = "IE = indirect (SM-mediated), DE = direct, TE = total",
         x = "ca percentile", y = "Effect on ln(yield)") +
    theme_coef +
    theme(axis.title.y = element_text(),
          panel.grid.major.y = element_line(color = "grey90", linewidth = 0.3))
}

p_ce_drought <- plot_conditional_effects(drought_ce, "Drought", bs_drought)
ggsave(file.path(figdir, "v3med_plot_conditional_drought.png"),
       p_ce_drought, width = 16, height = 5.5, dpi = 300, bg = "white")

p_ce_heat <- plot_conditional_effects(heat_ce, "Heat", bs_heat)
ggsave(file.path(figdir, "v3med_plot_conditional_heat.png"),
       p_ce_heat, width = 16, height = 5.5, dpi = 300, bg = "white")
cat("Plot: Conditional effects saved.\n")

# =============================================================================
# 7. INDEX OF MODERATED MEDIATION
# =============================================================================

idx_drought <- drought_ce %>%
  filter(fe_level == "L0", ctrl_version == "reduced",
         effect == "Index") %>%
  mutate(module = "Drought")

idx_heat <- heat_ce %>%
  filter(fe_level == "L0", ctrl_version == "reduced",
         effect == "Index") %>%
  mutate(module = "Heat")

idx_all <- bind_rows(idx_drought, idx_heat) %>%
  mutate(sm_label = factor(sm_label, levels = names(sm_colors)))

# Add bootstrap CI if available
if (!is.null(bs_drought)) {
  bs_idx_d <- bs_drought %>%
    filter(stat == "Index") %>%
    select(sm_source, ci_lo, ci_hi) %>%
    mutate(module = "Drought")
  idx_all <- idx_all %>%
    left_join(bs_idx_d, by = c("sm_source", "module"))
}
if (!is.null(bs_heat)) {
  bs_idx_h <- bs_heat %>%
    filter(stat == "Index") %>%
    select(sm_source, ci_lo, ci_hi) %>%
    mutate(module = "Heat")
  # Merge only if ci_lo/ci_hi not already present for heat rows
  heat_rows <- idx_all$module == "Heat"
  if (any(heat_rows) && !"ci_lo" %in% names(idx_all)) {
    idx_all <- idx_all %>%
      left_join(bs_idx_h, by = c("sm_source", "module"))
  } else if (any(heat_rows)) {
    # Fill heat rows
    idx_heat_ci <- idx_all %>%
      filter(module == "Heat") %>%
      select(-ci_lo, -ci_hi) %>%
      left_join(bs_idx_h, by = c("sm_source", "module"))
    idx_all <- bind_rows(
      idx_all %>% filter(module != "Heat"),
      idx_heat_ci
    )
  }
}

# Ensure ci columns exist
if (!"ci_lo" %in% names(idx_all)) {
  idx_all <- idx_all %>% mutate(ci_lo = NA_real_, ci_hi = NA_real_)
}

p_index <- ggplot(idx_all, aes(x = sm_label, y = value, fill = module)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "grey45") +
  geom_col(position = position_dodge(width = 0.7), width = 0.6, alpha = 0.85) +
  {if (any(!is.na(idx_all$ci_lo)))
    geom_errorbar(aes(ymin = ci_lo, ymax = ci_hi),
                  position = position_dodge(width = 0.7),
                  width = 0.2, linewidth = 0.5)} +
  scale_fill_manual(values = c("Drought" = "#E65100", "Heat" = "#1565C0"),
                    name = "Module") +
  labs(title = "Index of Moderated Mediation (a3 \u00d7 b)",
       subtitle = "Measures how much SR's indirect effect changes per unit ca",
       x = "SM Source", y = "Index value") +
  theme_coef +
  theme(axis.title.y = element_text(),
        axis.text.x = element_text(angle = 30, hjust = 1),
        panel.grid.major.y = element_line(color = "grey90", linewidth = 0.3))

ggsave(file.path(figdir, "v3med_plot_index.png"),
       p_index, width = 10, height = 5, dpi = 300, bg = "white")
cat("Plot: Index of moderated mediation saved.\n")

# =============================================================================
# 8. HETEROGENEITY: a3 / c3 ACROSS SUBSAMPLES
# =============================================================================

zone_order <- c("NE", "HHH", "SW", "SH", "NW", "Other", "low_irr", "high_irr")

plot_het_coef <- function(het_data, module_name, eq_name, term_name, title_suffix) {
  d <- het_data %>%
    filter(module == module_name, equation == eq_name, term == term_name) %>%
    mutate(
      sig = sig_star(p),
      ci_lo = b - 1.96 * se,
      ci_hi = b + 1.96 * se,
      subgroup = factor(subgroup, levels = zone_order),
      split_lbl = if_else(split_type == "zone", "Maize Zone", "Irrigation")
    )

  ggplot(d, aes(x = b, y = subgroup, color = sig)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45") +
    geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi),
                    size = 0.6, linewidth = 0.7) +
    scale_color_manual(values = sig_colors, name = "Significance") +
    facet_wrap(~split_lbl, scales = "free_y", ncol = 2) +
    labs(title = paste0(module_name, " Module: ", title_suffix, " by Subsample"),
         subtitle = "Grid + Year FE, reduced controls, gleam_sms_mean",
         x = "Coefficient (95% CI)") +
    theme_coef
}

# Drought a3 (mediator)
p_het_d_a3 <- plot_het_coef(het_coef, "drought", "mediator", "SR_x_D_full",
                            "a3 (D\u00d7ca \u2192 SM)")
ggsave(file.path(figdir, "v3med_plot_het_drought_a3.png"),
       p_het_d_a3, width = 12, height = 5, dpi = 300, bg = "white")

# Drought c3 (outcome)
p_het_d_c3 <- plot_het_coef(het_coef, "drought", "outcome", "SR_x_D_full",
                            "c3 (D\u00d7ca \u2192 Yield, direct)")
ggsave(file.path(figdir, "v3med_plot_het_drought_c3.png"),
       p_het_d_c3, width = 12, height = 5, dpi = 300, bg = "white")

# Heat a3h (mediator)
p_het_h_a3 <- plot_het_coef(het_coef, "heat", "mediator", "SR_x_Heat_full",
                            "a3h (H\u00d7ca \u2192 SM)")
ggsave(file.path(figdir, "v3med_plot_het_heat_a3.png"),
       p_het_h_a3, width = 12, height = 5, dpi = 300, bg = "white")

# Heat c3h (outcome)
p_het_h_c3 <- plot_het_coef(het_coef, "heat", "outcome", "SR_x_Heat_full",
                            "c3h (H\u00d7ca \u2192 Yield, direct)")
ggsave(file.path(figdir, "v3med_plot_het_heat_c3.png"),
       p_het_h_c3, width = 12, height = 5, dpi = 300, bg = "white")

cat("Plot: Heterogeneity coefficient plots saved.\n")

# =============================================================================
# 9. HETEROGENEITY: IE vs DE COMPARISON
# =============================================================================

plot_het_ie_de <- function(ce_data, module_name) {
  d <- ce_data %>%
    filter(module == module_name,
           effect %in% c("IE", "DE"),
           ca_level == "P50") %>%
    mutate(
      subgroup = factor(subgroup, levels = zone_order),
      split_lbl = if_else(split_type == "zone", "Maize Zone", "Irrigation"),
      effect = factor(effect, levels = c("IE", "DE"))
    )

  ggplot(d, aes(x = value, y = subgroup, fill = effect)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45") +
    geom_col(position = position_dodge(width = 0.6), width = 0.5, alpha = 0.85) +
    scale_fill_manual(values = effect_colors[c("IE", "DE")],
                      name = "Effect",
                      labels = c("IE" = "Indirect (SM-mediated)",
                                 "DE" = "Direct")) +
    facet_wrap(~split_lbl, scales = "free_y", ncol = 2) +
    labs(title = paste0(module_name, " Module: IE vs DE at Median ca"),
         subtitle = "gleam_sms_mean, reduced controls, grid + year FE",
         x = "Effect on ln(yield)", y = NULL) +
    theme_coef +
    theme(axis.title.y = element_blank(),
          panel.grid.major.y = element_blank(),
          panel.grid.major.x = element_line(color = "grey90", linewidth = 0.3))
}

p_het_ie_de_d <- plot_het_ie_de(het_ce, "drought")
ggsave(file.path(figdir, "v3med_plot_het_ie_de_drought.png"),
       p_het_ie_de_d, width = 12, height = 5, dpi = 300, bg = "white")

p_het_ie_de_h <- plot_het_ie_de(het_ce, "heat")
ggsave(file.path(figdir, "v3med_plot_het_ie_de_heat.png"),
       p_het_ie_de_h, width = 12, height = 5, dpi = 300, bg = "white")

cat("Plot: Heterogeneity IE vs DE saved.\n")

# =============================================================================
# 10. BOOTSTRAP CI PLOTS (if available)
# =============================================================================

if (!is.null(bs_drought) && !is.null(bs_heat)) {

  plot_bootstrap_ci <- function(bs_data, module_name) {
    d <- bs_data %>%
      filter(stat %in% c("IE", "DE", "TE"),
             ca_level %in% c("P25", "P50", "P75")) %>%
      mutate(
        stat = factor(stat, levels = c("IE", "DE", "TE")),
        ca_level = factor(ca_level, levels = c("P25", "P50", "P75")),
        sig = if_else(sign(ci_lo) == sign(ci_hi), "sig", "n.s.")
      )

    ggplot(d, aes(x = ca_level, y = point_est, color = stat, shape = sig)) +
      geom_hline(yintercept = 0, linetype = "dashed", color = "grey45") +
      geom_pointrange(aes(ymin = ci_lo, ymax = ci_hi),
                      position = position_dodge(width = 0.5),
                      size = 0.5, linewidth = 0.6) +
      scale_color_manual(values = effect_colors, name = "Effect") +
      scale_shape_manual(values = c("sig" = 16, "n.s." = 1),
                         name = "Bootstrap CI",
                         labels = c("sig" = "Excludes 0", "n.s." = "Includes 0")) +
      facet_wrap(~sm_source, nrow = 1) +
      labs(title = paste0(module_name, " Module: Bootstrap 95% CI"),
           subtitle = "500 cluster bootstrap reps, percentile CI",
           x = "ca percentile", y = "Effect on ln(yield)") +
      theme_coef +
      theme(axis.title.y = element_text(),
            panel.grid.major.y = element_line(color = "grey90", linewidth = 0.3))
  }

  p_bs_d <- plot_bootstrap_ci(bs_drought, "Drought")
  ggsave(file.path(figdir, "v3med_plot_bootstrap_drought.png"),
         p_bs_d, width = 12, height = 5, dpi = 300, bg = "white")

  p_bs_h <- plot_bootstrap_ci(bs_heat, "Heat")
  ggsave(file.path(figdir, "v3med_plot_bootstrap_heat.png"),
         p_bs_h, width = 12, height = 5, dpi = 300, bg = "white")

  cat("Plot: Bootstrap CI plots saved.\n")
} else {
  cat("Bootstrap data not yet available. Skipping bootstrap plots.\n")
}

cat("\n=== v3med_plots.R COMPLETE ===\n")
