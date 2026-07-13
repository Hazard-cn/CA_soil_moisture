# v3bpath_figures.R
# Purpose: Generate figures for v3bpath b-path audit beamer report
# Reads: temp/v3bpath_*.csv
# Writes: output/figures/v3bpath_*.png
# Date: 2026-04-21

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(readr)
  library(tidyr)
  library(scales)
  library(patchwork)
  library(stringr)
})

set.seed(42)

proj    <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
tmp_dir <- file.path(proj, "temp")
fig_dir <- file.path(proj, "output/figures")
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

# ---- Theme & palette ----------------------------------------------------
theme_bpath <- function(base_size = 11) {
  theme_minimal(base_size = base_size, base_family = "sans") +
    theme(
      panel.background = element_rect(fill = "white", colour = NA),
      plot.background  = element_rect(fill = "white", colour = NA),
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(colour = "grey90"),
      strip.background = element_rect(fill = "grey95", colour = NA),
      strip.text       = element_text(face = "bold"),
      plot.title       = element_text(face = "bold", size = base_size + 1),
      plot.subtitle    = element_text(colour = "grey30", size = base_size - 1),
      legend.position  = "bottom"
    )
}

sign_cols <- c("neg_sig"  = "#CB181D",
               "neg_ns"   = "#FDBB84",
               "pos_ns"   = "#A1D99B",
               "pos_sig"  = "#238B45")

sign_label <- function(b, p, alpha = 0.05) {
  dplyr::case_when(
    b < 0 & p <  alpha ~ "neg_sig",
    b < 0 & p >= alpha ~ "neg_ns",
    b >= 0 & p <  alpha ~ "pos_sig",
    TRUE ~ "pos_ns"
  )
}

sig_stars <- function(p) {
  dplyr::case_when(
    p < 0.01 ~ "***",
    p < 0.05 ~ "**",
    p < 0.10 ~ "*",
    TRUE ~ ""
  )
}

src_order <- c("GLEAM-Sfc", "GLEAM-Root", "ERA5L-L1", "ERA5L-L3", "SWSM-L1", "SWSM-L3")

# Window label ordering (biological time ordering: pre-season -> during -> post)
win_order <- c("v3pre30", "v3pm10", "v3he", "hepm10", "hema", "full")
win_pretty <- c(v3pre30 = "pre-30d",
                v3pm10  = "peri-stage ±10d",
                v3he    = "heading",
                hepm10  = "heading-early ±10d",
                hema    = "heading-mature",
                full    = "full-season")

save_fig <- function(p, name, w = 10, h = 5) {
  fp <- file.path(fig_dir, paste0("v3bpath_", name, ".png"))
  ggsave(fp, plot = p, width = w, height = h, dpi = 300, bg = "white")
  message("saved: ", fp)
}

# =========================================================================
# 0. Diagnostics: SMdef positive-fraction bar
# =========================================================================
diag <- read_csv(file.path(tmp_dir, "v3bpath_diagnostics.csv"), show_col_types = FALSE)

smdef_pos <- diag %>%
  filter(str_detect(item, "^N_smdef_positive_")) %>%
  mutate(sm_var = str_remove(item, "^N_smdef_positive_"),
         n_pos  = as.numeric(value))

smdef_mean <- diag %>%
  filter(str_detect(item, "^mean_smdef_")) %>%
  mutate(sm_var = str_remove(item, "^mean_smdef_"),
         mean_smdef = as.numeric(value))

smdef_sd <- diag %>%
  filter(str_detect(item, "^sd_smdef_")) %>%
  mutate(sm_var = str_remove(item, "^sd_smdef_"),
         sd_smdef = as.numeric(value))

label_map <- c(
  gleam_sms_mean   = "GLEAM-Sfc",
  gleam_smrz_mean  = "GLEAM-Root",
  era5l_swvl1_mean = "ERA5L-L1",
  era5l_swvl3_mean = "ERA5L-L3",
  swsm_l1_mean     = "SWSM-L1",
  swsm_l3_mean     = "SWSM-L3"
)

