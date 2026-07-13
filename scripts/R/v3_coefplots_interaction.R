# =============================================================================
# v3_coefplots_interaction.R
# Purpose: Coefficient plots for 4specs x 3SM x 6windows interaction grid
# Author:  YangSu + Claude
# Date:    2026-04-05
# Input:   output/tables/v3_step4_interaction_grid.csv
# Output:  output/figures/v3_coef_sr_buffering.png
#          output/figures/v3_coef_sm_interactions.png
# =============================================================================

set.seed(42)

library(ggplot2)
library(dplyr)
library(tidyr)

projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
outdir  <- file.path(projdir, "output/tables")
figdir  <- file.path(projdir, "output/figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

# --- Color palettes ---
sig_colors <- c("***" = "#1a237e",
                "**"  = "#1565c0",
                "*"   = "#64b5f6",
                "n.s."= "grey60")

sm_colors <- c("gleam" = "#4CAF50",
               "swsm"  = "#FF9800",
               "era5l" = "#2196F3")

# --- Helpers ---
sig_star <- function(p) {
  case_when(
    p < 0.01 ~ "***",
    p < 0.05 ~ "**",
    p < 0.10 ~ "*",
    TRUE ~ "n.s."
  )
}

# Window ordering (chronological by growth stage)
win_order <- c("v3pre30", "v3pm10", "v3he", "hepm10", "hema", "full")
win_labels <- c("v3pre30" = "V3-pre30",
                "v3pm10"  = "V3\u00b110",
                "v3he"    = "V3\u2192HE",
                "hepm10"  = "HE\u00b110",
                "hema"    = "HE\u2192MA",
                "full"    = "Full season")

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
# LOAD DATA
# =============================================================================
cat("Loading v3_step4_interaction_grid.csv...\n")
d <- read.csv(file.path(outdir, "v3_step4_interaction_grid.csv"),
              stringsAsFactors = FALSE)
cat("Rows:", nrow(d), "\n")

# =============================================================================
# PLOT A: SR Buffering Panel (SR x D, SR x Heat, D x Heat, SR x D x Heat)
# =============================================================================
cat("Generating Plot A: SR Buffering Panel...\n")

# Pivot SR-related coefficients to long format
d_sr <- d %>%
  select(window, spec, sm_src,
         b_SRD, se_SRD, p_SRD,
         b_SRH, se_SRH, p_SRH,
         b_DH, se_DH, p_DH,
         b_SRDH, se_SRDH, p_SRDH) %>%
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
    window = factor(window, levels = win_order, labels = win_labels),
    coef_label = case_when(
      coef_type == "SRD"  ~ "SR \u00d7 D",
      coef_type == "SRH"  ~ "SR \u00d7 Heat",
      coef_type == "DH"   ~ "D \u00d7 Heat",
      coef_type == "SRDH" ~ "SR \u00d7 D \u00d7 Heat"
    ),
    coef_label = factor(coef_label,
      levels = c("SR \u00d7 D", "SR \u00d7 Heat",
                 "D \u00d7 Heat", "SR \u00d7 D \u00d7 Heat")),
    # Create combined spec+source label
    model_label = case_when(
      spec == "spec1" ~ "Spec(1)",
      spec == "spec2" ~ "Spec(2)",
      spec == "spec3" & sm_src == "gleam" ~ "Spec(3) GLEAM",
      spec == "spec3" & sm_src == "swsm"  ~ "Spec(3) SWSM",
      spec == "spec3" & sm_src == "era5l" ~ "Spec(3) ERA5L",
      spec == "spec4" & sm_src == "gleam" ~ "Spec(4) GLEAM",
      spec == "spec4" & sm_src == "swsm"  ~ "Spec(4) SWSM",
      spec == "spec4" & sm_src == "era5l" ~ "Spec(4) ERA5L"
    ),
    model_label = factor(model_label,
      levels = c("Spec(1)", "Spec(2)",
                 "Spec(3) GLEAM", "Spec(3) SWSM", "Spec(3) ERA5L",
                 "Spec(4) GLEAM", "Spec(4) SWSM", "Spec(4) ERA5L"))
  )

