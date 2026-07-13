# =============================================================================
# v3proxy_plots.R
# Purpose: Coefficient plots for drought proxy comparison (v3proxy).
#          Handles: Set A/B/C, Competition, Heat consistency
#          Faceted by HotDryPr (off/on) and cut (full/ii/iv).
# Author:  YangSu + Claude
# Date:    2026-04-16
# Input:   output/tables/v3proxy_results_long.csv
# Output:  output/figures/v3proxy_*.png
# =============================================================================

set.seed(42)

library(ggplot2)
library(dplyr)
library(tidyr)
library(readr)
library(patchwork)

projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
tabdir  <- file.path(projdir, "output/tables")
figdir  <- file.path(projdir, "output/figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

# =============================================================================
# LOAD DATA
# =============================================================================
res <- read_csv(file.path(tabdir, "v3proxy_results_long.csv"), show_col_types = FALSE)
cat("Loaded", nrow(res), "rows from v3proxy_results_long.csv\n")
cat("Columns:", paste(names(res), collapse = ", "), "\n")
cat("model_set levels:", paste(unique(res$model_set), collapse = ", "), "\n")
cat("hdp levels:", paste(unique(res$hdp), collapse = ", "), "\n")

# =============================================================================
# LABELS & PALETTES
# =============================================================================
cut_labels <- c("full" = "Full Season", "ii" = "V3pm10 + HEpm10", "iv" = "V3pre30 + V3HE + HEMA")
hdp_labels <- c("off" = "Without HotDryPr", "on" = "With HotDryPr")

raw_order  <- c("full", "v3pm10", "hepm10", "v3pre30", "v3he", "hema")
raw_labels <- c("full" = "Full", "v3pm10" = "V3pm10", "hepm10" = "HEpm10",
                "v3pre30" = "V3pre30", "v3he" = "V3HE", "hema" = "HEMA")

source_labels <- c("gleam" = "GLEAM", "swsm" = "SWSM", "era" = "ERA5-Land", "baseline" = "Baseline")
layer_labels  <- c("surface" = "Surface", "rootzone" = "Rootzone", "baseline" = "Baseline")

sig_star <- function(p) {
  case_when(p < 0.01 ~ "***", p < 0.05 ~ "**", p < 0.10 ~ "*", TRUE ~ "n.s.")
}

sig_colors <- c("***" = "#1a237e", "**" = "#1565c0", "*" = "#64b5f6", "n.s." = "grey60")

source_colors <- c("GLEAM" = "#2E7D32", "SWSM" = "#E65100", "ERA5-Land" = "#1565C0", "Baseline" = "#455A64")
layer_shapes  <- c("Surface" = 16, "Rootzone" = 17, "Baseline" = 15)

set_colors <- c("Set A (SPEI)" = "#2171B5", "Set B (DrySM)" = "#CB181D")

# =============================================================================
# THEME
# =============================================================================
theme_proxy <- theme_minimal(base_size = 12, base_family = "sans") +
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.y = element_blank(),
    panel.grid.major.x = element_line(color = "grey90", linewidth = 0.4),
    strip.text = element_text(face = "bold", size = 10.5),
    legend.position = "bottom",
    legend.box = "vertical",
    legend.title = element_blank(),
    legend.text = element_text(size = 9.5),
    legend.margin = margin(t = 2, r = 2, b = 2, l = 2),
    plot.title = element_text(face = "bold", size = 14),
    plot.subtitle = element_text(size = 10.5, color = "grey35"),
    plot.caption = element_text(size = 9, hjust = 0),
    axis.title.y = element_blank(),
    axis.text.y = element_text(size = 9),
    axis.text.x = element_text(size = 9.5),
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    plot.margin = margin(t = 8, r = 12, b = 8, l = 8)
  )

# =============================================================================
# HELPER: add CI + sig columns
# =============================================================================
add_ci <- function(df) {
  df %>%
    filter(coef_present == 1) %>%
    mutate(
      ci_lo = b - 1.96 * se,
      ci_hi = b + 1.96 * se,
      sig = sig_star(p),
      sig = factor(sig, levels = c("***", "**", "*", "n.s."))
    )
}