smdef <- smdef_pos %>%
  left_join(smdef_mean, by = "sm_var") %>%
  left_join(smdef_sd, by = "sm_var") %>%
  mutate(sm_label = label_map[sm_var],
         sm_label = factor(sm_label, levels = src_order),
         share_pos = n_pos / 61887)

p_diag <- ggplot(smdef, aes(x = sm_label, y = share_pos, fill = sm_label)) +
  geom_col(width = 0.7, alpha = 0.85) +
  geom_text(aes(label = scales::percent(share_pos, accuracy = 0.1)),
            vjust = -0.4, size = 3.3) +
  scale_y_continuous(labels = percent, limits = c(0, 0.6)) +
  scale_fill_brewer(palette = "Set2", guide = "none") +
  labs(title = "SMdef 正值占比：6 个 source-layer 分布",
       subtitle = "分母 = bpath_full6_sample (N = 61,887)；均值/SD 见附注",
       x = NULL, y = "Share SMdef > 0") +
  theme_bpath()

save_fig(p_diag, "diag_smdef", w = 9, h = 4.5)

# =========================================================================
# 1. Timing audit: heatmap + full vs v3pre30 bar
# =========================================================================
tm <- read_csv(file.path(tmp_dir, "v3bpath_timing_audit.csv"), show_col_types = FALSE)

tm <- tm %>%
  mutate(sm_label = factor(sm_label, levels = src_order),
         window   = factor(window, levels = win_order),
         window_pretty = factor(win_pretty[as.character(window)],
                                levels = win_pretty[win_order]),
         sign_cat = sign_label(b_sm, p_sm),
         stars    = sig_stars(p_sm),
         b_text   = sprintf("%.2f%s", b_sm, stars))

p_tm_heat <- ggplot(tm, aes(x = window_pretty, y = sm_label, fill = sign_cat)) +
  geom_tile(colour = "white", linewidth = 0.6) +
  geom_text(aes(label = b_text), size = 3.1) +
  scale_fill_manual(values = sign_cols,
                    breaks = c("neg_sig", "neg_ns", "pos_ns", "pos_sig"),
                    labels = c("负·显著", "负·不显著", "正·不显著", "正·显著"),
                    name = NULL) +
  labs(title = "Timing audit: b(SM) 在 6 源 × 6 窗口下的符号",
       subtitle = "所有单元格共同样本 N = 61,900；stars: * p<.10, ** p<.05, *** p<.01",
       x = NULL, y = NULL) +
  theme_bpath() +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

save_fig(p_tm_heat, "timing_heatmap", w = 10, h = 4.8)

# Bar: full vs v3pre30
tm_bar <- tm %>%
  filter(window %in% c("full", "v3pre30")) %>%
  mutate(win_lab = recode(as.character(window),
                          full = "full-season", v3pre30 = "pre-30d"))

p_tm_bar <- ggplot(tm_bar, aes(x = sm_label, y = b_sm, fill = win_lab)) +
  geom_col(position = position_dodge(width = 0.75), width = 0.7, alpha = 0.85) +
  geom_errorbar(aes(ymin = b_sm - 1.96 * se_sm, ymax = b_sm + 1.96 * se_sm),
                position = position_dodge(width = 0.75), width = 0.2) +
  geom_hline(yintercept = 0, colour = "grey30") +
  scale_fill_manual(values = c("full-season" = "#CB181D", "pre-30d" = "#238B45"),
                    name = NULL) +
  labs(title = "Timing 改善：full-season 全部负号 vs pre-30d 部分翻正",
       subtitle = "误差棒 = ±1.96·SE；pre-30d 仍有 2/6 保持负号",
       x = NULL, y = "b(SM)") +
  theme_bpath() +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

save_fig(p_tm_bar, "timing_full_vs_pre", w = 10, h = 4.5)

# =========================================================================
# 2. Control ladder
# =========================================================================
cl <- read_csv(file.path(tmp_dir, "v3bpath_control_ladder.csv"), show_col_types = FALSE)

