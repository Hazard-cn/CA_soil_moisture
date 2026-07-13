# =============================================================================
# plot_f4_b067_v2.R — Revised coefficient figures
# v2 changes:
#   1. IE/DE/TE plots: x-axis = SR level (P25->P50->P75), y = estimate
#   2. Baseline: annotated mechanism diagram with path labels
#   3. Heterogeneity (zone/irr): only IE/DE/TE gradient plots
# =============================================================================

set.seed(42)

projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
infile  <- file.path(projdir, "temp/2026-06-04_f4_b067_full_bootstrap_counterfactual",
                     "f4_b067_mean_raw_unified_coefficients_effects.csv")
outdir  <- file.path(projdir, "output/figures/f4_b067_v2")
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(patchwork)
  library(readr)
  library(tidyr)
})

# ---- Load & prep ----
df <- readr::read_csv(infile, show_col_types = FALSE) %>%
  filter(sample_id == "B067", branch == "mean", transform == "raw") %>%
  mutate(
    across(c(estimate, model_se, model_p, model_ci_lo_95, model_ci_hi_95,
             bs_se, bs_ci_lo_95, bs_ci_hi_95, ca_value), as.numeric),
    ci_lo = coalesce(bs_ci_lo_95, model_ci_lo_95),
    ci_hi = coalesce(bs_ci_hi_95, model_ci_hi_95),
    sig_plot = case_when(
      record_type == "rhs_coefficient" & !is.na(model_p) & model_p < 0.05 ~ "p < 0.05",
      record_type != "rhs_coefficient" & !is.na(ci_lo) & !is.na(ci_hi) & ci_lo * ci_hi > 0 ~ "CI excl. 0",
      TRUE ~ "n.s."
    )
  )

hazard_levels <- c("drought", "heat", "hotdry")
hazard_labels <- c(drought = "Drought", heat = "Heat", hotdry = "Hot-dry")
hazard_colors <- c(drought = "#8B5A2B", heat = "#C7252E", hotdry = "#6A3D9A")
effect_labels <- c(IE = "Indirect (via SM)", DE = "Direct (residual)", TE = "Total")
effect_colors <- setNames(c("#2166AC", "#E66101", "#111111"), effect_labels)

theme_pub <- theme_minimal(base_size = 10, base_family = "sans") +
  theme(
    panel.background  = element_blank(),
    plot.background   = element_rect(fill = "white", colour = NA),
    panel.grid.minor  = element_blank(),
    axis.title  = element_text(size = 10),
    axis.text   = element_text(size = 8),
    strip.text  = element_text(size = 10, face = "bold"),
    plot.title  = element_text(size = 12, face = "bold"),
    plot.subtitle = element_text(size = 9, color = "grey30"),
    legend.position = "bottom",
    legend.title = element_text(size = 9),
    legend.text  = element_text(size = 8)
  )

save_fig <- function(p, fname, w = 180, h = 120) {
  ggsave(file.path(outdir, fname), p, width = w, height = h,
         units = "mm", dpi = 300, bg = "white")
  cat("  Saved:", fname, "\n")
}

# =============================================================================
# Fig 1: BASELINE — Annotated mechanism coefficient diagram
# One row per hazard, columns = the 5 key coefficients with path labels
# =============================================================================
cat("Fig 1: Baseline annotated mechanism...\n")

d_base <- df %>%
  filter(record_type == "rhs_coefficient", layer == "baseline",
         role %in% c("a1", "a3", "b", "c1", "c3")) %>%
  mutate(
    path_label = case_when(
      role == "a1" ~ "a1: Hazard\n-> SM",
      role == "a3" ~ "a3: SR x Hazard\n-> SM",
      role == "b"  ~ "b: SM\n-> Yield",
      role == "c1" ~ "c1: Hazard\n-> Yield",
      role == "c3" ~ "c3: SR x Hazard\n-> Yield"
    ),
    path_label = factor(path_label, levels = c(
      "a1: Hazard\n-> SM",
      "a3: SR x Hazard\n-> SM",
      "b: SM\n-> Yield",
      "c1: Hazard\n-> Yield",
      "c3: SR x Hazard\n-> Yield"
    )),
    hazard_f = factor(hazard_labels[as.character(hazard)],
                      levels = hazard_labels),
    sig_shape = ifelse(sig_plot == "p < 0.05", "p < 0.05", "n.s.")
  )

