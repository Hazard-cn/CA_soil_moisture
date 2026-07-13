# =============================================================================
# fig_spec_curve.R — Specification Curve: 3 panels (SR×D×H, SR×Heat, SR×D)
# Purpose: Publication-quality spec curve from step8b_spec_curve.csv
# Author: YangSu / Claude Code
# Date: 2026-03-22
# =============================================================================

set.seed(42)

# --- 0. Packages ---
library(ggplot2)
library(dplyr)
library(tidyr)
library(patchwork)

# --- 1. Paths ---
projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
infile  <- file.path(projdir, "output/tables/step8b_spec_curve.csv")
outfile <- file.path(projdir, "output/figures/step8b_spec_curve_compound.png")

# --- 2. Load data ---
spec <- read.csv(infile, stringsAsFactors = FALSE)
cat("Specs loaded:", nrow(spec), "\n")

# Check completeness
cat("Non-missing b_triple:", sum(!is.na(spec$b_triple)), "/", nrow(spec), "\n")

# --- 3. Prepare data ---
# Sort by effect size for each estimand
spec_triple <- spec %>%
  filter(!is.na(b_triple)) %>%
  arrange(b_triple) %>%
  mutate(
    rank = row_number(),
    sig = case_when(
      p_triple < 0.01 ~ "p < 0.01",
      p_triple < 0.05 ~ "p < 0.05",
      p_triple < 0.10 ~ "p < 0.10",
      TRUE ~ "n.s."
    ),
    sign_color = ifelse(b_triple >= 0, "positive", "negative")
  )

spec_heat <- spec %>%
  filter(!is.na(b_heat)) %>%
  arrange(b_heat) %>%
  mutate(
    rank = row_number(),
    sig = case_when(
      p_heat < 0.01 ~ "p < 0.01",
      p_heat < 0.05 ~ "p < 0.05",
      p_heat < 0.10 ~ "p < 0.10",
      TRUE ~ "n.s."
    ),
    sign_color = ifelse(b_heat >= 0, "positive", "negative")
  )

spec_drought <- spec %>%
  filter(!is.na(b_drought)) %>%
  arrange(b_drought) %>%
  mutate(
    rank = row_number(),
    sig = case_when(
      p_drought < 0.01 ~ "p < 0.01",
      p_drought < 0.05 ~ "p < 0.05",
      p_drought < 0.10 ~ "p < 0.10",
      TRUE ~ "n.s."
    ),
    sign_color = ifelse(b_drought >= 0, "positive", "negative")
  )

# --- 4. Summary statistics ---
cat("\n=== SR×D×H ===\n")
cat("Positive:", sum(spec_triple$b_triple > 0), "/", nrow(spec_triple), "\n")
cat("Pos-sig (10%):", sum(spec_triple$b_triple > 0 & spec_triple$p_triple < 0.10), "\n")
cat("Neg-sig (10%):", sum(spec_triple$b_triple < 0 & spec_triple$p_triple < 0.10), "\n")

cat("\n=== SR×Heat ===\n")
cat("Positive:", sum(spec_heat$b_heat > 0), "/", nrow(spec_heat), "\n")
cat("Pos-sig (10%):", sum(spec_heat$b_heat > 0 & spec_heat$p_heat < 0.10), "\n")
cat("Neg-sig (10%):", sum(spec_heat$b_heat < 0 & spec_heat$p_heat < 0.10), "\n")

cat("\n=== SR×D ===\n")
cat("Positive:", sum(spec_drought$b_drought > 0), "/", nrow(spec_drought), "\n")
cat("Pos-sig (10%):", sum(spec_drought$b_drought > 0 & spec_drought$p_drought < 0.10), "\n")
cat("Neg-sig (10%):", sum(spec_drought$b_drought < 0 & spec_drought$p_drought < 0.10), "\n")

# --- 5. Color palette ---
sig_colors <- c(
  "p < 0.01" = "#7B2D8E",  # compound purple
  "p < 0.05" = "#2171B5",  # blue
  "p < 0.10" = "#6BAED6",  # light blue
  "n.s."     = "grey70"
)

# --- 6. Panel 1: SR×D×H (main) ---
p1 <- ggplot(spec_triple, aes(x = rank, y = b_triple)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "grey50") +
  geom_point(aes(color = sig), size = 1.8) +
  geom_errorbar(aes(ymin = b_triple - 1.96 * se_triple,
                     ymax = b_triple + 1.96 * se_triple,
                     color = sig),
                width = 0, linewidth = 0.3, alpha = 0.6) +
  scale_color_manual(values = sig_colors, name = "Significance") +
  labs(
    title = "A. SR × Drought × Heat (core estimand)",
    x = "Specification (sorted by effect size)",
    y = "Coefficient"
  ) +
  theme_minimal(base_size = 10) +
  theme(
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    legend.position = "bottom",
    plot.title = element_text(face = "bold", size = 11)
  )

# --- 7. Panel 2: SR×Heat (parallel) ---
p2 <- ggplot(spec_heat, aes(x = rank, y = b_heat)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "grey50") +
  geom_point(aes(color = sig), size = 1.8) +
  geom_errorbar(aes(ymin = b_heat - 1.96 * se_heat,
                     ymax = b_heat + 1.96 * se_heat,
                     color = sig),
                width = 0, linewidth = 0.3, alpha = 0.6) +
  scale_color_manual(values = sig_colors, name = "Significance") +
  labs(
    title = "B. SR × Heat",
    x = "Specification (sorted by effect size)",
    y = "Coefficient"
  ) +
  theme_minimal(base_size = 10) +
  theme(
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    legend.position = "bottom",
    plot.title = element_text(face = "bold", size = 11)
  )

# --- 8. Panel 3: SR×D (secondary) ---
p3 <- ggplot(spec_drought, aes(x = rank, y = b_drought)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "grey50") +
  geom_point(aes(color = sig), size = 1.8) +
  geom_errorbar(aes(ymin = b_drought - 1.96 * se_drought,
                     ymax = b_drought + 1.96 * se_drought,
                     color = sig),
                width = 0, linewidth = 0.3, alpha = 0.6) +
  scale_color_manual(values = sig_colors, name = "Significance") +
  labs(
    title = "C. SR × Drought (secondary/suggestive)",
    x = "Specification (sorted by effect size)",
    y = "Coefficient"
  ) +
  theme_minimal(base_size = 10) +
  theme(
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    legend.position = "bottom",
    plot.title = element_text(face = "bold", size = 11)
  )

# --- 9. Combine and export ---
combined <- p1 / p2 / p3 +
  plot_layout(guides = "collect") &
  theme(legend.position = "bottom")

ggsave(outfile, combined,
       width = 12, height = 10, dpi = 300, bg = "white")

cat("\nFigure saved to:", outfile, "\n")
cat("Done.\n")
