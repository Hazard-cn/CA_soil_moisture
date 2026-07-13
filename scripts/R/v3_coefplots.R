# =============================================================================
# v3_coefplots.R
# Purpose: Generate all coefficient forest plots for v3 analysis
# Author:  YangSu + Claude
# Date:    2026-04-04
# Input:   output/tables/v3_step2_stage_single.csv
#          output/tables/v3_step2_stage_horserace.csv
#          output/tables/v3_step3_attenuation.csv
#          output/tables/v3_step5_robustness.csv
#          output/tables/v3_step1_baseline.csv
# Output:  output/figures/v3_coef_*.png
# =============================================================================

set.seed(42)

library(ggplot2)
library(dplyr)
library(tidyr)
library(patchwork)

projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
outdir  <- file.path(projdir, "output/tables")
figdir  <- file.path(projdir, "output/figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

# --- Color palette ---
sig_colors <- c("***" = "#1a237e",   # deep blue
                "**"  = "#1565c0",   # medium blue
                "*"   = "#64b5f6",   # light blue
                "n.s."= "grey60")

coef_colors <- c("SR_x_D"       = "#2196F3",  # blue
                 "SR_x_Heat"    = "#F44336",  # red
                 "D_x_Heat"     = "#FF9800",  # orange
                 "SR_x_D_x_Heat"= "#9C27B0")  # purple

sm_colors <- c("gleam" = "#4CAF50",  # green
               "swsm"  = "#FF9800",  # orange
               "era5l" = "#2196F3")  # blue

# --- Helper: significance stars ---
sig_star <- function(p) {
  case_when(
    p < 0.01 ~ "***",
    p < 0.05 ~ "**",
    p < 0.10 ~ "*",
    TRUE ~ "n.s."
  )
}

# Window ordering (chronological)
win_order <- c("v3pre30", "v3pm10", "v3he", "hepm10", "hema", "full")
win_labels <- c("v3pre30" = "V3-pre30", "v3pm10" = "V3\u00b110",
                "v3he" = "V3\u2192HE", "hepm10" = "HE\u00b110",
                "hema" = "HE\u2192MA", "full" = "Full season")

# Theme
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
# PLOT 1: Window Comparison — 6 windows, 3 coef panels (free scales)
# =============================================================================
cat("Generating Plot 1: Window Comparison...\n")

d_single <- read.csv(file.path(outdir, "v3_step2_stage_single.csv"),
                      stringsAsFactors = FALSE)

# Reshape to long
d_long <- d_single %>%
  transmute(
    window,
    # SR x D
    coef_SRD = b_SRD, se_SRD, p_SRD,
    # SR x Heat
    coef_SRH = b_SRH, se_SRH, p_SRH,
    # SR x D x H
    coef_SRDH = b_SRDH, se_SRDH, p_SRDH
  ) %>%
  pivot_longer(
    cols = -window,
    names_to = c(".value", "type"),
    names_pattern = "(.+)_(SR[DH]+)"
  ) %>%
  mutate(
    ci_lo = coef - 1.96 * se,
    ci_hi = coef + 1.96 * se,
    sig = sig_star(p),
    window = factor(window, levels = win_order, labels = win_labels),
    coef_label = case_when(
      type == "SRD"  ~ "SR \u00d7 D",
      type == "SRH"  ~ "SR \u00d7 Heat",
      type == "SRDH" ~ "SR \u00d7 D \u00d7 Heat"
    ),
    coef_label = factor(coef_label,
      levels = c("SR \u00d7 D", "SR \u00d7 Heat", "SR \u00d7 D \u00d7 Heat"))
  )

p1 <- ggplot(d_long, aes(y = window, x = coef, color = sig)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey40") +
  geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi), size = 0.5, linewidth = 0.7) +
  scale_color_manual(values = sig_colors, name = "Significance") +
  facet_wrap(~coef_label, scales = "free_x", nrow = 1) +
  labs(title = "SR Buffering Coefficients Across Growth Windows",
       subtitle = "Single-window Spec(2), grid+year FE, cluster(grid_id)",
       x = "Coefficient estimate (95% CI)", y = NULL) +
  theme_coef

