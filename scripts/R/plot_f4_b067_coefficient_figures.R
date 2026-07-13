# =============================================================================
# F4-B067 mean/raw coefficient plots.
# Input: f4_b067_mean_raw_unified_coefficients_effects.csv
# Output: output/figures/0604 + Chinese "huibao" directory via Unicode escapes.
# =============================================================================

set.seed(42)

projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
infile <- file.path(
  projdir,
  "temp/2026-06-04_f4_b067_full_bootstrap_counterfactual",
  "f4_b067_mean_raw_unified_coefficients_effects.csv"
)
outdir <- file.path(projdir, "output/figures/f4_b067_stage")
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(patchwork)
  library(readr)
  library(scales)
  library(stringr)
})

stopifnot(file.exists(infile))

df <- readr::read_csv(infile, show_col_types = FALSE) %>%
  filter(sample_id == "B067", branch == "mean", transform == "raw") %>%
  mutate(
    estimate = as.numeric(estimate),
    model_se = as.numeric(model_se),
    model_p = as.numeric(model_p),
    model_ci_lo_95 = as.numeric(model_ci_lo_95),
    model_ci_hi_95 = as.numeric(model_ci_hi_95),
    bs_se = as.numeric(bs_se),
    bs_ci_lo_95 = as.numeric(bs_ci_lo_95),
    bs_ci_hi_95 = as.numeric(bs_ci_hi_95),
    ci_lo = ifelse(!is.na(bs_ci_lo_95), bs_ci_lo_95, model_ci_lo_95),
    ci_hi = ifelse(!is.na(bs_ci_hi_95), bs_ci_hi_95, model_ci_hi_95),
    sig_plot = case_when(
      record_type == "rhs_coefficient" & !is.na(model_p) & model_p < 0.05 ~ "p < 0.05",
      record_type != "rhs_coefficient" & !is.na(ci_lo) & !is.na(ci_hi) & ci_lo * ci_hi > 0 ~ "CI excludes 0",
      TRUE ~ "not significant"
    )
  )

if (nrow(df) != 1078) {
  stop(sprintf("Unexpected mean/raw row count: %s", nrow(df)))
}

hazard_levels <- c("drought", "heat", "hotdry")
hazard_labels <- c(drought = "Drought", heat = "Heat", hotdry = "Hot-dry")
hazard_colors <- c(drought = "#8B5A2B", heat = "#C7252E", hotdry = "#6A3D9A")
effect_colors <- c(IE = "#2166AC", DE = "#E66101", TE = "#111111")
ca_colors <- c(P25 = "#9E9E9E", P50 = "#3182BD", P75 = "#08519C")
irr_colors <- c(high_irr = "#2166AC", low_irr = "#B2182B")
zone_order <- c("NE", "HHH", "NW", "SW", "SH")
zone_labels <- c(NE = "NE", HHH = "HHH", NW = "NW", SW = "SW", SH = "SH")

df <- df %>%
  mutate(
    hazard = factor(hazard, levels = hazard_levels),
    hazard_label = factor(hazard_labels[as.character(hazard)], levels = hazard_labels[hazard_levels]),
    point_shape = factor(sig_plot, levels = c("p < 0.05", "CI excludes 0", "not significant"))
  )

theme_coef <- theme_minimal(base_size = 10, base_family = "sans") +
  theme(
    panel.background = element_blank(),
    plot.background = element_rect(fill = "white", colour = NA),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title = element_text(size = 10),
    axis.text = element_text(size = 8),
    strip.text = element_text(size = 9, face = "bold"),
    plot.title = element_text(size = 12, face = "bold"),
    plot.subtitle = element_text(size = 9),
    legend.position = "bottom",
    legend.title = element_text(size = 9),
    legend.text = element_text(size = 8)
  )

shape_scale <- scale_shape_manual(
  values = c("p < 0.05" = 16, "CI excludes 0" = 16, "not significant" = 21),
  breaks = c("p < 0.05", "CI excludes 0", "not significant"),
  name = "Significance"
)

save_png <- function(plot, filename, width = 180, height = 100) {
  path <- file.path(outdir, filename)
  ggsave(path, plot, width = width, height = height, units = "mm", dpi = 300, bg = "white")
  invisible(path)
}

coefplot_base <- function(data, xlab, title = NULL) {
  ggplot(data, aes(x = estimate, y = label)) +
    geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.35, color = "grey45") +
    geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi, color = color_key), orientation = "y", width = 0.22, linewidth = 0.6) +
    geom_point(aes(color = color_key, shape = point_shape), size = 2.8, stroke = 0.8, fill = "white") +
    shape_scale +
    labs(x = xlab, y = NULL, title = title) +
    theme_coef
}