cl <- cl %>%
  mutate(sm_label = factor(sm_label, levels = src_order),
         ladder   = factor(ladder, levels = c("L0", "L1", "L2", "L3")))

p_cl_b <- ggplot(cl, aes(x = ladder, y = b_sm, group = sm_label, colour = sm_label)) +
  geom_ribbon(aes(ymin = b_sm - 1.96 * se_b_sm, ymax = b_sm + 1.96 * se_b_sm,
                  fill = sm_label), alpha = 0.10, colour = NA) +
  geom_line(linewidth = 0.9) +
  geom_point(size = 2.5) +
  geom_hline(yintercept = 0, colour = "black", linetype = "dashed") +
  scale_colour_brewer(palette = "Dark2", name = NULL) +
  scale_fill_brewer(palette = "Dark2", guide = "none") +
  labs(title = "Control ladder: b(SM) 从 L0 到 L3 的演变",
       subtitle = "L0 = irr+GDD+W_full；L1 +pr；L2 +et0；L3 +aridity。阴影 = 95%CI",
       x = NULL, y = "b(SM)") +
  theme_bpath()

save_fig(p_cl_b, "ladder_b", w = 10, h = 4.8)

# c3 across ladder
p_cl_c3 <- ggplot(cl, aes(x = ladder, y = c3, group = sm_label, colour = sm_label)) +
  geom_ribbon(aes(ymin = c3 - 1.96 * se_c3, ymax = c3 + 1.96 * se_c3,
                  fill = sm_label), alpha = 0.10, colour = NA) +
  geom_line(linewidth = 0.9) +
  geom_point(size = 2.5) +
  geom_hline(yintercept = 0, colour = "black", linetype = "dashed") +
  scale_colour_brewer(palette = "Dark2", name = NULL) +
  scale_fill_brewer(palette = "Dark2", guide = "none") +
  labs(title = "Control ladder: c3 (SR × D direct buffering)",
       subtitle = "6 源 × L0→L3 均保持正号（阴影 = 95%CI）",
       x = NULL, y = "c3 = coef(SR × D)") +
  theme_bpath()

save_fig(p_cl_c3, "ladder_c3", w = 10, h = 4.8)

# =========================================================================
# 3. Wet control audit
# =========================================================================
wc <- read_csv(file.path(tmp_dir, "v3bpath_wet_control_audit.csv"), show_col_types = FALSE)

wc <- wc %>%
  mutate(sm_label = factor(sm_label, levels = src_order),
         spec     = factor(spec, levels = c("N0", "N1", "N2")))

# delta_b N0 -> N1 per source
wc_delta <- wc %>%
  filter(spec %in% c("N0", "N1")) %>%
  select(source, layer, sm_label, spec, b_sm) %>%
  pivot_wider(names_from = spec, values_from = b_sm) %>%
  mutate(wet_delta_b = N1 - N0)

p_wc_delta <- ggplot(wc_delta, aes(x = sm_label, y = wet_delta_b, fill = sm_label)) +
  geom_col(width = 0.7, alpha = 0.85) +
  geom_text(aes(label = sprintf("%+.2f", wet_delta_b)), vjust = -0.3, size = 3.2) +
  geom_hline(yintercept = 0, colour = "grey30") +
  scale_fill_brewer(palette = "Set2", guide = "none") +
  labs(title = "Wet control 吸收负 b：N1 - N0 的 Δb 全部 > 0",
       subtitle = "Δb = b(SM|N1) - b(SM|N0)；N1 加入 W_full 后负 b 被削弱",
       x = NULL, y = "Δ b(SM) = N1 - N0") +
  theme_bpath() +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

save_fig(p_wc_delta, "wet_delta", w = 9, h = 4.5)

# N2 spec: SMdef sign
wc_n2 <- wc %>%
  filter(spec == "N2") %>%
  mutate(sign_cat = sign_label(b_sm, p_b_sm),
         stars    = sig_stars(p_b_sm),
         b_text   = sprintf("%.2f%s", b_sm, stars))