ggsave(file.path(figdir, "v3_coef_windows.png"), p1,
       width = 14, height = 5, dpi = 300, bg = "white")

# =============================================================================
# PLOT 2: Horse-Race Scheme Comparison
# =============================================================================
cat("Generating Plot 2: Horse-Race Scheme Comparison...\n")

d_hr <- read.csv(file.path(outdir, "v3_step2_stage_horserace.csv"),
                  stringsAsFactors = FALSE)

d_hr <- d_hr %>%
  mutate(
    ci_lo = b - 1.96 * se,
    ci_hi = b + 1.96 * se,
    sig = sig_star(p),
    window = factor(window, levels = win_order, labels = win_labels),
    scheme_label = paste0("Scheme ", scheme),
    coef_label = case_when(
      coef_type == "SR_x_D"        ~ "SR \u00d7 D",
      coef_type == "SR_x_Heat"     ~ "SR \u00d7 Heat",
      coef_type == "D_x_Heat"      ~ "D \u00d7 Heat",
      coef_type == "SR_x_D_x_Heat" ~ "SR \u00d7 D \u00d7 Heat"
    ),
    coef_label = factor(coef_label,
      levels = c("SR \u00d7 D", "SR \u00d7 Heat",
                 "D \u00d7 Heat", "SR \u00d7 D \u00d7 Heat"))
  )

# Focus on SR interaction coefficients only
d_hr_sr <- d_hr %>% filter(coef_type %in% c("SR_x_D", "SR_x_Heat", "SR_x_D_x_Heat"))

p2 <- ggplot(d_hr_sr, aes(y = window, x = b, color = sig,
                            shape = scheme_label)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey40") +
  geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi),
                  position = position_dodge(width = 0.5),
                  size = 0.5, linewidth = 0.6) +
  scale_color_manual(values = sig_colors, name = "Significance") +
  scale_shape_manual(values = c(16, 17, 15), name = "Horse-Race Scheme") +
  facet_wrap(~coef_label, scales = "free_x", nrow = 1) +
  labs(title = "Horse-Race: Which Growth Period Drives SR Buffering?",
       subtitle = "Scheme i: V3\u00b110+HE\u00b110 | ii: V3\u2192HE+HE\u2192MA | iii: V3pre30+V3\u2192HE+HE\u2192MA",
       x = "Coefficient estimate (95% CI)", y = NULL) +
  theme_coef +
  theme(legend.box = "horizontal")

ggsave(file.path(figdir, "v3_coef_horserace.png"), p2,
       width = 14, height = 5.5, dpi = 300, bg = "white")

# =============================================================================
# PLOT 3: SM Source Attenuation
# =============================================================================
cat("Generating Plot 3: SM Source Attenuation...\n")

d_att <- read.csv(file.path(outdir, "v3_step3_attenuation.csv"),
                   stringsAsFactors = FALSE)

# Reshape: spec1 vs spec3 comparison
d_att_long <- d_att %>%
  transmute(
    window, sm_src,
    `Spec(1)_SRD` = b1_SRD, `se1_SRD` = se1_SRD,
    `Spec(3)_SRD` = b3_SRD, `se3_SRD` = se3_SRD,
    att_SRD,
    `Spec(1)_SRH` = b1_SRH, `se1_SRH` = se1_SRH,
    `Spec(3)_SRH` = b3_SRH, `se3_SRH` = se3_SRH,
    att_SRH
  )

# Plot attenuation for SR x D: paired dots
d_paired <- d_att %>%
  select(window, sm_src, b1_SRD, se1_SRD, b3_SRD, se3_SRD) %>%
  pivot_longer(
    cols = c(b1_SRD, b3_SRD),
    names_to = "spec",
    values_to = "b"
  ) %>%
  mutate(
    se = ifelse(spec == "b1_SRD", se1_SRD, se3_SRD),
    spec_label = ifelse(spec == "b1_SRD", "Spec(1)", "Spec(3)"),
    window = factor(window, levels = win_order, labels = win_labels),
    ci_lo = b - 1.96 * se,
    ci_hi = b + 1.96 * se
  )