single_coef_panel <- function(data, xlab = "Coefficient") {
  ggplot(data, aes(x = estimate, y = 1)) +
    geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.35, color = "grey45") +
    geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi, color = color_key), orientation = "y", width = 0.18, linewidth = 0.65) +
    geom_point(aes(color = color_key, shape = point_shape), size = 2.8, stroke = 0.8, fill = "white") +
    shape_scale +
    labs(x = xlab, y = NULL, title = unique(data$panel_title)) +
    theme_coef +
    theme(axis.text.y = element_blank(), legend.position = "none")
}

# Fig 1: baseline a1 and b.
d1 <- df %>%
  filter(record_type == "rhs_coefficient", layer == "baseline", role %in% c("a1", "b")) %>%
  mutate(
    label = hazard_labels[as.character(hazard)],
    label = factor(label, levels = rev(hazard_labels[hazard_levels])),
    color_key = as.character(hazard)
  )

p1a <- coefplot_base(d1 %>% filter(role == "a1"), "a1 coefficient", "Hazard -> soil moisture") +
  scale_color_manual(values = hazard_colors, guide = "none")
p1b <- coefplot_base(d1 %>% filter(role == "b"), "b coefficient", "Soil moisture -> ln(yield)") +
  scale_color_manual(values = hazard_colors, guide = "none")
fig1 <- p1a + p1b +
  plot_annotation(
    title = "Fig 1. Baseline mechanism channel",
    subtitle = "F4-B067, mean mediator, raw variables; bootstrap CI used where available."
  )
save_png(fig1, "fig1_baseline_channel.png", width = 180, height = 82)

# Fig 2: baseline c3 and a3, independent x scale per panel.
d2 <- df %>%
  filter(record_type == "rhs_coefficient", layer == "baseline", role %in% c("c3", "a3")) %>%
  mutate(
    color_key = as.character(hazard),
    panel_title = paste0(hazard_labels[as.character(hazard)], " | ", role),
    role_order = ifelse(role == "c3", 1L, 2L),
    hazard_order = match(as.character(hazard), hazard_levels)
  ) %>%
  arrange(hazard_order, role_order)
fig2_panels <- lapply(seq_len(nrow(d2)), function(i) {
  single_coef_panel(d2[i, ], "Coefficient") +
    scale_color_manual(values = hazard_colors, guide = "none")
})
fig2 <- wrap_plots(fig2_panels, ncol = 2) +
  plot_annotation(
    title = "Fig 2. Baseline SR modulation",
    subtitle = "Rows are hazards; columns are c3 and a3. Each panel uses its own x scale."
  )
save_png(fig2, "fig2_baseline_sr_modulation.png", width = 180, height = 135)

# Fig 3: baseline IE/DE/TE gradients across SR P25/P50/P75.
d3 <- df %>%
  filter(record_type == "iede_effect", layer == "baseline", ca_level %in% c("P25", "P50", "P75")) %>%
  mutate(
    effect = factor(effect, levels = c("IE", "DE", "TE")),
    ca_level = factor(ca_level, levels = c("P25", "P50", "P75"))
  )
fig3 <- ggplot(d3, aes(x = ca_level, y = estimate, color = effect, group = effect, shape = point_shape)) +
  geom_hline(yintercept = 0, linetype = "dashed", linewidth = 0.35, color = "grey45") +
  geom_line(linewidth = 0.55, position = position_dodge(width = 0.22)) +
  geom_errorbar(aes(ymin = ci_lo, ymax = ci_hi), width = 0.10, linewidth = 0.50, position = position_dodge(width = 0.22)) +
  geom_point(size = 2.6, stroke = 0.8, fill = "white", position = position_dodge(width = 0.22)) +
  facet_wrap(~ hazard_label, ncol = 1, scales = "free_x") +
  scale_color_manual(values = effect_colors, name = "Effect") +
  shape_scale +
  labs(
    x = "SR level",
    y = "Conditional effect",
    title = "Fig 3. Baseline IE/DE/TE decomposition across SR levels",
    subtitle = "The x axis is SR level; each line shows how IE, DE, or TE changes from P25 to P75."
  ) +
  theme_coef
save_png(fig3, "fig3_baseline_iede_typology.png", width = 180, height = 128)

# Fig 4: full-sample irrigation heterogeneity c3.
d4 <- df %>%
  filter(record_type == "rhs_coefficient", layer == "heterogeneity", subgroup_dim == "irr_group", role == "c3") %>%
  mutate(
    label = factor(subgroup, levels = c("low_irr", "high_irr"), labels = c("Low irrigation", "High irrigation")),
    color_key = as.character(subgroup)
  )
fig4 <- ggplot(d4, aes(x = estimate, y = label, color = color_key, shape = point_shape)) +
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.35, color = "grey45") +
  geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi), orientation = "y", width = 0.22, linewidth = 0.65) +
  geom_point(size = 3.0, stroke = 0.8, fill = "white") +
  facet_wrap(~ hazard_label, ncol = 1, scales = "free_x") +
  scale_color_manual(values = irr_colors, name = "Group") +
  shape_scale +
  labs(x = "c3 coefficient", y = NULL, title = "Fig 4. Irrigation heterogeneity in SR buffering") +
  theme_coef