p_wc_n2 <- ggplot(wc_n2, aes(x = sm_label, y = b_sm, fill = sign_cat)) +
  geom_col(width = 0.7, alpha = 0.85) +
  geom_errorbar(aes(ymin = b_sm - 1.96 * se_b_sm, ymax = b_sm + 1.96 * se_b_sm),
                width = 0.2) +
  geom_text(aes(label = b_text, y = b_sm + ifelse(b_sm >= 0, 1.96 * se_b_sm + 0.05,
                                                  -1.96 * se_b_sm - 0.05)),
            size = 3.2) +
  geom_hline(yintercept = 0, colour = "grey30") +
  scale_fill_manual(values = sign_cols,
                    breaks = c("neg_sig", "neg_ns", "pos_ns", "pos_sig"),
                    labels = c("负·显著", "负·不显著", "正·不显著", "正·显著"),
                    name = NULL) +
  labs(title = "Wet audit N2: 改写成 SMdef 后的 b 符号",
       subtitle = "5/6 转正但仅 1/6 达到显著",
       x = NULL, y = "b(SMdef)") +
  theme_bpath() +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

save_fig(p_wc_n2, "wet_n2_smdef", w = 9, h = 4.5)

# =========================================================================
# 4. Nonlinear audit
# =========================================================================
nl <- read_csv(file.path(tmp_dir, "v3bpath_nonlinear_audit.csv"), show_col_types = FALSE)

nl <- nl %>%
  mutate(sm_label = factor(sm_label, levels = src_order),
         spec     = factor(spec, levels = c("baseline", "quadratic", "tails")))

# Linear and quadratic sm_linear panel
p_nl_lin <- ggplot(nl, aes(x = sm_label, y = sm_linear, fill = spec)) +
  geom_col(position = position_dodge(width = 0.75), width = 0.7, alpha = 0.85) +
  geom_errorbar(aes(ymin = sm_linear - 1.96 * se_sm_linear,
                    ymax = sm_linear + 1.96 * se_sm_linear),
                position = position_dodge(width = 0.75), width = 0.2) +
  geom_hline(yintercept = 0, colour = "grey30") +
  scale_fill_brewer(palette = "Set1", name = NULL) +
  labs(title = "Nonlinear audit: baseline / quadratic / tails 的 linear SM 系数",
       subtitle = "三种规格下 linear 项均维持负号",
       x = NULL, y = "linear SM coef") +
  theme_bpath() +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

save_fig(p_nl_lin, "nonlinear_linear", w = 10, h = 4.8)

# Turning point in support tile
nl_quad <- nl %>%
  filter(spec == "quadratic") %>%
  mutate(in_support = factor(ifelse(turning_in_support == 1, "在支持内", "不在支持内"),
                             levels = c("在支持内", "不在支持内")),
         tp_text = sprintf("tp=%.2f", turning_point))

p_nl_tp <- ggplot(nl_quad, aes(x = sm_label, y = "quadratic", fill = in_support)) +
  geom_tile(colour = "white", linewidth = 0.6) +
  geom_text(aes(label = tp_text), size = 3.2) +
  scale_fill_manual(values = c("在支持内" = "#238B45", "不在支持内" = "#BDBDBD"),
                    name = NULL) +
  labs(title = "Quadratic turning point 是否落在样本支持区间",
       subtitle = "4/6 在支持内 → 非线性存在，但单独无法修复 b 方向",
       x = NULL, y = NULL) +
  theme_bpath() +
  theme(axis.text.y = element_blank())

save_fig(p_nl_tp, "nonlinear_turning", w = 10, h = 2.8)

# =========================================================================
# 5. Proxy competition
# =========================================================================
pc <- read_csv(file.path(tmp_dir, "v3bpath_proxy_competition.csv"), show_col_types = FALSE)