p3 <- ggplot(d_paired, aes(y = window, x = b, color = sm_src,
                             shape = spec_label)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey40") +
  geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi),
                  position = position_dodge(width = 0.6),
                  size = 0.4, linewidth = 0.5) +
  scale_color_manual(values = sm_colors, name = "SM Source") +
  scale_shape_manual(values = c(16, 1), name = "Specification") +
  labs(title = "SR \u00d7 D Attenuation: Spec(1) vs Spec(3) by SM Source",
       subtitle = "Hollow = Spec(3) with SM controls; shift toward 0 = attenuation",
       x = "Coefficient estimate (95% CI)", y = NULL) +
  theme_coef +
  theme(legend.box = "horizontal")

ggsave(file.path(figdir, "v3_coef_attenuation.png"), p3,
       width = 12, height = 5.5, dpi = 300, bg = "white")

# =============================================================================
# PLOT 4: Robustness Summary — Year-Drop + FE + Prov-Year Windows
# =============================================================================
cat("Generating Plot 4: Robustness Summary...\n")

d_rob <- read.csv(file.path(outdir, "v3_step5_robustness.csv"),
                   stringsAsFactors = FALSE)

# --- 4A: Year-Drop ---
d_yd <- d_rob %>%
  filter(test == "year_drop") %>%
  mutate(
    ci_lo_SRD  = b_SRD  - 1.96 * se_SRD,
    ci_hi_SRD  = b_SRD  + 1.96 * se_SRD,
    ci_lo_SRH  = b_SRH  - 1.96 * se_SRH,
    ci_hi_SRH  = b_SRH  + 1.96 * se_SRH,
    ci_lo_SRDH = b_SRDH - 1.96 * se_SRDH,
    ci_hi_SRDH = b_SRDH + 1.96 * se_SRDH,
    variant_label = gsub("drop", "Drop ", variant)
  )

# Baseline values
d_base <- d_rob %>% filter(test == "fe_sensitivity" & variant == "grid_yr")
base_SRD  <- d_base$b_SRD
base_SRH  <- d_base$b_SRH
base_SRDH <- d_base$b_SRDH

# Reshape year-drop for faceted plot
d_yd_long <- d_yd %>%
  select(variant_label, b_SRD, se_SRD, p_SRD, b_SRH, se_SRH, p_SRH,
         b_SRDH, se_SRDH, p_SRDH) %>%
  pivot_longer(
    cols = -variant_label,
    names_to = c(".value", "type"),
    names_pattern = "(.+)_(SRD|SRH|SRDH)"
  ) %>%
  mutate(
    ci_lo = b - 1.96 * se,
    ci_hi = b + 1.96 * se,
    sig = sig_star(p),
    coef_label = case_when(
      type == "SRD"  ~ "SR \u00d7 D",
      type == "SRH"  ~ "SR \u00d7 Heat",
      type == "SRDH" ~ "SR \u00d7 D \u00d7 Heat"
    ),
    coef_label = factor(coef_label,
      levels = c("SR \u00d7 D", "SR \u00d7 Heat", "SR \u00d7 D \u00d7 Heat")),
    baseline = case_when(
      type == "SRD"  ~ base_SRD,
      type == "SRH"  ~ base_SRH,
      type == "SRDH" ~ base_SRDH
    )
  )

p4a <- ggplot(d_yd_long, aes(y = variant_label, x = b, color = sig)) +
  geom_vline(aes(xintercept = baseline), linetype = "solid",
             color = "grey50", linewidth = 0.5) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey80") +
  geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi), size = 0.5, linewidth = 0.7) +
  scale_color_manual(values = sig_colors, name = "Significance") +
  facet_wrap(~coef_label, scales = "free_x", nrow = 1) +
  labs(title = "Year-Drop Robustness (Full Season, Spec 2)",
       subtitle = "Vertical line = baseline; dashed = zero",
       x = "Coefficient estimate (95% CI)", y = NULL) +
  theme_coef

ggsave(file.path(figdir, "v3_coef_yeardrop.png"), p4a,
       width = 14, height = 4, dpi = 300, bg = "white")