fig1 <- ggplot(d_base, aes(x = estimate, y = hazard_f,
                            color = hazard_f, shape = sig_shape)) +
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.3, color = "grey50") +
  geom_errorbarh(aes(xmin = ci_lo, xmax = ci_hi),
                 height = 0.25, linewidth = 0.55) +
  geom_point(size = 2.8, stroke = 0.7, fill = "white") +
  facet_wrap(~ path_label, ncol = 5, scales = "free_x") +
  scale_color_manual(values = hazard_colors, guide = "none") +
  scale_shape_manual(values = c("p < 0.05" = 16, "n.s." = 21),
                     name = "Significance") +
  labs(x = "Coefficient", y = NULL,
       title = "Baseline: Five mechanism coefficients",
       subtitle = "Each panel = one path in the moderated-mediation model. Scales are independent.") +
  theme_pub +
  theme(strip.text = element_text(size = 8))

save_fig(fig1, "fig1_baseline_mechanism_annotated.png", w = 250, h = 85)

# =============================================================================
# Fig 2: BASELINE — IE/DE/TE gradient (x = SR level, y = estimate)
# =============================================================================
cat("Fig 2: Baseline IE/DE/TE gradient...\n")

d_iede_base <- df %>%
  filter(record_type == "iede_effect", layer == "baseline",
         ca_level %in% c("P25", "P50", "P75")) %>%
  mutate(
    effect_f = factor(effect, levels = c("IE", "DE", "TE"), labels = effect_labels),
    sr_x     = factor(ca_level, levels = c("P25", "P50", "P75")),
    hazard_f = factor(hazard_labels[as.character(hazard)], levels = hazard_labels),
    sig_shape = ifelse(sig_plot == "CI excl. 0", "CI excl. 0", "n.s.")
  )

fig2 <- ggplot(d_iede_base, aes(x = sr_x, y = estimate,
                                 color = effect_f, group = effect_f,
                                 shape = sig_shape)) +
  geom_hline(yintercept = 0, linetype = "dashed", linewidth = 0.3, color = "grey50") +
  geom_line(linewidth = 0.6, position = position_dodge(width = 0.25)) +
  geom_errorbar(aes(ymin = ci_lo, ymax = ci_hi),
                width = 0.12, linewidth = 0.5,
                position = position_dodge(width = 0.25)) +
  geom_point(size = 2.8, stroke = 0.7, fill = "white",
             position = position_dodge(width = 0.25)) +
  facet_wrap(~ hazard_f, nrow = 1, scales = "free_y") +
  scale_color_manual(values = effect_colors, name = "Effect") +
  scale_shape_manual(values = c("CI excl. 0" = 16, "n.s." = 21),
                     name = "Significance") +
  labs(x = "Straw return level", y = "Conditional effect",
       title = "Baseline: IE / DE / TE across SR adoption levels",
       subtitle = "Left to right: as SR rises from P25 to P75, negative effects shrink toward zero") +
  theme_pub

save_fig(fig2, "fig2_baseline_iede_gradient.png", w = 240, h = 100)