pc_r <- pc %>%
  filter(control_version == "reduced") %>%
  mutate(sm_label = factor(sm_label, levels = src_order))

pc_long <- pc_r %>%
  transmute(sm_label,
            `SetA: SR × D`        = setA_dca,
            `SetB: SR × DrySM`    = setB_dryxca,
            `Compete: SR × DrySM` = compete_sm_dryxca,
            `Compete: SR × D`     = compete_d_dca,
            se_SetA  = setA_dca_se,
            se_SetB  = setB_dryxca_se,
            se_CompSM = compete_sm_dryxca_se,
            se_CompD  = compete_d_dca_se,
            p_SetA   = setA_dca_p,
            p_SetB   = setB_dryxca_p,
            p_CompSM = compete_sm_dryxca_p,
            p_CompD  = compete_d_dca_p) %>%
  pivot_longer(
    cols = -sm_label,
    names_to = c(".value", "spec"),
    names_pattern = "^(.*?)_?(SetA|SetB|CompSM|CompD)$"
  ) %>%
  rename(coef = 2)

# simpler: manually build
pc_long <- bind_rows(
  pc_r %>% transmute(sm_label, spec = "SetA: SR × D",
                     coef = setA_dca, se = setA_dca_se, p = setA_dca_p),
  pc_r %>% transmute(sm_label, spec = "SetB: SR × DrySM",
                     coef = setB_dryxca, se = setB_dryxca_se, p = setB_dryxca_p),
  pc_r %>% transmute(sm_label, spec = "Compete: SR × D",
                     coef = compete_d_dca, se = compete_d_dca_se, p = compete_d_dca_p),
  pc_r %>% transmute(sm_label, spec = "Compete: SR × DrySM",
                     coef = compete_sm_dryxca, se = compete_sm_dryxca_se, p = compete_sm_dryxca_p)
) %>%
  mutate(spec = factor(spec, levels = c("SetA: SR × D", "SetB: SR × DrySM",
                                        "Compete: SR × D", "Compete: SR × DrySM")),
         sig  = p < 0.05)

p_pc <- ggplot(pc_long, aes(x = coef, y = sm_label, colour = spec)) +
  geom_vline(xintercept = 0, colour = "grey30", linetype = "dashed") +
  geom_errorbarh(aes(xmin = coef - 1.96 * se, xmax = coef + 1.96 * se),
                 height = 0, linewidth = 0.6,
                 position = position_dodge(width = 0.7)) +
  geom_point(aes(shape = sig), size = 2.6,
             position = position_dodge(width = 0.7)) +
  scale_colour_brewer(palette = "Set1", name = NULL) +
  scale_shape_manual(values = c(`TRUE` = 16, `FALSE` = 1),
                     labels = c(`TRUE` = "p < .05", `FALSE` = "n.s."),
                     name = NULL) +
  labs(title = "Proxy competition (reduced controls)",
       subtitle = "SetA/SetB 独立跑；Compete 把 SPEI 与 DrySM 同时放入同一回归",
       x = "Coefficient", y = NULL) +
  theme_bpath()

save_fig(p_pc, "proxy_competition", w = 10, h = 5)

# =========================================================================
# 6. Source-depth audit: a3 / b / c3 panels
# =========================================================================
sd <- read_csv(file.path(tmp_dir, "v3bpath_source_depth_audit.csv"), show_col_types = FALSE)

sd_r <- sd %>%
  filter(control_version == "reduced") %>%
  mutate(sm_label = factor(sm_label, levels = src_order))