# =============================================================================
# PLOT 1: Forest — Set A vs Set B, full cut, faceted by HDP
#         GLEAM-Sfc only for clean comparison
# =============================================================================
make_forest_AB <- function(cut_id = "full") {

  # Set A: baseline
  dA <- res %>%
    filter(model_set == "SetA", ctrl_version == "reduced", cut == cut_id,
           term_group %in% c("shock_coef", "buffer_interaction")) %>%
    add_ci() %>%
    mutate(
      set_label = "Set A (SPEI)",
      coef_label = case_when(
        term == "D" ~ "Shock: D",
        term == "D_x_ca" ~ "Buffer: SR\u00d7D",
        TRUE ~ term
      ),
      raw_label = raw_labels[raw_window]
    )

  # Set B: GLEAM surface only
  dB <- res %>%
    filter(model_set == "SetB", ctrl_version == "reduced", cut == cut_id,
           source == "gleam", layer == "surface",
           term_group %in% c("shock_coef", "buffer_interaction")) %>%
    add_ci() %>%
    mutate(
      set_label = "Set B (DrySM)",
      coef_label = case_when(
        term == "drysm" ~ "Shock: DrySM",
        term == "drysm_x_ca" ~ "Buffer: SR\u00d7DrySM",
        TRUE ~ term
      ),
      raw_label = raw_labels[raw_window]
    )

  dd <- bind_rows(dA, dB) %>%
    mutate(
      hdp_label = factor(hdp_labels[hdp], levels = hdp_labels),
      y_label = paste0(set_label, " | ", coef_label, " | ", raw_label)
    )

  # Order: Set A shock, Set A buffer, Set B shock, Set B buffer — per window
  dd <- dd %>%
    arrange(match(hdp, c("off", "on")),
            match(raw_window, raw_order),
            set_label, match(term_group, c("shock_coef", "buffer_interaction")))
  dd$y_label <- factor(dd$y_label, levels = rev(unique(dd$y_label)))

  p <- ggplot(dd, aes(x = b, y = y_label, color = sig)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
    geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi), size = 0.5, linewidth = 0.7) +
    scale_color_manual(values = sig_colors, drop = FALSE) +
    facet_wrap(~hdp_label, scales = "free_y", ncol = 2) +
    labs(
      title = paste0("Set A (SPEI) vs Set B (DrySM): ", cut_labels[[cut_id]]),
      subtitle = "Reduced controls, grid + year FE, GLEAM-Sfc for Set B",
      x = "Coefficient (95% CI)"
    ) +
    theme_proxy

  p
}

# Generate for all 3 cuts
for (ct in names(cut_labels)) {
  p <- make_forest_AB(ct)
  ggsave(file.path(figdir, paste0("v3proxy_forest_AB_", ct, ".png")),
         p, width = 14, height = 7, dpi = 300, bg = "white")
}
cat("Saved forest_AB plots\n")

# =============================================================================
# PLOT 2: Set B across all 6 SM sources (full cut, HDP off only)
#         Shows robustness of DrySM shock & buffer across SM products
# =============================================================================
make_source_comparison <- function(cut_id = "full", hdp_id = "off") {

  dd <- res %>%
    filter(model_set == "SetB", ctrl_version == "reduced", cut == cut_id,
           hdp == hdp_id, source != "baseline",
           term_group %in% c("shock_coef", "buffer_interaction")) %>%
    add_ci() %>%
    mutate(
      source_label = factor(source_labels[source], levels = c("GLEAM", "SWSM", "ERA5-Land")),
      layer_label  = factor(layer_labels[layer], levels = c("Surface", "Rootzone")),
      raw_label    = raw_labels[raw_window],
      y_label = paste(source_label, layer_label, raw_label, sep = " | ")
    ) %>%
    arrange(match(raw_window, raw_order), source_label, layer_label)

  dd$y_label <- factor(dd$y_label, levels = rev(unique(dd$y_label)))

  dd_shock  <- dd %>% filter(term_group == "shock_coef")
  dd_buffer <- dd %>% filter(term_group == "buffer_interaction")

  p_shock <- ggplot(dd_shock, aes(x = b, y = y_label, color = source_label, shape = layer_label)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
    geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi), size = 0.5, linewidth = 0.6) +
    scale_color_manual(values = source_colors, drop = FALSE) +
    scale_shape_manual(values = layer_shapes, drop = FALSE) +
    labs(title = "DrySM shock coefficient", x = "Coefficient (95% CI)") +
    theme_proxy

  p_buffer <- ggplot(dd_buffer, aes(x = b, y = y_label, color = source_label, shape = layer_label)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
    geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi), size = 0.5, linewidth = 0.6) +
    scale_color_manual(values = source_colors, drop = FALSE) +
    scale_shape_manual(values = layer_shapes, drop = FALSE) +
    labs(title = "SR\u00d7DrySM buffering", x = "Coefficient (95% CI)") +
    theme_proxy

  p_shock + p_buffer +
    plot_annotation(
      title = paste0("Set B: DrySM across 6 SM sources (", cut_labels[[cut_id]], ", HDP=", hdp_id, ")"),
      subtitle = "Reduced controls, grid + year FE",
      theme = theme(plot.title = element_text(face = "bold", size = 14))
    ) +
    plot_layout(guides = "collect") &
    theme(legend.position = "bottom")
}