# =============================================================================
# Helper: IE/DE/TE gradient plot for any subgroup
# =============================================================================
plot_iede_gradient <- function(data, title_text, subtitle_text = NULL,
                                facet_rows = "hazard_f", facet_cols = NULL,
                                w = 240, h = 100) {
  d <- data %>%
    filter(ca_level %in% c("P25", "P50", "P75")) %>%
    mutate(
      effect_f  = factor(effect, levels = c("IE", "DE", "TE"), labels = effect_labels),
      sr_x      = factor(ca_level, levels = c("P25", "P50", "P75")),
      hazard_f  = factor(hazard_labels[as.character(hazard)], levels = hazard_labels),
      sig_shape = ifelse(sig_plot == "CI excl. 0", "CI excl. 0", "n.s.")
    )

  p <- ggplot(d, aes(x = sr_x, y = estimate,
                      color = effect_f, group = effect_f,
                      shape = sig_shape)) +
    geom_hline(yintercept = 0, linetype = "dashed", linewidth = 0.3, color = "grey50") +
    geom_line(linewidth = 0.55, position = position_dodge(width = 0.25)) +
    geom_errorbar(aes(ymin = ci_lo, ymax = ci_hi),
                  width = 0.12, linewidth = 0.45,
                  position = position_dodge(width = 0.25)) +
    geom_point(size = 2.5, stroke = 0.7, fill = "white",
               position = position_dodge(width = 0.25)) +
    scale_color_manual(values = effect_colors, name = "Effect") +
    scale_shape_manual(values = c("CI excl. 0" = 16, "n.s." = 21),
                       name = "Significance") +
    labs(x = "Straw return level", y = "Conditional effect",
         title = title_text, subtitle = subtitle_text) +
    theme_pub

  if (!is.null(facet_cols)) {
    p <- p + facet_grid(reformulate(facet_cols, facet_rows), scales = "free_y")
  } else {
    p <- p + facet_wrap(~ hazard_f, nrow = 1, scales = "free_y")
  }
  p
}

# =============================================================================
# Fig 3–7: Zone IE/DE/TE gradient (one figure per zone)
# =============================================================================
cat("Fig 3-7: Zone IE/DE/TE gradients...\n")

zones <- c("NE", "HHH", "NW", "SW", "SH")
zone_full <- c(NE = "Northeast (NE)", HHH = "Huang-Huai-Hai (HHH)",
               NW = "Northwest (NW)", SW = "Southwest (SW)", SH = "South (SH)")

for (i in seq_along(zones)) {
  z <- zones[i]
  d_z <- df %>%
    filter(record_type == "iede_effect", layer == "heterogeneity",
           subgroup == z)
  if (nrow(d_z) == 0) { cat("  Skipping", z, "\n"); next }

  p <- plot_iede_gradient(d_z,
    title_text = paste0(zone_full[z], ": IE / DE / TE across SR levels"))

  save_fig(p, sprintf("fig%d_zone_%s_iede.png", i + 2, z), w = 240, h = 100)
}

# =============================================================================
# Fig 8-9: Irrigation heterogeneity IE/DE/TE gradient
# =============================================================================
cat("Fig 8-9: Irrigation IE/DE/TE gradients...\n")

irr_labels <- c(high_irr = "High irrigation", low_irr = "Low irrigation")

for (irr in c("high_irr", "low_irr")) {
  d_irr <- df %>%
    filter(record_type == "iede_effect", layer == "heterogeneity",
           subgroup == irr)
  fig_num <- ifelse(irr == "high_irr", 8, 9)

  p <- plot_iede_gradient(d_irr,
    title_text = paste0(irr_labels[irr], ": IE / DE / TE across SR levels"))

  save_fig(p, sprintf("fig%d_irr_%s_iede.png", fig_num, irr), w = 240, h = 100)
}

# =============================================================================
# Fig 10: Irrigation COMBINED — 2 rows (high/low) × 3 cols (hazard)
# =============================================================================
cat("Fig 10: Irrigation combined panel...\n")

d_irr_all <- df %>%
  filter(record_type == "iede_effect", layer == "heterogeneity",
         subgroup %in% c("high_irr", "low_irr"),
         ca_level %in% c("P25", "P50", "P75")) %>%
  mutate(
    effect_f  = factor(effect, levels = c("IE", "DE", "TE"), labels = effect_labels),
    sr_x      = factor(ca_level, levels = c("P25", "P50", "P75")),
    hazard_f  = factor(hazard_labels[as.character(hazard)], levels = hazard_labels),
    irr_f     = factor(irr_labels[subgroup], levels = irr_labels),
    row_f     = factor(
      paste(irr_f, effect_f, sep = " | "),
      levels = as.vector(outer(irr_labels, effect_labels, paste, sep = " | "))
    ),
    sig_shape = ifelse(sig_plot == "CI excl. 0", "CI excl. 0", "n.s.")
  )

