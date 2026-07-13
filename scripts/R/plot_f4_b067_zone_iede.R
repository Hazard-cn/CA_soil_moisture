# =============================================================================
# plot_f4_b067_zone_iede.R — 每个产区一张 IE/DE/TE 随 SR 变化图
# 每张图: 3 hazard (行) × 3 effect (IE/DE/TE, y轴) × 3 SR level (P25/P50/P75, 颜色)
# =============================================================================

set.seed(42)

projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
infile  <- file.path(projdir, "temp/2026-06-04_f4_b067_full_bootstrap_counterfactual",
                     "f4_b067_mean_raw_unified_coefficients_effects.csv")
outdir  <- file.path(projdir, "output/figures/f4_b067_stage")
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(readr)
})

df <- readr::read_csv(infile, show_col_types = FALSE) %>%
  filter(sample_id == "B067", branch == "mean", transform == "raw") %>%
  mutate(
    estimate    = as.numeric(estimate),
    bs_ci_lo_95 = as.numeric(bs_ci_lo_95),
    bs_ci_hi_95 = as.numeric(bs_ci_hi_95),
    model_ci_lo_95 = as.numeric(model_ci_lo_95),
    model_ci_hi_95 = as.numeric(model_ci_hi_95),
    ci_lo = ifelse(!is.na(bs_ci_lo_95), bs_ci_lo_95, model_ci_lo_95),
    ci_hi = ifelse(!is.na(bs_ci_hi_95), bs_ci_hi_95, model_ci_hi_95),
    sig_plot = ifelse(!is.na(ci_lo) & !is.na(ci_hi) & ci_lo * ci_hi > 0,
                      "CI excludes 0", "not significant")
  )

# --- Zone IEDE data ---
zones <- c("NE", "HHH", "NW", "SW", "SH")
zone_full <- c(NE = "Northeast (NE)", HHH = "Huang-Huai-Hai (HHH)",
               NW = "Northwest (NW)", SW = "Southwest (SW)", SH = "South (SH)")

d_zone <- df %>%
  filter(record_type == "iede_effect", layer == "heterogeneity",
         subgroup %in% zones, ca_level %in% c("P25", "P50", "P75")) %>%
  mutate(
    effect   = factor(effect, levels = c("IE", "DE", "TE")),
    ca_level = factor(ca_level, levels = c("P25", "P50", "P75")),
    hazard_label = factor(
      c(drought = "Drought", heat = "Heat", hotdry = "Hot-dry")[as.character(hazard)],
      levels = c("Drought", "Heat", "Hot-dry")
    )
  )

# --- Also get baseline for comparison ---
d_base <- df %>%
  filter(record_type == "iede_effect", layer == "baseline",
         ca_level %in% c("P25", "P50", "P75")) %>%
  mutate(
    effect   = factor(effect, levels = c("IE", "DE", "TE")),
    ca_level = factor(ca_level, levels = c("P25", "P50", "P75")),
    hazard_label = factor(
      c(drought = "Drought", heat = "Heat", hotdry = "Hot-dry")[as.character(hazard)],
      levels = c("Drought", "Heat", "Hot-dry")
    ),
    subgroup = "Baseline"
  )

ca_colors <- c(P25 = "#BDBDBD", P50 = "#3182BD", P75 = "#08519C")

theme_zone <- theme_minimal(base_size = 10, base_family = "sans") +
  theme(
    panel.background = element_blank(),
    plot.background  = element_rect(fill = "white", colour = NA),
    panel.grid.major.y = element_blank(),
    panel.grid.minor   = element_blank(),
    axis.title  = element_text(size = 10),
    axis.text   = element_text(size = 8),
    strip.text  = element_text(size = 10, face = "bold"),
    plot.title  = element_text(size = 12, face = "bold"),
    plot.subtitle = element_text(size = 9, color = "grey30"),
    legend.position = "bottom",
    legend.title = element_text(size = 9),
    legend.text  = element_text(size = 8)
  )

