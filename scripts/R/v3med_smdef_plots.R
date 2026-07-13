# =============================================================================
# v3med_smdef_plots.R
# Purpose: Generate diagnostic + repair-attempt plots for the Model 8 b-path
#          inversion in v3med. Five plots:
#            1. b-path anomaly across 6 SM sources (raw SM vs DrySM cross-check)
#            2. Path D spec sensitivity (GLEAM-Sfc, 5 specifications)
#            3. Path A: Model 8 with SMdef (6-source forest)
#            4. SM tails smoking-gun (dry tail n.s. vs wet tail negative)
#            5. Bootstrap CIs for SMdef drought (GLEAM-Sfc + GLEAM-Root)
# Author:  YangSu + Claude
# Date:    2026-04-16
# =============================================================================

library(ggplot2)
library(dplyr)
library(tidyr)
library(readr)
library(stringr)
library(patchwork)
library(scales)

set.seed(42)

projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
outdir  <- file.path(projdir, "output/tables")
figdir  <- file.path(projdir, "output/figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

# ---- Theme & palettes ----
theme_med <- theme_minimal(base_size = 12, base_family = "sans") +
  theme(
    panel.grid.minor = element_blank(),
    strip.text = element_text(face = "bold", size = 11),
    legend.position = "bottom",
    plot.title = element_text(face = "bold", size = 13),
    plot.subtitle = element_text(size = 10, color = "grey40"),
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA)
  )

sig_colors <- c("***" = "#1a237e", "**"  = "#1565c0",
                "*"   = "#64b5f6", "n.s."= "grey60")

sm_order <- c("GLEAM-Sfc", "GLEAM-Root", "SWSM-L1", "SWSM-L3", "ERA5L-L1", "ERA5L-L3")

sig_star <- function(p) {
  case_when(
    p < 0.01 ~ "***",
    p < 0.05 ~ "**",
    p < 0.10 ~ "*",
    TRUE     ~ "n.s."
  )
}

# =============================================================================
# PLOT 1: b-path ANOMALY (original Model 8, 6 sources x 2 ctrl)
# =============================================================================
orig <- read_csv(file.path(outdir, "v3med_drought_model8_coefficients.csv"),
                 show_col_types = FALSE) %>%
  filter(fe_level == "L0", equation == "outcome", term == "SM") %>%
  mutate(sig = sig_star(p),
         sm_label = factor(sm_label, levels = sm_order),
         ctrl_label = ifelse(ctrl_version == "reduced",
                             "Reduced ctrl (irr + gdd10)",
                             "Full ctrl (+pr, et0, aridity)"),
         lo = b - 1.96*se, hi = b + 1.96*se)

p1 <- ggplot(orig, aes(x = b, y = sm_label, color = sig)) +
  geom_vline(xintercept = 0, color = "grey40", linetype = "dashed") +
  geom_pointrange(aes(xmin = lo, xmax = hi), size = 0.7, linewidth = 0.8) +
  geom_text(aes(label = sprintf("%.2f%s", b, sig)), vjust = -1, size = 3.3, show.legend = FALSE) +
  scale_color_manual(values = sig_colors, name = "Significance") +
  facet_wrap(~ ctrl_label) +
  labs(
    title = "Original Model 8 b-path: SM -> lnY coefficient (raw SM)",
    subtitle = "All 6 SM sources yield b<0 (violates mediation assumption b>0)",
    x = expression(paste("b coefficient (SM ", symbol("\\256"), " lnY)")),
    y = NULL
  ) +
  theme_med

ggsave(file.path(figdir, "v3med_smdef_bpath_anomaly.png"),
       plot = p1, width = 11, height = 5, dpi = 300, bg = "white")
cat("Saved v3med_smdef_bpath_anomaly.png\n")

# =============================================================================
# PLOT 2: PATH D DIAGNOSTIC (5 specs, GLEAM-Sfc)
# =============================================================================
pd <- read_csv(file.path(outdir, "v3med_bpath_diagnostic.csv"), show_col_types = FALSE)

pd_plot <- pd %>%
  filter(term %in% c("SM", "SM_linear", "SM_squared", "sm_q1", "sm_q4", "SMdef")) %>%
  mutate(
    spec_label = case_when(
      spec == "S1_baseline" ~ "S1. Baseline (grid+year FE)",
      spec == "S2_provyear_FE" ~ "S2. prov*year FE",
      spec == "S3_quadratic" ~ "S3. Quadratic SM",
      spec == "S4_tails" ~ "S4. SM tails (P25/P75)",
      spec == "S5_SMdef_provyear" ~ "S5. SMdef + prov*year FE"
    ),
    term_label = case_when(
      term == "SM" ~ "b (SM)",
      term == "SM_linear" ~ "b (SM linear)",
      term == "SM_squared" ~ "b (SM^2)",
      term == "sm_q1" ~ "b (1[SM<P25] dry tail)",
      term == "sm_q4" ~ "b (1[SM>P75] wet tail)",
      term == "SMdef" ~ "b (SMdef)"
    ),
    sig = sig_star(p),
    lo = b - 1.96*se, hi = b + 1.96*se,
    spec_order = factor(spec_label, levels = rev(c(
      "S1. Baseline (grid+year FE)",
      "S2. prov*year FE",
      "S3. Quadratic SM",
      "S4. SM tails (P25/P75)",
      "S5. SMdef + prov*year FE"
    )))
  )