fig10 <- ggplot(d_irr_all, aes(x = sr_x, y = estimate,
                                color = effect_f, group = effect_f,
                                shape = sig_shape)) +
  geom_hline(yintercept = 0, linetype = "dashed", linewidth = 0.3, color = "grey50") +
  geom_line(linewidth = 0.55) +
  geom_errorbar(aes(ymin = ci_lo, ymax = ci_hi),
                width = 0.12, linewidth = 0.45,
                alpha = 0.85) +
  geom_point(size = 2.3, stroke = 0.7, fill = "white",
             alpha = 0.95) +
  facet_grid(row_f ~ hazard_f, scales = "free_y") +
  scale_color_manual(values = effect_colors, name = "Effect") +
  scale_shape_manual(values = c("CI excl. 0" = 16, "n.s." = 21),
                     name = "Significance") +
  labs(x = "Straw return level", y = "Conditional effect",
       title = "Irrigation heterogeneity: IE / DE / TE across SR levels",
       subtitle = "Rows split irrigation group and effect type to avoid overlapping near-zero series; columns = hazard type") +
  theme_pub +
  theme(strip.text.y = element_text(size = 8, angle = 0))

save_fig(fig10, "fig10_irr_combined_iede.png", w = 240, h = 230)

# =============================================================================
# Fig 11: AI>2 Irrigation COMBINED — same format
# =============================================================================
cat("Fig 11: AI>2 irrigation combined...\n")

d_ai2 <- df %>%
  filter(record_type == "iede_effect", layer == "ai_gt2_irrigation",
         ca_level %in% c("P25", "P50", "P75")) %>%
  mutate(
    effect_f  = factor(effect, levels = c("IE", "DE", "TE"), labels = effect_labels),
    sr_x      = factor(ca_level, levels = c("P25", "P50", "P75")),
    hazard_f  = factor(hazard_labels[as.character(hazard)], levels = hazard_labels),
    irr_f     = factor(irr_labels[subgroup], levels = irr_labels),
    row_f     = factor(
      paste(irr_f, effect_f, sep = " | "),
      levels = as.vector(outer(irr_labels, effect_labels, paste, sep = " | "))
    ),
    sig_shape = ifelse(sig_plot == "CI excl. 0", "CI excl. 0", "n.s.")
  )

if (nrow(d_ai2) > 0) {
  fig11 <- ggplot(d_ai2, aes(x = sr_x, y = estimate,
                              color = effect_f, group = effect_f,
                              shape = sig_shape)) +
    geom_hline(yintercept = 0, linetype = "dashed", linewidth = 0.3, color = "grey50") +
    geom_line(linewidth = 0.55) +
    geom_errorbar(aes(ymin = ci_lo, ymax = ci_hi),
                  width = 0.12, linewidth = 0.45,
                  alpha = 0.85) +
    geom_point(size = 2.3, stroke = 0.7, fill = "white",
               alpha = 0.95) +
    facet_grid(row_f ~ hazard_f, scales = "free_y") +
    scale_color_manual(values = effect_colors, name = "Effect") +
    scale_shape_manual(values = c("CI excl. 0" = 16, "n.s." = 21),
                       name = "Significance") +
    labs(x = "Straw return level", y = "Conditional effect",
         title = "Arid areas (AI>2): IE / DE / TE across SR levels by irrigation",
         subtitle = "Rows split irrigation group and effect type to avoid overlapping near-zero series; columns = hazard type") +
    theme_pub +
    theme(strip.text.y = element_text(size = 8, angle = 0))

  save_fig(fig11, "fig11_ai2_irr_combined_iede.png", w = 240, h = 230)
} else {
  cat("  No AI>2 IEDE data found, skipping fig11\n")
}

cat("\n===== All v2 figures complete =====\n")
cat("Output:", outdir, "\n")
