# sm_state_audit_figures.R
# Purpose: Generate figures for 2026-04-21 SM state audit beamer report
# Reads: temp/2026-04-21_sm_state_audit/*.csv
# Writes: output/figures/sm_state_*.png
# Date: 2026-04-21

suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(readr)
  library(tidyr); library(scales); library(patchwork); library(stringr)
})

set.seed(42)

proj    <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
src_dir <- file.path(proj, "temp/2026-04-21_sm_state_audit")
fig_dir <- file.path(proj, "output/figures")
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

# ---- Theme --------------------------------------------------------------
theme_sm <- function(base_size = 11) {
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

sign_cols <- c("neg_sig" = "#CB181D", "neg_ns" = "#FDBB84",
               "pos_ns"  = "#A1D99B", "pos_sig" = "#238B45")

sign_label <- function(b, p, alpha = 0.05) {
  dplyr::case_when(
    is.na(b) | is.na(p) ~ NA_character_,
    b <  0 & p <  alpha ~ "neg_sig",
    b <  0 & p >= alpha ~ "neg_ns",
    b >= 0 & p <  alpha ~ "pos_sig",
    TRUE ~ "pos_ns"
  )
}

sig_stars <- function(p) {
  dplyr::case_when(
    is.na(p) ~ "",
    p < 0.01 ~ "***",
    p < 0.05 ~ "**",
    p < 0.10 ~ "*",
    TRUE ~ ""
  )
}

src_order  <- c("GLEAM-Sfc", "GLEAM-Root", "ERA5L-L1", "ERA5L-L3", "SWSM-L1", "SWSM-L3")
win_order  <- c("full", "v3pre30", "v3pm10")
win_pretty <- c(full = "full-season", v3pre30 = "pre-30d", v3pm10 = "peri-stage ±10d")
scheme_order <- c("maize_zone", "pooled")

save_fig <- function(p, name, w = 10, h = 5) {
  fp <- file.path(fig_dir, paste0("sm_state_", name, ".png"))
  ggsave(fp, plot = p, width = w, height = h, dpi = 300, bg = "white")
  message("saved: ", fp)
}

# =========================================================================
# 1. Wet-leaning summary: raw_corr_w heatmap + flag tile
# =========================================================================
wl <- read_csv(file.path(src_dir, "sm_state_wet_leaning_summary.csv"),
               show_col_types = FALSE)

wl <- wl %>%
  mutate(sm_label = factor(sm_label, levels = src_order),
         window   = factor(window, levels = win_order),
         window_pretty = factor(win_pretty[as.character(window)],
                                levels = win_pretty[win_order]),
         threshold_scheme = factor(threshold_scheme, levels = scheme_order))

# Corr heatmap (raw_corr_w is same across schemes; take unique)
wl_corr <- wl %>%
  filter(threshold_scheme == "maize_zone") %>%
  mutate(corr_label = sprintf("%.3f", raw_corr_w))

p_corr <- ggplot(wl_corr, aes(x = window_pretty, y = sm_label, fill = raw_corr_w)) +
  geom_tile(colour = "white", linewidth = 0.6) +
  geom_text(aes(label = corr_label), size = 3.3) +
  scale_fill_gradient2(low = "#CB181D", mid = "white", high = "#238B45",
                       midpoint = 0, limits = c(-0.3, 0.3),
                       name = "corr(SM, W)") +
  labs(title = "raw SM 与 wetness benchmark (W) 的相关系数",
       subtitle = "6 source-layer × 3 window；18/18 全部为正 → SM 与 W 方向一致",
       x = NULL, y = NULL) +
  theme_sm()

save_fig(p_corr, "corr_sm_w", w = 9, h = 5)

# wet_leaning_flag tile
p_flag <- ggplot(wl, aes(x = window_pretty, y = sm_label,
                         fill = factor(wet_leaning_flag))) +
  facet_wrap(~ threshold_scheme, labeller = as_labeller(
    c(maize_zone = "maize_zone 阈值", pooled = "pooled 阈值"))) +
  geom_tile(colour = "white", linewidth = 0.6) +
  geom_text(aes(label = ifelse(criteria_flag == 1, "✓", "·")), size = 4) +
  scale_fill_manual(values = c(`0` = "#FDBB84", `1` = "#238B45"),
                    labels = c(`0` = "未达湿偏门槛",
                               `1` = "达到湿偏门槛"),
                    name = NULL) +
  labs(title = "Wet-leaning 判定：窗口 × 源 × 阈值 (18 × 2 = 36 组合)",
       subtitle = "单元格 ✓ = criteria_flag=1；颜色 = wet_leaning_flag (窗口级聚合门槛)",
       x = NULL, y = NULL) +
  theme_sm()

save_fig(p_flag, "wet_flag", w = 11, h = 5)

# =========================================================================
# 2. Descriptive: mean(WetShare - DryShare) per window × source × scheme
# =========================================================================
dsc <- read_csv(file.path(src_dir, "sm_state_descriptives.csv"),
                show_col_types = FALSE)

dsc <- dsc %>%
  mutate(sm_label = factor(sm_label, levels = src_order),
         window   = factor(window, levels = win_order),
         window_pretty = factor(win_pretty[as.character(window)],
                                levels = win_pretty[win_order]),
         threshold_scheme = factor(threshold_scheme, levels = scheme_order))

p_dsc <- ggplot(dsc, aes(x = sm_label, y = mean_wet_minus_dry,
                         fill = threshold_scheme)) +
  geom_col(position = position_dodge(width = 0.75), width = 0.7, alpha = 0.85) +
  facet_wrap(~ window_pretty, ncol = 3) +
  geom_hline(yintercept = 0, colour = "grey30") +
  scale_fill_manual(values = c(maize_zone = "#2171B5", pooled = "#E6550D"),
                    name = NULL) +
  labs(title = "Descriptive: mean(WetShare - DryShare) 全部为负",
       subtitle = "所有 18 (6源) × 3 窗 × 2 阈值 组合都 < 0 → 样本整体 dry-side 略大于 wet-side",
       x = NULL, y = "mean(WetShare - DryShare)") +
  theme_sm() +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

save_fig(p_dsc, "wet_minus_dry", w = 11.5, h = 5)

# =========================================================================
# 3. Share of grids with WetShare > DryShare per source-layer × window
# =========================================================================
p_share <- ggplot(dsc, aes(x = sm_label, y = share_wet_gt_dry,
                           fill = threshold_scheme)) +
  geom_col(position = position_dodge(width = 0.75), width = 0.7, alpha = 0.85) +
  facet_wrap(~ window_pretty, ncol = 3) +
  geom_hline(yintercept = 0.5, colour = "grey30", linetype = "dashed") +
  scale_fill_manual(values = c(maize_zone = "#2171B5", pooled = "#E6550D"),
                    name = NULL) +
  scale_y_continuous(labels = percent, limits = c(0, 1)) +
  labs(title = "格点层面 share(WetShare > DryShare)",
       subtitle = "多数单元格落在 50% 以下 → 更多格点呈现 dry-side 占优",
       x = NULL, y = "Share of grids with W > D") +
  theme_sm() +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

save_fig(p_share, "share_wet_gt_dry", w = 11.5, h = 5)

# =========================================================================
# 4. Main model comparison: b_main by window × scheme × spec × source
# =========================================================================
mm <- read_csv(file.path(src_dir, "sm_state_model_main.csv"),
               show_col_types = FALSE)
vp <- read_csv(file.path(src_dir, "sm_state_model_v3pm10.csv"),
               show_col_types = FALSE)
mm_all <- bind_rows(mm, vp)

mm_all <- mm_all %>%
  mutate(sm_label = factor(sm_label, levels = src_order),
         window   = factor(window, levels = win_order),
         window_pretty = factor(win_pretty[as.character(window)],
                                levels = win_pretty[win_order]),
         threshold_scheme = factor(threshold_scheme, levels = scheme_order),
         spec     = factor(spec, levels = c("Raw-Legacy", "Raw-StateCtrl", "State-Main")),
         sign_cat = sign_label(b_main, p_b_main),
         stars    = sig_stars(p_b_main))

# ---- 4a. Heatmap of b_main sign across every combination ----------------
p_b_heat <- mm_all %>%
  ggplot(aes(x = spec, y = sm_label, fill = sign_cat)) +
  geom_tile(colour = "white", linewidth = 0.6) +
  geom_text(aes(label = sprintf("%+.2f%s", b_main, stars)), size = 2.8) +
  facet_grid(threshold_scheme ~ window_pretty,
             labeller = labeller(
               threshold_scheme = c(maize_zone = "maize_zone",
                                    pooled     = "pooled"))) +
  scale_fill_manual(values = sign_cols,
                    breaks = c("neg_sig","neg_ns","pos_ns","pos_sig"),
                    labels = c("负·显著","负·不显著","正·不显著","正·显著"),
                    name = NULL) +
  labs(title = "b_main 在 3 规格 × 3 窗口 × 2 阈值下的符号与显著性",
       subtitle = "full 全面改善；v3pre30 阈值敏感；v3pm10 negative-control 也改善",
       x = NULL, y = NULL) +
  theme_sm() +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

save_fig(p_b_heat, "b_main_heatmap", w = 12, h = 6.4)

# ---- 4b. Paired bar: Raw-StateCtrl vs State-Main (main spec focus) ------
mm_pair <- mm_all %>%
  filter(spec %in% c("Raw-StateCtrl", "State-Main"))

p_pair <- ggplot(mm_pair, aes(x = sm_label, y = b_main, fill = spec)) +
  geom_col(position = position_dodge(width = 0.75), width = 0.7, alpha = 0.9) +
  geom_errorbar(aes(ymin = b_main - 1.96 * se_b_main,
                    ymax = b_main + 1.96 * se_b_main),
                position = position_dodge(width = 0.75), width = 0.2) +
  facet_grid(threshold_scheme ~ window_pretty,
             labeller = labeller(
               threshold_scheme = c(maize_zone = "maize_zone",
                                    pooled     = "pooled"))) +
  geom_hline(yintercept = 0, colour = "grey30") +
  scale_fill_manual(values = c("Raw-StateCtrl" = "#CB181D",
                               "State-Main"    = "#238B45"),
                    name = NULL) +
  labs(title = "b_main 对照: Raw-StateCtrl vs State-Main",
       subtitle = "误差棒 = ±1.96·SE；full 两方案下 State-Main 系统性转正",
       x = NULL, y = "b_main") +
  theme_sm() +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

save_fig(p_pair, "b_main_pair", w = 13, h = 6.2)

# =========================================================================
# 5. Sign/significance tally per (window × scheme × spec) — 12 cells
# =========================================================================
tally <- mm_all %>%
  group_by(window, window_pretty, threshold_scheme, spec) %>%
  summarise(
    n_neg_sig = sum(sign_cat == "neg_sig", na.rm = TRUE),
    n_neg_ns  = sum(sign_cat == "neg_ns",  na.rm = TRUE),
    n_pos_ns  = sum(sign_cat == "pos_ns",  na.rm = TRUE),
    n_pos_sig = sum(sign_cat == "pos_sig", na.rm = TRUE),
    .groups   = "drop"
  ) %>%
  pivot_longer(starts_with("n_"), names_to = "cat", values_to = "n") %>%
  mutate(cat = factor(cat, levels = c("n_neg_sig", "n_neg_ns", "n_pos_ns", "n_pos_sig"),
                      labels = c("负·显著", "负·不显著", "正·不显著", "正·显著")))

p_tally <- ggplot(tally, aes(x = spec, y = n, fill = cat)) +
  geom_col(position = position_stack(), width = 0.65, alpha = 0.9) +
  geom_text(data = . %>% filter(n > 0),
            aes(label = n), position = position_stack(vjust = 0.5), size = 3.1) +
  facet_grid(threshold_scheme ~ window_pretty,
             labeller = labeller(
               threshold_scheme = c(maize_zone = "maize_zone",
                                    pooled     = "pooled"))) +
  scale_fill_manual(values = c("负·显著" = "#CB181D",
                               "负·不显著" = "#FDBB84",
                               "正·不显著" = "#A1D99B",
                               "正·显著" = "#238B45"),
                    name = NULL) +
  scale_y_continuous(breaks = 0:6) +
  labs(title = "符号计数 (每单元 6 个 source-layer)",
       subtitle = "full × 两方案: Raw 5 neg-sig → State 4 pos-sig；v3pm10 也翻转",
       x = NULL, y = "# of source-layers") +
  theme_sm() +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

save_fig(p_tally, "sign_tally", w = 12, h = 6.2)

# =========================================================================
# 6. State-Main: a1 and a3 (mediator equation) sign heatmap
# =========================================================================
sm_state <- mm_all %>% filter(spec == "State-Main")

mk_coef_heat <- function(df, coef, se, pv, title) {
  df %>%
    mutate(sign_cat = sign_label(.data[[coef]], .data[[pv]]),
           stars    = sig_stars(.data[[pv]]),
           txt      = sprintf("%+.3f%s", .data[[coef]], stars)) %>%
    ggplot(aes(x = window_pretty, y = sm_label, fill = sign_cat)) +
    geom_tile(colour = "white", linewidth = 0.6) +
    geom_text(aes(label = txt), size = 2.8) +
    facet_wrap(~ threshold_scheme,
               labeller = as_labeller(c(maize_zone = "maize_zone",
                                        pooled     = "pooled"))) +
    scale_fill_manual(values = sign_cols,
                      breaks = c("neg_sig","neg_ns","pos_ns","pos_sig"),
                      labels = c("负·显著","负·不显著","正·不显著","正·显著"),
                      name = NULL) +
    labs(title = title, x = NULL, y = NULL) +
    theme_sm() +
    theme(axis.text.x = element_text(angle = 14, hjust = 1))
}

p_a1 <- mk_coef_heat(sm_state, "a1", "se_a1", "p_a1",
                     "State-Main mediator: a1 (D → DryShare)")
p_a3 <- mk_coef_heat(sm_state, "a3", "se_a3", "p_a3",
                     "State-Main mediator: a3 (D × SR → DryShare)")

p_a <- (p_a1 / p_a3) + plot_layout(guides = "collect") &
  theme(legend.position = "bottom")

save_fig(p_a, "state_a1_a3", w = 11, h = 8.5)

# =========================================================================
# 7. State-Main: b_wet coefficient heatmap (wet penalty)
# =========================================================================
p_bwet <- mk_coef_heat(sm_state, "b_wet", "se_b_wet", "p_b_wet",
                       "State-Main outcome: b_wet (WetShare → ln yield)")
save_fig(p_bwet, "state_bwet", w = 11, h = 4.5)

# =========================================================================
# 8. c3 (direct SR buffering) stability across specs
# =========================================================================
p_c3 <- mm_all %>%
  mutate(sign_cat = sign_label(c3, p_c3),
         stars    = sig_stars(p_c3)) %>%
  ggplot(aes(x = spec, y = sm_label, fill = sign_cat)) +
  geom_tile(colour = "white", linewidth = 0.6) +
  geom_text(aes(label = sprintf("%+.3f%s", c3, stars)), size = 2.8) +
  facet_grid(threshold_scheme ~ window_pretty,
             labeller = labeller(
               threshold_scheme = c(maize_zone = "maize_zone",
                                    pooled     = "pooled"))) +
  scale_fill_manual(values = sign_cols,
                    breaks = c("neg_sig","neg_ns","pos_ns","pos_sig"),
                    labels = c("负·显著","负·不显著","正·不显著","正·显著"),
                    name = NULL) +
  labs(title = "c3 (D × SR → Y direct buffering) 跨 3 spec × 3 窗口 × 2 阈值",
       subtitle = "full 普遍正显著；v3pm10 普遍负（因 v3pm10 本身并非主胁迫窗口）",
       x = NULL, y = NULL) +
  theme_sm() +
  theme(axis.text.x = element_text(angle = 18, hjust = 1))

save_fig(p_c3, "c3_stability", w = 12, h = 6.4)

# =========================================================================
# 9. Summary verdict tile: full vs v3pre30 vs v3pm10 × scheme
# =========================================================================
verdict_tbl <- tibble::tribble(
  ~window,    ~scheme,      ~verdict,                 ~detail,
  "full",    "pooled",     "改善，阈值不敏感",        "5 neg→4 pos sig",
  "full",    "maize_zone", "改善，阈值不敏感",        "5 neg→4 pos sig",
  "v3pre30", "pooled",     "恶化",                   "2 neg→3 neg sig",
  "v3pre30", "maize_zone", "几乎无净改善",           "仍 1 neg / 2 pos",
  "v3pm10",  "pooled",     "negative-control 改善",  "2 neg→5 pos sig",
  "v3pm10",  "maize_zone", "negative-control 改善",  "5 neg→5 pos sig"
)

verdict_tbl <- verdict_tbl %>%
  mutate(window = factor(window, levels = win_order),
         window_pretty = factor(win_pretty[as.character(window)],
                                levels = win_pretty[win_order]),
         scheme = factor(scheme, levels = scheme_order),
         vcol = case_when(
           str_detect(verdict, "恶化") ~ "bad",
           str_detect(verdict, "无净改善") ~ "neutral",
           str_detect(verdict, "negative-control") ~ "warn",
           TRUE ~ "good"
         ))

p_verdict <- ggplot(verdict_tbl, aes(x = window_pretty, y = scheme, fill = vcol)) +
  geom_tile(colour = "white", linewidth = 0.6) +
  geom_text(aes(label = paste0(verdict, "\n(", detail, ")")),
            size = 3.1, lineheight = 1.05) +
  scale_fill_manual(values = c(good = "#A1D99B", neutral = "#FDBB84",
                               warn = "#FDAE6B", bad = "#FB6A4A"),
                    guide = "none") +
  labs(title = "State-Main vs Raw-StateCtrl 的效应总评",
       subtitle = "full 干净改善；v3pre30 阈值敏感；v3pm10 negative-control 也改善",
       x = NULL, y = NULL) +
  theme_sm()

save_fig(p_verdict, "verdict_tile", w = 11, h = 4.2)

message("\n--- all sm_state_audit figures generated ---")