mk_panel <- function(df, varname, se_name, p_name, title) {
  df %>%
    mutate(coef = .data[[varname]],
           se   = .data[[se_name]],
           p    = .data[[p_name]],
           sign_cat = sign_label(coef, p),
           stars    = sig_stars(p)) %>%
    ggplot(aes(x = sm_label, y = coef, fill = sign_cat)) +
    geom_col(width = 0.7, alpha = 0.85) +
    geom_errorbar(aes(ymin = coef - 1.96 * se, ymax = coef + 1.96 * se),
                  width = 0.2) +
    geom_hline(yintercept = 0, colour = "grey30") +
    scale_fill_manual(values = sign_cols,
                      breaks = c("neg_sig", "neg_ns", "pos_ns", "pos_sig"),
                      labels = c("负·显著", "负·不显著", "正·不显著", "正·显著"),
                      name = NULL) +
    labs(title = title, x = NULL, y = NULL) +
    theme_bpath() +
    theme(axis.text.x = element_text(angle = 18, hjust = 1))
}

p_a3 <- mk_panel(sd_r, "a3", "se_a3", "p_a3",
                 "a3: D × SR → SM (mediator eq.)")
p_b  <- mk_panel(sd_r, "b_sm", "se_b_sm", "p_b_sm",
                 "b: SM → Y (outcome eq.)")
p_c3 <- mk_panel(sd_r, "c3", "se_c3", "p_c3",
                 "c3: D × SR → Y (outcome eq.)")

p_sd <- (p_a3 | p_b | p_c3) +
  plot_layout(guides = "collect") +
  plot_annotation(title = "Source-depth audit (reduced controls): a3 / b / c3 对比",
                  subtitle = "a3 对源高度敏感；b 在 6/6 上保持负号；c3 在 6/6 上保持正号",
                  theme = theme(plot.title = element_text(face = "bold"))) &
  theme(legend.position = "bottom")

save_fig(p_sd, "source_depth", w = 13, h = 5)

# =========================================================================
# 7. Heat consistency
# =========================================================================
hc <- read_csv(file.path(tmp_dir, "v3bpath_heat_consistency.csv"), show_col_types = FALSE)

hc <- hc %>%
  mutate(sm_label = factor(sm_label, levels = src_order),
         bg       = factor(background_role, levels = c("rawSM_bg", "DrySM_bg")),
         ctrl     = factor(control_version, levels = c("reduced", "full")),
         group    = interaction(bg, ctrl, sep = " | "),
         sig      = p_hxca < 0.05)

p_hc <- ggplot(hc, aes(x = b_hxca, y = sm_label, colour = group)) +
  geom_vline(xintercept = 0, colour = "grey30", linetype = "dashed") +
  geom_errorbarh(aes(xmin = b_hxca - 1.96 * se_hxca, xmax = b_hxca + 1.96 * se_hxca),
                 height = 0,
                 position = position_dodge(width = 0.7)) +
  geom_point(size = 2.6,
             position = position_dodge(width = 0.7)) +
  scale_colour_brewer(palette = "Set1", name = NULL) +
  labs(title = "Heat consistency: SR × Heat 在 6 源 × bg × controls 下",
       subtitle = "24 条估计全部为正，集中在 0.0010-0.0013；heat-side 稳定",
       x = "SR × Heat", y = NULL) +
  theme_bpath()

save_fig(p_hc, "heat_consistency", w = 10, h = 5)

# =========================================================================
# 8. Sensitivity claim audit: 30 tile
# =========================================================================
sc <- read_csv(file.path(tmp_dir, "v3bpath_sensitivity_claim_audit.csv"), show_col_types = FALSE)

spec_order <- c("raw_full_L0", "raw_full_provyear",
                "smdef_full_L0", "smdef_full_provyear",
                "stage_v3pre30_L0")

sc <- sc %>%
  mutate(sm_label = factor(sm_label, levels = src_order),
         spec     = factor(spec, levels = spec_order),
         index_text = sprintf("%.3f", index_ab))

p_sc <- ggplot(sc, aes(x = spec, y = sm_label, fill = claim_level)) +
  geom_tile(colour = "white", linewidth = 0.6) +
  geom_text(aes(label = index_text), size = 3.0) +
  scale_fill_manual(values = c(not_mediation = "#EF3B2C", mediation = "#238B45"),
                    name = NULL) +
  labs(title = "Sensitivity claim audit: 30 个规格下的 claim_level",
       subtitle = "全部 30/30 = not_mediation；单元格数字 = index_ab (= a3 × b)",
       x = NULL, y = NULL) +
  theme_bpath() +
  theme(axis.text.x = element_text(angle = 16, hjust = 1))