for (ct in names(cut_labels)) {
  for (hdp_id in c("off", "on")) {
    p <- make_source_comparison(ct, hdp_id)
    ggsave(file.path(figdir, paste0("v3proxy_source_", ct, "_hdp", hdp_id, ".png")),
           p, width = 16, height = 7, dpi = 300, bg = "white")
  }
}
cat("Saved source comparison plots\n")

# =============================================================================
# PLOT 3: Overlap diagnostic (Set C) — D vs DrySM coefficients
# =============================================================================
make_overlap <- function(cut_id = "full") {

  dd <- res %>%
    filter(model_set == "SetC", ctrl_version == "reduced", cut == cut_id,
           source == "gleam", layer == "surface",
           term_group %in% c("overlap_d", "overlap_drysm")) %>%
    add_ci() %>%
    mutate(
      hdp_label = factor(hdp_labels[hdp], levels = hdp_labels),
      proxy_label = if_else(term == "D", "D (SPEI)", "DrySM (SM)"),
      raw_label = raw_labels[raw_window],
      y_label = paste(proxy_label, raw_label, sep = " | ")
    )

  dd$y_label <- factor(dd$y_label, levels = rev(unique(dd$y_label)))

  p <- ggplot(dd, aes(x = b, y = y_label, color = sig)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
    geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi), size = 0.5, linewidth = 0.7) +
    scale_color_manual(values = sig_colors, drop = FALSE) +
    facet_wrap(~hdp_label, scales = "free_y", ncol = 2) +
    labs(
      title = paste0("Set C: Overlap Diagnostic (", cut_labels[[cut_id]], ")"),
      subtitle = "D and DrySM in same model (no interactions), GLEAM-Sfc",
      x = "Coefficient (95% CI)"
    ) +
    theme_proxy

  p
}

for (ct in names(cut_labels)) {
  p <- make_overlap(ct)
  ggsave(file.path(figdir, paste0("v3proxy_overlap_", ct, ".png")),
         p, width = 13, height = 6, dpi = 300, bg = "white")
}
cat("Saved overlap plots\n")

# =============================================================================
# PLOT 4: Competition — SR×D attenuation vs SR×DrySM attenuation
# =============================================================================
make_competition <- function(cut_id = "full") {

  # Baseline for comparison: Set A buffering and Set B buffering
  d_base_A <- res %>%
    filter(model_set == "SetA", ctrl_version == "reduced", cut == cut_id,
           term_group == "buffer_interaction") %>%
    add_ci() %>%
    mutate(context = "Alone", proxy = "SR\u00d7D")

  d_base_B <- res %>%
    filter(model_set == "SetB", ctrl_version == "reduced", cut == cut_id,
           source == "gleam", layer == "surface",
           term_group == "buffer_interaction") %>%
    add_ci() %>%
    mutate(context = "Alone", proxy = "SR\u00d7DrySM")

  # Competition
  d_comp_D <- res %>%
    filter(model_set == "CompeteD", ctrl_version == "reduced", cut == cut_id,
           source == "gleam", layer == "surface",
           term_group == "competition_d") %>%
    add_ci() %>%
    mutate(context = "+ DrySM control", proxy = "SR\u00d7D")

  d_comp_SM <- res %>%
    filter(model_set == "CompeteSM", ctrl_version == "reduced", cut == cut_id,
           source == "gleam", layer == "surface",
           term_group == "competition_sm") %>%
    add_ci() %>%
    mutate(context = "+ D control", proxy = "SR\u00d7DrySM")

  dd <- bind_rows(d_base_A, d_base_B, d_comp_D, d_comp_SM) %>%
    mutate(
      hdp_label = factor(hdp_labels[hdp], levels = hdp_labels),
      raw_label = raw_labels[raw_window],
      y_label = paste(context, raw_label, sep = " | ")
    )

  dd$y_label <- factor(dd$y_label, levels = rev(unique(dd$y_label)))

  p <- ggplot(dd, aes(x = b, y = y_label, color = sig)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
    geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi), size = 0.5, linewidth = 0.7) +
    scale_color_manual(values = sig_colors, drop = FALSE) +
    facet_grid(proxy ~ hdp_label, scales = "free_y") +
    labs(
      title = paste0("Competition Models (", cut_labels[[cut_id]], ")"),
      subtitle = "Buffering coefficient: alone vs with competing proxy, GLEAM-Sfc",
      x = "Coefficient (95% CI)"
    ) +
    theme_proxy

  p
}