p2 <- ggplot(pd_plot, aes(x = b, y = spec_order, color = sig, shape = term_label)) +
  geom_vline(xintercept = 0, color = "grey40", linetype = "dashed") +
  geom_pointrange(aes(xmin = lo, xmax = hi),
                  position = position_dodge(width = 0.6),
                  size = 0.6, linewidth = 0.8) +
  scale_color_manual(values = sig_colors, name = "Significance") +
  scale_shape_manual(values = c(16, 17, 15, 18, 3, 8), name = "Term") +
  labs(
    title = "Path D: Can any specification recover b > 0? (GLEAM-Sfc)",
    subtitle = "No spec yields positive SM coefficient; quadratic U-shape with min at SM ~0.41; wet-tail drives negative sign",
    x = "Coefficient (95% CI)",
    y = NULL
  ) +
  theme_med

ggsave(file.path(figdir, "v3med_smdef_pathD_diagnostic.png"),
       plot = p2, width = 12, height = 6, dpi = 300, bg = "white")
cat("Saved v3med_smdef_pathD_diagnostic.png\n")

# =============================================================================
# PLOT 3: PATH A SMdef MODEL 8 COEFFS (6 sources)
# =============================================================================
smc <- read_csv(file.path(outdir, "v3med_smdef_drought_coefficients.csv"),
                show_col_types = FALSE) %>%
  filter(fe_level == "L0", ctrl_version == "reduced")

a_tbl <- smc %>%
  mutate(
    tag = case_when(
      equation == "mediator" & term == "D_full" ~ "a1 (D -> SMdef)",
      equation == "mediator" & term == "SR_x_D_full" ~ "a3 (SR*D -> SMdef)",
      equation == "outcome"  & term == "SMdef" ~ "b (SMdef -> lnY)",
      equation == "outcome"  & term == "SR_x_D_full" ~ "c3 (SR*D -> lnY)",
      TRUE ~ NA_character_
    )
  ) %>%
  filter(!is.na(tag)) %>%
  mutate(
    sig = sig_star(p),
    sm_label = factor(sm_label, levels = sm_order),
    lo = b - 1.96*se, hi = b + 1.96*se,
    tag = factor(tag, levels = c("a1 (D -> SMdef)", "a3 (SR*D -> SMdef)",
                                  "b (SMdef -> lnY)", "c3 (SR*D -> lnY)"))
  )

p3 <- ggplot(a_tbl, aes(x = b, y = sm_label, color = sig)) +
  geom_vline(xintercept = 0, color = "grey40", linetype = "dashed") +
  geom_pointrange(aes(xmin = lo, xmax = hi), size = 0.6, linewidth = 0.8) +
  scale_color_manual(values = sig_colors, name = "Significance") +
  facet_wrap(~ tag, scales = "free_x", ncol = 2) +
  labs(
    title = "Path A: Model 8 with SMdef as mediator (L0, reduced ctrl)",
    subtitle = "a1 > 0 (drought increases deficit); a3 sign mixed; b > 0 (wrong for mediation); c3 > 0 robust",
    x = "Coefficient (95% CI)",
    y = NULL
  ) +
  theme_med

ggsave(file.path(figdir, "v3med_smdef_pathA_coefs.png"),
       plot = p3, width = 12, height = 6, dpi = 300, bg = "white")
cat("Saved v3med_smdef_pathA_coefs.png\n")

# =============================================================================
# PLOT 4: SM TAILS SMOKING GUN (from Path D Spec 4)
# =============================================================================
tails <- pd %>%
  filter(spec == "S4_tails", term %in% c("sm_q1", "sm_q4")) %>%
  mutate(
    label = ifelse(term == "sm_q1", "Dry tail\n1[SM < grid P25]", "Wet tail\n1[SM > grid P75]"),
    sig = sig_star(p),
    lo = b - 1.96*se, hi = b + 1.96*se
  )

p4 <- ggplot(tails, aes(x = label, y = b, fill = sig)) +
  geom_hline(yintercept = 0, color = "grey40", linetype = "dashed") +
  geom_col(width = 0.55) +
  geom_errorbar(aes(ymin = lo, ymax = hi), width = 0.2, color = "black") +
  geom_text(aes(label = sprintf("%.4f%s", b, sig)), vjust = -0.5, size = 4) +
  scale_fill_manual(values = sig_colors, name = "Significance") +
  labs(
    title = "Smoking gun: within-grid SM signal is dominated by wet tail (GLEAM-Sfc)",
    subtitle = "Dry tail has NO yield effect; wet tail strongly hurts yield (waterlogging confound)",
    x = NULL,
    y = "Coefficient on lnY"
  ) +
  theme_med