save_fig(p_sc, "claim_audit", w = 10, h = 4.8)

# =========================================================================
# 9. SM comparison summary: tile with normalized metrics
# =========================================================================
ss <- read_csv(file.path(tmp_dir, "v3bpath_sm_comparison_summary.csv"), show_col_types = FALSE)

ss <- ss %>%
  mutate(sm_label = paste(toupper(source), layer, sep = "-"),
         sm_label = case_when(
           source == "gleam" & layer == "surface"  ~ "GLEAM-Sfc",
           source == "gleam" & layer == "rootzone" ~ "GLEAM-Root",
           source == "era"   & layer == "surface"  ~ "ERA5L-L1",
           source == "era"   & layer == "rootzone" ~ "ERA5L-L3",
           source == "swsm"  & layer == "surface"  ~ "SWSM-L1",
           source == "swsm"  & layer == "rootzone" ~ "SWSM-L3"
         ),
         sm_label = factor(sm_label, levels = src_order))

# Long format of key metrics
ss_long <- ss %>%
  transmute(sm_label,
            `b (full)`          = timing_full_b,
            `b (pre-30d)`       = timing_v3pre30_b,
            `b @ L0`            = ladder_L0_b,
            `b (SMdef)`         = smdef_b,
            `b (source reduced)` = source_b_reduced,
            `SR × Heat`         = heat_Hxca_raw) %>%
  pivot_longer(-sm_label, names_to = "metric", values_to = "value") %>%
  mutate(metric = factor(metric, levels = c("b (full)", "b (pre-30d)", "b @ L0",
                                             "b (SMdef)", "b (source reduced)",
                                             "SR × Heat")),
         sign  = ifelse(value >= 0, "pos", "neg"),
         label = ifelse(abs(value) < 0.01,
                        sprintf("%.4f", value),
                        sprintf("%.2f", value)))

p_ss <- ggplot(ss_long, aes(x = metric, y = sm_label, fill = sign)) +
  geom_tile(colour = "white", linewidth = 0.6) +
  geom_text(aes(label = label), size = 3.0) +
  scale_fill_manual(values = c(neg = "#FC9272", pos = "#A1D99B"),
                    labels = c(neg = "负", pos = "正"),
                    name = NULL) +
  labs(title = "跨 SM 数据源比较一览：6 源-layer × 6 个关键指标",
       subtitle = "SR × Heat 全部正号（heat 侧稳健）；b(full)/b@L0 全部负（b-path 异常跨源）",
       x = NULL, y = NULL) +
  theme_bpath() +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

save_fig(p_ss, "sm_comparison", w = 10, h = 4.8)

# =========================================================================
# 10. Overview cover figure — b(SM) across all windows (bar grid)
# =========================================================================
p_overview <- ggplot(tm, aes(x = window_pretty, y = b_sm, fill = sign_cat)) +
  geom_col(width = 0.8, alpha = 0.85) +
  geom_hline(yintercept = 0, colour = "grey30") +
  facet_wrap(~ sm_label, ncol = 3, scales = "free_y") +
  scale_fill_manual(values = sign_cols,
                    breaks = c("neg_sig", "neg_ns", "pos_ns", "pos_sig"),
                    labels = c("负·显著", "负·不显著", "正·不显著", "正·显著"),
                    name = NULL) +
  labs(title = "b(SM) 跨 6 源 × 6 窗口全景",
       subtitle = "full-season 6/6 为负；pre-30d 部分翻正；stage 窗口符号分裂",
       x = NULL, y = "b(SM)") +
  theme_bpath() +
  theme(axis.text.x = element_text(angle = 30, hjust = 1, size = 8))

save_fig(p_overview, "overview_bsm_grid", w = 12, h = 6.2)

message("\n--- all v3bpath figures generated ---")