save_png(fig4, "fig4_het_irrigation_c3.png", width = 180, height = 128)

# Fig 5: production-zone heterogeneity c3.
d5 <- df %>%
  filter(record_type == "rhs_coefficient", layer == "heterogeneity", subgroup_dim == "maize_zone", role == "c3", subgroup %in% zone_order) %>%
  mutate(
    label = factor(zone_labels[subgroup], levels = rev(zone_labels[zone_order])),
    color_key = ifelse(as.character(hazard) == "drought" & subgroup == "SW" & estimate < 0, "SW_drought_negative", as.character(hazard))
  )
zone_colors <- c(hazard_colors, SW_drought_negative = "#B2182B")
fig5 <- ggplot(d5, aes(x = estimate, y = label, color = color_key, shape = point_shape)) +
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.35, color = "grey45") +
  geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi), orientation = "y", width = 0.20, linewidth = 0.55) +
  geom_point(size = 2.7, stroke = 0.8, fill = "white") +
  facet_wrap(~ hazard_label, ncol = 3, scales = "free_x") +
  scale_color_manual(values = zone_colors, guide = "none") +
  shape_scale +
  labs(
    x = "c3 coefficient",
    y = NULL,
    title = "Fig 5. Production-zone heterogeneity in SR buffering",
    subtitle = "SW drought is highlighted in red when the c3 point estimate is negative."
  ) +
  theme_coef
save_png(fig5, "fig5_het_zone_c3.png", width = 180, height = 95)

# Fig 6: AI>2 dry-area irrigation gradient c3.
d6 <- df %>%
  filter(record_type == "rhs_coefficient", layer == "ai_gt2_irrigation", role == "c3") %>%
  mutate(
    label = factor(subgroup, levels = c("low_irr", "high_irr"), labels = c("Low irrigation", "High irrigation")),
    color_key = as.character(subgroup)
  )
fig6 <- ggplot(d6, aes(x = estimate, y = label, color = color_key, shape = point_shape)) +
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.35, color = "grey45") +
  geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi), orientation = "y", width = 0.24, linewidth = 0.70) +
  geom_point(size = 3.2, stroke = 0.8, fill = "white") +
  facet_wrap(~ hazard_label, ncol = 1, scales = "free_x") +
  scale_color_manual(values = irr_colors, name = "Group") +
  shape_scale +
  labs(
    x = "c3 coefficient",
    y = NULL,
    title = "Fig 6. AI > 2 dry-area irrigation gradient",
    subtitle = "Dry-grid subsamples are defined by grid-mean PET/P > 2."
  ) +
  theme_coef
save_png(fig6, "fig6_ai2_irrigation_c3.png", width = 180, height = 128)

# Fig 7: IE/DE/TE gradients by irrigation group across SR P25/P50/P75.
d7 <- df %>%
  filter(record_type == "iede_effect", layer == "heterogeneity", subgroup_dim == "irr_group", ca_level %in% c("P25", "P50", "P75"), effect %in% c("IE", "DE", "TE")) %>%
  mutate(
    effect = factor(effect, levels = c("IE", "DE", "TE")),
    ca_level = factor(ca_level, levels = c("P25", "P50", "P75")),
    irr_label = factor(subgroup, levels = c("high_irr", "low_irr"), labels = c("High irrigation", "Low irrigation")),
    color_key = as.character(effect)
  )
fig7 <- ggplot(d7, aes(x = ca_level, y = estimate, color = effect, group = effect, shape = point_shape)) +
  geom_hline(yintercept = 0, linetype = "dashed", linewidth = 0.35, color = "grey45") +
  geom_line(linewidth = 0.50, position = position_dodge(width = 0.22)) +
  geom_errorbar(aes(ymin = ci_lo, ymax = ci_hi), width = 0.09, linewidth = 0.45, position = position_dodge(width = 0.22)) +
  geom_point(size = 2.2, stroke = 0.8, fill = "white", position = position_dodge(width = 0.22)) +
  facet_grid(hazard_label ~ irr_label, scales = "free_y") +
  scale_color_manual(values = effect_colors, name = "Effect") +
  shape_scale +
  labs(
    x = "SR level",
    y = "Conditional effect",
    title = "Fig 7. IE/DE/TE by irrigation status across SR levels",
    subtitle = "The x axis is SR level; separate panels show whether the gradient differs by irrigation group."
  ) +
  theme_coef
save_png(fig7, "fig7_het_irr_iede.png", width = 180, height = 145)