ggsave(file.path(figdir, "v3med_smdef_smoking_gun_tails.png"),
       plot = p4, width = 9, height = 5, dpi = 300, bg = "white")
cat("Saved v3med_smdef_smoking_gun_tails.png\n")

# =============================================================================
# PLOT 5: BOOTSTRAP CIS (if bootstrap file exists)
# =============================================================================
boot_path <- file.path(outdir, "v3med_smdef_bootstrap.csv")
if (file.exists(boot_path)) {
  bt <- read_csv(boot_path, show_col_types = FALSE) %>%
    mutate(
      sm_label = case_when(
        source == "gleam_sms_mean" ~ "GLEAM-Sfc",
        source == "gleam_smrz_mean" ~ "GLEAM-Root",
        TRUE ~ source
      ),
      estimand_label = case_when(
        estimand == "a1" ~ "a1 (D->SMdef)",
        estimand == "a3" ~ "a3 (SR*D->SMdef)",
        estimand == "b"  ~ "b  (SMdef->Y)",
        estimand == "idx"~ "Index = a3*b",
        estimand == "ie50" ~ "IE at ca_P50",
        estimand == "de50" ~ "DE at ca_P50",
        estimand == "te50" ~ "TE at ca_P50",
        estimand == "ie25" ~ "IE at ca_P25",
        estimand == "ie75" ~ "IE at ca_P75",
        estimand == "de25" ~ "DE at ca_P25",
        estimand == "de75" ~ "DE at ca_P75",
        estimand == "te25" ~ "TE at ca_P25",
        estimand == "te75" ~ "TE at ca_P75",
        TRUE ~ estimand
      )
    ) %>%
    filter(estimand %in% c("a1","a3","b","idx","ie25","ie50","ie75","de25","de50","de75","te25","te50","te75"))

  # Panel A: path coefs
  btA <- bt %>% filter(estimand %in% c("a1","a3","b","idx")) %>%
    mutate(est_order = factor(estimand_label,
      levels = c("a1 (D->SMdef)","a3 (SR*D->SMdef)","b  (SMdef->Y)","Index = a3*b")))
  # Panel B: conditional effects
  btB <- bt %>% filter(grepl("^(IE|DE|TE)", estimand_label)) %>%
    mutate(effect_type = str_extract(estimand_label, "^(IE|DE|TE)"),
           ca_lvl = str_extract(estimand_label, "P\\d{2}"))

  pa <- ggplot(btA, aes(x = point, y = est_order, color = sm_label)) +
    geom_vline(xintercept = 0, color = "grey40", linetype = "dashed") +
    geom_pointrange(aes(xmin = ll95, xmax = ul95),
                    position = position_dodge(width = 0.4),
                    size = 0.7, linewidth = 0.8) +
    scale_color_manual(values = c("GLEAM-Sfc" = "#2E7D32", "GLEAM-Root" = "#66BB6A"),
                       name = "SM source") +
    labs(title = "Bootstrap 95% BC CIs: SMdef mediation coefficients (500 reps)",
         subtitle = "b CI above 0 -> wrong direction for mediation; Index CI near 0 -> mediation not identified",
         x = "Point estimate (95% BC CI)", y = NULL) +
    theme_med

  pb <- ggplot(btB, aes(x = point, y = ca_lvl, color = effect_type)) +
    geom_vline(xintercept = 0, color = "grey40", linetype = "dashed") +
    geom_pointrange(aes(xmin = ll95, xmax = ul95),
                    position = position_dodge(width = 0.4),
                    size = 0.5, linewidth = 0.7) +
    facet_wrap(~ sm_label) +
    scale_color_manual(values = c("IE" = "#D95F0E", "DE" = "#2C7FB8", "TE" = "#238443"),
                       name = "Effect") +
    labs(title = "Conditional effects at ca P25/P50/P75 (SMdef bootstrap)",
         subtitle = "DE (direct) robust & positive; IE (indirect) ambiguous",
         x = "Conditional effect (95% BC CI)", y = "ca percentile") +
    theme_med

  combined <- pa / pb + plot_layout(heights = c(1, 1.2))
  ggsave(file.path(figdir, "v3med_smdef_bootstrap_ci.png"),
         plot = combined, width = 12, height = 9, dpi = 300, bg = "white")
  cat("Saved v3med_smdef_bootstrap_ci.png\n")
} else {
  cat("Bootstrap CSV not found at", boot_path, "- skipping Plot 5\n")
}

cat("\n=== v3med_smdef_plots.R COMPLETE ===\n")