# --- 4B: Prov-Year FE across windows ---
d_py <- d_rob %>%
  filter(test == "provyr_windows") %>%
  mutate(
    ci_lo_SRD  = b_SRD  - 1.96 * se_SRD,
    ci_hi_SRD  = b_SRD  + 1.96 * se_SRD,
    ci_lo_SRH  = b_SRH  - 1.96 * se_SRH,
    ci_hi_SRH  = b_SRH  + 1.96 * se_SRH,
    ci_lo_SRDH = b_SRDH - 1.96 * se_SRDH,
    ci_hi_SRDH = b_SRDH + 1.96 * se_SRDH
  )

d_py_long <- d_py %>%
  select(variant, b_SRD, se_SRD, p_SRD, b_SRH, se_SRH, p_SRH,
         b_SRDH, se_SRDH, p_SRDH) %>%
  pivot_longer(
    cols = -variant,
    names_to = c(".value", "type"),
    names_pattern = "(.+)_(SRD|SRH|SRDH)"
  ) %>%
  mutate(
    ci_lo = b - 1.96 * se,
    ci_hi = b + 1.96 * se,
    sig = sig_star(p),
    window = factor(variant, levels = win_order, labels = win_labels),
    coef_label = case_when(
      type == "SRD"  ~ "SR \u00d7 D",
      type == "SRH"  ~ "SR \u00d7 Heat",
      type == "SRDH" ~ "SR \u00d7 D \u00d7 Heat"
    ),
    coef_label = factor(coef_label,
      levels = c("SR \u00d7 D", "SR \u00d7 Heat", "SR \u00d7 D \u00d7 Heat"))
  )

p4b <- ggplot(d_py_long, aes(y = window, x = b, color = sig)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey40") +
  geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi), size = 0.5, linewidth = 0.7) +
  scale_color_manual(values = sig_colors, name = "Significance") +
  facet_wrap(~coef_label, scales = "free_x", nrow = 1) +
  labs(title = "Province \u00d7 Year FE Across Windows (Spec 2)",
       subtitle = "Strictest FE specification",
       x = "Coefficient estimate (95% CI)", y = NULL) +
  theme_coef

ggsave(file.path(figdir, "v3_coef_provyr_windows.png"), p4b,
       width = 14, height = 5, dpi = 300, bg = "white")

# --- 4C: Heat Threshold Sensitivity ---
d_ht <- d_rob %>%
  filter(test == "heat_threshold") %>%
  mutate(
    ci_lo_SRH  = b_SRH  - 1.96 * se_SRH,
    ci_hi_SRH  = b_SRH  + 1.96 * se_SRH,
    ci_lo_SRDH = b_SRDH - 1.96 * se_SRDH,
    ci_hi_SRDH = b_SRDH + 1.96 * se_SRDH,
    threshold = variant
  )

d_ht_long <- d_ht %>%
  select(threshold, b_SRH, se_SRH, p_SRH, b_SRDH, se_SRDH, p_SRDH) %>%
  pivot_longer(
    cols = -threshold,
    names_to = c(".value", "type"),
    names_pattern = "(.+)_(SRH|SRDH)"
  ) %>%
  mutate(
    ci_lo = b - 1.96 * se,
    ci_hi = b + 1.96 * se,
    sig = sig_star(p),
    coef_label = ifelse(type == "SRH", "SR \u00d7 Heat", "SR \u00d7 D \u00d7 Heat"),
    coef_label = factor(coef_label,
      levels = c("SR \u00d7 Heat", "SR \u00d7 D \u00d7 Heat"))
  )

p4c <- ggplot(d_ht_long, aes(y = threshold, x = b, color = sig)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey40") +
  geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi), size = 0.6, linewidth = 0.8) +
  scale_color_manual(values = sig_colors, name = "Significance") +
  facet_wrap(~coef_label, scales = "free_x", nrow = 1) +
  labs(title = "Heat Threshold Sensitivity (Full Season, Spec 2)",
       x = "Coefficient estimate (95% CI)", y = "Threshold") +
  theme_coef

ggsave(file.path(figdir, "v3_coef_heat_threshold.png"), p4c,
       width = 10, height = 3.5, dpi = 300, bg = "white")

cat("All coefficient plots generated successfully.\n")
cat("Output directory:", figdir, "\n")