# Fig 8: scenario contrasts.
d8 <- df %>%
  filter(record_type == "counterfactual") %>%
  mutate(
    scenario_label = case_when(
      str_detect(scenario, "P50") ~ "Hazard P50",
      str_detect(scenario, "P90") ~ "Hazard P90",
      TRUE ~ scenario
    ),
    group_label = case_when(
      layer == "baseline" ~ "Baseline: all",
      layer == "ai_gt5_pooled" ~ "AI>5: all",
      layer == "ai_gt2_irrigation" ~ paste0("AI>2: ", subgroup),
      subgroup_dim == "irr_group" ~ paste0("Irrigation: ", subgroup),
      subgroup_dim == "maize_zone" ~ paste0("Zone: ", subgroup),
      TRUE ~ paste(layer, subgroup, sep = ": ")
    ),
    group_order = case_when(
      group_label == "Baseline: all" ~ 1,
      str_starts(group_label, "Irrigation:") ~ 2,
      str_starts(group_label, "Zone:") ~ 3,
      str_starts(group_label, "AI>2:") ~ 4,
      group_label == "AI>5: all" ~ 5,
      TRUE ~ 9
    ),
    group_label = factor(group_label, levels = rev(unique(group_label[order(group_order, group_label)]))),
    color_key = scenario_label
  )
scenario_colors <- c("Hazard P50" = "#4D4D4D", "Hazard P90" = "#D95F02")
fig8 <- ggplot(d8, aes(x = estimate, y = group_label, color = color_key, shape = color_key)) +
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.35, color = "grey45") +
  geom_errorbar(aes(xmin = bs_ci_lo_95, xmax = bs_ci_hi_95), orientation = "y", width = 0.18, linewidth = 0.52, position = position_dodge(width = 0.45)) +
  geom_point(size = 2.3, position = position_dodge(width = 0.45)) +
  facet_wrap(~ hazard_label, ncol = 3, scales = "free_x") +
  scale_x_continuous(labels = percent_format(accuracy = 0.1)) +
  scale_color_manual(values = scenario_colors, name = "Scenario") +
  scale_shape_manual(values = c("Hazard P50" = 16, "Hazard P90" = 17), name = "Scenario") +
  labs(
    x = "Percent yield contrast: TE(P75) - TE(P25)",
    y = NULL,
    title = "Fig 8. Scenario contrasts by hazard and subgroup",
    subtitle = "Contrasts are conditional scenario calculations, not causal counterfactual estimates."
  ) +
  theme_coef
save_png(fig8, "fig8_counterfactual.png", width = 180, height = 145)

inventory <- tibble::tibble(
  figure = paste0("fig", 1:8),
  file = c(
    "fig1_baseline_channel.png",
    "fig2_baseline_sr_modulation.png",
    "fig3_baseline_iede_typology.png",
    "fig4_het_irrigation_c3.png",
    "fig5_het_zone_c3.png",
    "fig6_ai2_irrigation_c3.png",
    "fig7_het_irr_iede.png",
    "fig8_counterfactual.png"
  )
) %>%
  mutate(
    path = file.path(outdir, file),
    exists = file.exists(path),
    size_bytes = ifelse(exists, file.info(path)$size, NA_real_)
  )
readr::write_csv(inventory, file.path(outdir, "figure_inventory.csv"))

if (!all(inventory$exists)) {
  stop("Some figures were not written.")
}

copy_code <- paste0(
  "from pathlib import Path\n",
  "import csv, shutil\n",
  "stage = Path(r'C:/YangSu/00_Project/CA_mechanism/regression_SR/output/figures/f4_b067_stage')\n",
  "target = Path(r'C:/YangSu/00_Project/CA_mechanism/regression_SR/output/figures') / ('0604' + '\\u6c47' + '\\u62a5')\n",
  "target.mkdir(parents=True, exist_ok=True)\n",
  "rows = []\n",
  "for p in sorted(stage.glob('fig*.png')):\n",
  "    dst = target / p.name\n",
  "    shutil.copy2(p, dst)\n",
  "    rows.append({'figure': p.stem.split('_')[0], 'file': p.name, 'path': str(dst), 'exists': dst.exists(), 'size_bytes': dst.stat().st_size})\n",
  "with (target / 'figure_inventory.csv').open('w', encoding='utf-8-sig', newline='') as f:\n",
  "    writer = csv.DictWriter(f, fieldnames=['figure', 'file', 'path', 'exists', 'size_bytes'])\n",
  "    writer.writeheader()\n",
  "    writer.writerows(rows)\n",
  "print(target)\n"
)
copy_script <- file.path(outdir, "copy_to_unicode_output.py")
writeLines(copy_code, copy_script, useBytes = TRUE)
copy_status <- system2("python", copy_script)
if (!identical(copy_status, 0L)) {
  stop("Copying figures to the Unicode output directory failed.")
}

invisible(inventory)