for (ct in names(cut_labels)) {
  p <- make_competition(ct)
  ggsave(file.path(figdir, paste0("v3proxy_competition_", ct, ".png")),
         p, width = 14, height = 8, dpi = 300, bg = "white")
}
cat("Saved competition plots\n")

# =============================================================================
# PLOT 5: Heat consistency — SR×H with D vs DrySM control
# =============================================================================
make_heat <- function(cut_id = "full") {

  dd <- res %>%
    filter(module == "heat", model_set == "HeatCheck", ctrl_version == "reduced",
           cut == cut_id, source == "gleam", layer == "surface",
           term_group == "heat_buffer") %>%
    add_ci() %>%
    mutate(
      hdp_label = factor(hdp_labels[hdp], levels = hdp_labels),
      raw_label = raw_labels[raw_window],
      y_label = paste("SR\u00d7H", raw_label, sep = " | ")
    )

  dd$y_label <- factor(dd$y_label, levels = rev(unique(dd$y_label)))

  p <- ggplot(dd, aes(x = b, y = y_label, color = sig)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
    geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi), size = 0.5, linewidth = 0.7) +
    scale_color_manual(values = sig_colors, drop = FALSE) +
    facet_wrap(~hdp_label, ncol = 2) +
    labs(
      title = paste0("Heat Module: SR\u00d7H with DrySM control (", cut_labels[[cut_id]], ")"),
      subtitle = "GLEAM-Sfc background drought control, reduced controls",
      x = "Coefficient (95% CI)"
    ) +
    theme_proxy

  p
}

for (ct in names(cut_labels)) {
  p <- make_heat(ct)
  ggsave(file.path(figdir, paste0("v3proxy_heat_", ct, ".png")),
         p, width = 13, height = 5.5, dpi = 300, bg = "white")
}
cat("Saved heat plots\n")

# =============================================================================
# PLOT 6: HDP effect — how adding HotDryPr changes shock/buffer coefficients
# =============================================================================
make_hdp_effect <- function(cut_id = "full") {

  # Set A
  dA <- res %>%
    filter(model_set == "SetA", ctrl_version == "reduced", cut == cut_id,
           term_group %in% c("shock_coef", "buffer_interaction")) %>%
    add_ci() %>%
    mutate(
      set = "Set A (SPEI)",
      coef_type = if_else(term_group == "shock_coef", "Shock", "Buffer"),
      raw_label = raw_labels[raw_window]
    )

  # Set B (GLEAM-Sfc)
  dB <- res %>%
    filter(model_set == "SetB", ctrl_version == "reduced", cut == cut_id,
           source == "gleam", layer == "surface",
           term_group %in% c("shock_coef", "buffer_interaction")) %>%
    add_ci() %>%
    mutate(
      set = "Set B (DrySM)",
      coef_type = if_else(term_group == "shock_coef", "Shock", "Buffer"),
      raw_label = raw_labels[raw_window]
    )

  dd <- bind_rows(dA, dB) %>%
    mutate(
      hdp_label = factor(hdp_labels[hdp], levels = hdp_labels),
      y_label = paste(coef_type, raw_label, sep = " | ")
    )

  dd$y_label <- factor(dd$y_label, levels = rev(unique(dd$y_label)))

  p <- ggplot(dd, aes(x = b, y = y_label, color = hdp_label)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
    geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi),
                    position = position_dodge(width = 0.5),
                    size = 0.5, linewidth = 0.6) +
    scale_color_manual(values = c("Without HotDryPr" = "#1565C0", "With HotDryPr" = "#E65100")) +
    facet_wrap(~set, scales = "free_x", ncol = 2) +
    labs(
      title = paste0("HotDryPr Effect on Shock & Buffer (", cut_labels[[cut_id]], ")"),
      subtitle = "Does adding compound hot-dry days attenuate the drought proxy coefficients?",
      x = "Coefficient (95% CI)"
    ) +
    theme_proxy

  p
}

for (ct in names(cut_labels)) {
  p <- make_hdp_effect(ct)
  ggsave(file.path(figdir, paste0("v3proxy_hdp_effect_", ct, ".png")),
         p, width = 14, height = 6.5, dpi = 300, bg = "white")
}
cat("Saved HDP effect plots\n")

cat("\n=== v3proxy_plots.R COMPLETE ===\n")
