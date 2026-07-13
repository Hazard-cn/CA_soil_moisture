# =============================================================================
# v3_heterogeneity_plots.R
# Purpose: Coefficient plots for heterogeneity analysis (zones + irrigation)
# Author:  YangSu + Claude
# Date:    2026-04-05
# Input:   output/tables/v3_step8_zone.csv
#          output/tables/v3_step8_irrigation.csv
# Output:  output/figures/v3_het_zones.png
#          output/figures/v3_het_irrigation.png
# =============================================================================

set.seed(42)

library(ggplot2)
library(dplyr)
library(tidyr)

projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
outdir  <- file.path(projdir, "output/tables")
figdir  <- file.path(projdir, "output/figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

# --- Palettes and helpers ---
sig_colors <- c("***" = "#1a237e",
                "**"  = "#1565c0",
                "*"   = "#64b5f6",
                "n.s."= "grey60")

win_colors <- c("full"    = "#37474F",
                "v3pre30" = "#8BC34A",
                "v3pm10"  = "#FF9800",
                "hepm10"  = "#F44336",
                "v3he"    = "#2196F3",
                "hema"    = "#9C27B0")

sig_star <- function(p) {
  case_when(
    p < 0.01 ~ "***",
    p < 0.05 ~ "**",
    p < 0.10 ~ "*",
    TRUE ~ "n.s."
  )
}

win_order <- c("v3pre30", "v3pm10", "v3he", "hepm10", "hema", "full")
win_labels <- c("v3pre30" = "V3-pre30",
                "v3pm10"  = "V3\u00b110",
                "v3he"    = "V3\u2192HE",
                "hepm10"  = "HE\u00b110",
                "hema"    = "HE\u2192MA",
                "full"    = "Full season")

theme_coef <- theme_minimal(base_size = 11, base_family = "sans") +
  theme(
    panel.grid.minor = element_blank(),
    strip.text = element_text(face = "bold", size = 11),
    legend.position = "bottom",
    plot.title = element_text(face = "bold", size = 12),
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA)
  )

# =============================================================================
# PLOT A: Zone Heterogeneity
# =============================================================================
cat("Loading v3_step8_zone.csv...\n")
d_zone <- read.csv(file.path(outdir, "v3_step8_zone.csv"),
                    stringsAsFactors = FALSE)
cat("Rows:", nrow(d_zone), "\n")

# Zone ordering (by typical sample size / geographic logic)
zone_order <- c("NE", "HHH", "SW", "SH", "NW", "Other")
zone_labels <- c("NE"    = "NE Spring",
                 "HHH"   = "HHH Summer",
                 "SW"    = "SW Mountain",
                 "SH"    = "S. Hill",
                 "NW"    = "NW Irrigation",
                 "Other" = "Other")

d_zone_long <- d_zone %>%
  filter(N > 0) %>%
  pivot_longer(
    cols = c(starts_with("b_"), starts_with("se_"), starts_with("p_")),
    names_to = c(".value", "coef_type"),
    names_pattern = "(b|se|p)_(SRD|SRH|DH|SRDH)"
  ) %>%
  filter(!is.na(b)) %>%
  mutate(
    ci_lo = b - 1.96 * se,
    ci_hi = b + 1.96 * se,
    sig = sig_star(p),
    zone = factor(zone, levels = zone_order, labels = zone_labels),
    window = factor(window, levels = win_order, labels = win_labels),
    coef_label = case_when(
      coef_type == "SRD"  ~ "SR \u00d7 D",
      coef_type == "SRH"  ~ "SR \u00d7 Heat",
      coef_type == "DH"   ~ "D \u00d7 Heat",
      coef_type == "SRDH" ~ "SR \u00d7 D \u00d7 Heat"
    ),
    coef_label = factor(coef_label,
      levels = c("SR \u00d7 D", "SR \u00d7 Heat",
                 "D \u00d7 Heat", "SR \u00d7 D \u00d7 Heat"))
  )

pA <- ggplot(d_zone_long, aes(y = zone, x = b, color = window)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey40") +
  geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi),
                  position = position_dodge(width = 0.7),
                  size = 0.3, linewidth = 0.5) +
  scale_color_manual(values = win_colors, name = "Window",
                     labels = win_labels) +
  facet_wrap(~coef_label, scales = "free_x", nrow = 1) +
  labs(title = "Heterogeneity by Maize Production Zone",
       subtitle = "Spec(2), grid+year FE, cluster(grid_id). 95% CI shown.",
       x = "Coefficient estimate", y = NULL) +
  theme_coef

ggsave(file.path(figdir, "v3_het_zones.png"), pA,
       width = 16, height = 7, dpi = 300, bg = "white")
cat("Saved: v3_het_zones.png\n")

# =============================================================================
# PLOT B: Irrigation Split
# =============================================================================
cat("Loading v3_step8_irrigation.csv...\n")
d_irr <- read.csv(file.path(outdir, "v3_step8_irrigation.csv"),
                   stringsAsFactors = FALSE)
cat("Rows:", nrow(d_irr), "\n")

d_irr_long <- d_irr %>%
  filter(N > 0) %>%
  pivot_longer(
    cols = c(starts_with("b_"), starts_with("se_"), starts_with("p_")),
    names_to = c(".value", "coef_type"),
    names_pattern = "(b|se|p)_(SRD|SRH|DH|SRDH)"
  ) %>%
  filter(!is.na(b)) %>%
  mutate(
    ci_lo = b - 1.96 * se,
    ci_hi = b + 1.96 * se,
    sig = sig_star(p),
    irr_label = ifelse(irr_group == "low_irr", "Low Irrigation", "High Irrigation"),
    irr_label = factor(irr_label, levels = c("Low Irrigation", "High Irrigation")),
    window = factor(window, levels = win_order, labels = win_labels),
    coef_label = case_when(
      coef_type == "SRD"  ~ "SR \u00d7 D",
      coef_type == "SRH"  ~ "SR \u00d7 Heat",
      coef_type == "DH"   ~ "D \u00d7 Heat",
      coef_type == "SRDH" ~ "SR \u00d7 D \u00d7 Heat"
    ),
    coef_label = factor(coef_label,
      levels = c("SR \u00d7 D", "SR \u00d7 Heat",
                 "D \u00d7 Heat", "SR \u00d7 D \u00d7 Heat"))
  )

pB <- ggplot(d_irr_long, aes(y = irr_label, x = b, color = window)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey40") +
  geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi),
                  position = position_dodge(width = 0.6),
                  size = 0.4, linewidth = 0.6) +
  scale_color_manual(values = win_colors, name = "Window",
                     labels = win_labels) +
  facet_wrap(~coef_label, scales = "free_x", nrow = 1) +
  labs(title = "Heterogeneity by Irrigation Level",
       subtitle = "Spec(2), median split on irr_frac. Grid+year FE.",
       x = "Coefficient estimate", y = NULL) +
  theme_coef

ggsave(file.path(figdir, "v3_het_irrigation.png"), pB,
       width = 16, height = 5, dpi = 300, bg = "white")
cat("Saved: v3_het_irrigation.png\n")

cat("=== v3_heterogeneity_plots.R COMPLETE ===\n")