# Color by model type
model_colors <- c(
  "Spec(1)" = "#37474F",
  "Spec(2)" = "#78909C",
  "Spec(3) GLEAM" = "#4CAF50",
  "Spec(3) SWSM"  = "#FF9800",
  "Spec(3) ERA5L" = "#2196F3",
  "Spec(4) GLEAM" = "#1B5E20",
  "Spec(4) SWSM"  = "#E65100",
  "Spec(4) ERA5L" = "#0D47A1"
)

pA <- ggplot(d_sr, aes(y = window, x = b, color = model_label)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey40") +
  geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi),
                  position = position_dodge(width = 0.7),
                  size = 0.3, linewidth = 0.5) +
  scale_color_manual(values = model_colors, name = "Model") +
  facet_wrap(~coef_label, scales = "free_x", nrow = 1) +
  labs(title = "SR Buffering Coefficients: 6 Windows \u00d7 4 Specs \u00d7 3 SM Sources",
       subtitle = "Grid+year FE, cluster(grid_id). 95% CI shown.",
       x = "Coefficient estimate", y = NULL) +
  theme_coef +
  guides(color = guide_legend(nrow = 2))

ggsave(file.path(figdir, "v3_coef_sr_buffering.png"), pA,
       width = 16, height = 7, dpi = 300, bg = "white")
cat("Saved: v3_coef_sr_buffering.png\n")

# =============================================================================
# PLOT B: SM Interaction Panel (SM, SM x D, SM x Heat, SM x SR)
# =============================================================================
cat("Generating Plot B: SM Interaction Panel...\n")

d_sm <- d %>%
  filter(spec %in% c("spec3", "spec4")) %>%
  select(window, spec, sm_src,
         b_SM, se_SM, p_SM,
         b_SMD, se_SMD, p_SMD,
         b_SMH, se_SMH, p_SMH,
         b_SMSR, se_SMSR, p_SMSR) %>%
  pivot_longer(
    cols = c(starts_with("b_"), starts_with("se_"), starts_with("p_")),
    names_to = c(".value", "coef_type"),
    names_pattern = "(b|se|p)_(SM|SMD|SMH|SMSR)"
  ) %>%
  filter(!is.na(b)) %>%
  mutate(
    ci_lo = b - 1.96 * se,
    ci_hi = b + 1.96 * se,
    sig = sig_star(p),
    window = factor(window, levels = win_order, labels = win_labels),
    coef_label = case_when(
      coef_type == "SM"   ~ "SM (main)",
      coef_type == "SMD"  ~ "SM \u00d7 D",
      coef_type == "SMH"  ~ "SM \u00d7 Heat",
      coef_type == "SMSR" ~ "SM \u00d7 SR"
    ),
    coef_label = factor(coef_label,
      levels = c("SM (main)", "SM \u00d7 D", "SM \u00d7 Heat", "SM \u00d7 SR")),
    spec_label = ifelse(spec == "spec3", "Spec(3)", "Spec(4)")
  )

pB <- ggplot(d_sm, aes(y = window, x = b, color = sm_src, shape = spec_label)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey40") +
  geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi),
                  position = position_dodge(width = 0.6),
                  size = 0.3, linewidth = 0.5) +
  scale_color_manual(values = sm_colors, name = "SM Source") +
  scale_shape_manual(values = c("Spec(3)" = 16, "Spec(4)" = 17), name = "Spec") +
  facet_wrap(~coef_label, scales = "free_x", nrow = 1) +
  labs(title = "Soil Moisture Interaction Coefficients: 6 Windows \u00d7 3 SM Sources",
       subtitle = "Spec(3) = no compound, Spec(4) = with compound. Grid+year FE.",
       x = "Coefficient estimate", y = NULL) +
  theme_coef

ggsave(file.path(figdir, "v3_coef_sm_interactions.png"), pB,
       width = 16, height = 7, dpi = 300, bg = "white")
cat("Saved: v3_coef_sm_interactions.png\n")

cat("=== v3_coefplots_interaction.R COMPLETE ===\n")