# --- Draw one figure per zone ---
for (z in zones) {
  d_z <- d_zone %>% filter(subgroup == z)

  if (nrow(d_z) == 0) {
    cat("Skipping", z, "- no data\n")
    next
  }

  p <- ggplot(d_z, aes(x = estimate, y = effect, color = ca_level,
                        shape = sig_plot)) +
    geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.35, color = "grey45") +
    geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi),
                  orientation = "y", width = 0.18, linewidth = 0.6,
                  position = position_dodge(width = 0.55)) +
    geom_point(size = 2.8, stroke = 0.8, fill = "white",
               position = position_dodge(width = 0.55)) +
    facet_wrap(~ hazard_label, ncol = 1, scales = "free_x") +
    scale_color_manual(values = ca_colors, name = "SR level") +
    scale_shape_manual(
      values = c("CI excludes 0" = 16, "not significant" = 21),
      name = "Significance"
    ) +
    labs(
      x = "Conditional effect",
      y = NULL,
      title = paste0(zone_full[z], ": IE / DE / TE across SR levels"),
      subtitle = "P25 → P50 → P75: attenuation = negative effects shrink toward zero"
    ) +
    theme_zone

  fname <- paste0("fig_zone_iede_", z, ".png")
  ggsave(file.path(outdir, fname), p,
         width = 160, height = 140, units = "mm", dpi = 300, bg = "white")
  cat("Saved", fname, "\n")
}

# --- Also draw baseline as reference ---
p_base <- ggplot(d_base, aes(x = estimate, y = effect, color = ca_level,
                              shape = sig_plot)) +
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.35, color = "grey45") +
  geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi),
                orientation = "y", width = 0.18, linewidth = 0.6,
                position = position_dodge(width = 0.55)) +
  geom_point(size = 2.8, stroke = 0.8, fill = "white",
             position = position_dodge(width = 0.55)) +
  facet_wrap(~ hazard_label, ncol = 1, scales = "free_x") +
  scale_color_manual(values = ca_colors, name = "SR level") +
  scale_shape_manual(
    values = c("CI excludes 0" = 16, "not significant" = 21),
    name = "Significance"
  ) +
  labs(
    x = "Conditional effect",
    y = NULL,
    title = "Baseline (full sample): IE / DE / TE across SR levels",
    subtitle = "P25 → P50 → P75: attenuation = negative effects shrink toward zero"
  ) +
  theme_zone

ggsave(file.path(outdir, "fig_zone_iede_Baseline.png"), p_base,
       width = 160, height = 140, units = "mm", dpi = 300, bg = "white")
cat("Saved fig_zone_iede_Baseline.png\n")

# --- Irrigation split (high/low) ---
for (irr in c("high_irr", "low_irr")) {
  d_irr <- df %>%
    filter(record_type == "iede_effect", layer == "heterogeneity",
           subgroup == irr, ca_level %in% c("P25", "P50", "P75")) %>%
    mutate(
      effect   = factor(effect, levels = c("IE", "DE", "TE")),
      ca_level = factor(ca_level, levels = c("P25", "P50", "P75")),
      hazard_label = factor(
        c(drought = "Drought", heat = "Heat", hotdry = "Hot-dry")[as.character(hazard)],
        levels = c("Drought", "Heat", "Hot-dry")
      )
    )

  irr_label <- c(high_irr = "High irrigation", low_irr = "Low irrigation")[irr]

  p_irr <- ggplot(d_irr, aes(x = estimate, y = effect, color = ca_level,
                               shape = sig_plot)) +
    geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.35, color = "grey45") +
    geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi),
                  orientation = "y", width = 0.18, linewidth = 0.6,
                  position = position_dodge(width = 0.55)) +
    geom_point(size = 2.8, stroke = 0.8, fill = "white",
               position = position_dodge(width = 0.55)) +
    facet_wrap(~ hazard_label, ncol = 1, scales = "free_x") +
    scale_color_manual(values = ca_colors, name = "SR level") +
    scale_shape_manual(
      values = c("CI excludes 0" = 16, "not significant" = 21),
      name = "Significance"
    ) +
    labs(
      x = "Conditional effect",
      y = NULL,
      title = paste0(irr_label, ": IE / DE / TE across SR levels"),
      subtitle = "P25 → P50 → P75: attenuation = negative effects shrink toward zero"
    ) +
    theme_zone

  fname <- paste0("fig_zone_iede_", irr, ".png")
  ggsave(file.path(outdir, fname), p_irr,
         width = 160, height = 140, units = "mm", dpi = 300, bg = "white")
  cat("Saved", fname, "\n")
}

cat("\n===== Zone IE/DE/TE figures complete =====\n")
