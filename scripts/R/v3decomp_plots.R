# =============================================================================
# v3decomp_plots.R
# Purpose: Create profile-specific decomposition figures for beamer report
# Input:   output/tables/v3decomp_profile_point_estimates.csv
#          output/tables/v3decomp_bootstrap_summary.csv
# Output:  output/figures/v3decomp_plot_*.png
# =============================================================================

set.seed(42)

library(ggplot2)
library(dplyr)
library(tidyr)

projdir <- "C:/YangSu/00_Project/CA_mechanism/regression_SR"
tabdir  <- file.path(projdir, "output/tables")
figdir  <- file.path(projdir, "output/figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

point <- read.csv(file.path(tabdir, "v3decomp_profile_point_estimates.csv"),
                  stringsAsFactors = FALSE)
boot  <- read.csv(file.path(tabdir, "v3decomp_bootstrap_summary.csv"),
                  stringsAsFactors = FALSE)

profile_levels <- c("baseline", "d_only", "h_only", "dh_p75", "dh_p90", "joint_tail")
profile_labels <- c(
  "baseline" = "基准",
  "d_only" = "仅干旱 (P75)",
  "h_only" = "仅高温 (P75)",
  "dh_p75" = "干旱+高温 (P75)",
  "dh_p90" = "干旱+高温 (P90)",
  "joint_tail" = "联合尾部均值"
)
main_profiles <- c("baseline", "d_only", "h_only", "dh_p75")

profile_colors <- c(
  "基准" = "#4E79A7",
  "仅干旱 (P75)" = "#E15759",
  "仅高温 (P75)" = "#F28E2B",
  "干旱+高温 (P75)" = "#7B2D8E",
  "干旱+高温 (P90)" = "#2F7F5F",
  "联合尾部均值" = "#8C6D31"
)

stat_labels <- c(
  "DE" = "直接部分",
  "IE" = "SM中介部分",
  "TE" = "总部分"
)
stat_colors <- c(
  "直接部分" = "#2C7FB8",
  "SM中介部分" = "#D95F0E",
  "总部分" = "#238443"
)
stat_shapes <- c(
  "直接部分" = 16,
  "SM中介部分" = 17,
  "总部分" = 15
)

base_theme <- theme_minimal(base_size = 12, base_family = "sans") +
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.y = element_blank(),
    panel.grid.major.x = element_line(color = "grey90", linewidth = 0.45),
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    axis.title.y = element_blank(),
    legend.position = "bottom",
    legend.title = element_text(size = 10),
    plot.title = element_text(face = "bold", size = 15)
  )

prep_single_stat <- function(stat_name, value_col) {
  point %>%
    filter(profile %in% main_profiles) %>%
    transmute(profile, estimate = .data[[value_col]]) %>%
    left_join(
      boot %>%
        filter(stat == stat_name) %>%
        select(profile, ci_lo, ci_hi),
      by = "profile"
    ) %>%
    mutate(
      profile = factor(profile, levels = rev(main_profiles)),
      profile_label = factor(profile_labels[as.character(profile)],
                             levels = rev(profile_labels[main_profiles]))
    )
}

a_df <- prep_single_stat("a_hat", "a_hat") %>% mutate(a_hat = estimate)
b_df <- prep_single_stat("b_hat", "b_hat") %>% mutate(b_hat = estimate)

decomp_df <- point %>%
  filter(profile %in% main_profiles) %>%
  select(profile, DE, IE, TE) %>%
  pivot_longer(cols = c(DE, IE, TE), names_to = "stat", values_to = "estimate") %>%
  left_join(
    boot %>%
      filter(stat %in% c("DE", "IE", "TE")) %>%
      select(profile, stat, ci_lo, ci_hi),
    by = c("profile", "stat")
  ) %>%
  mutate(
    profile = factor(profile, levels = rev(main_profiles)),
    profile_label = factor(profile_labels[as.character(profile)],
                           levels = rev(profile_labels[main_profiles])),
    stat_label = factor(stat_labels[stat], levels = c("直接部分", "SM中介部分", "总部分"))
  )

share_df <- point %>%
  filter(profile %in% main_profiles) %>%
  select(profile, share) %>%
  left_join(
    boot %>%
      filter(stat == "share") %>%
      select(profile, ci_lo, ci_hi),
    by = "profile"
  ) %>%
  mutate(
    share_pct = 100 * share,
    ci_lo_pct = 100 * ci_lo,
    ci_hi_pct = 100 * ci_hi,
    profile = factor(profile, levels = rev(main_profiles)),
    profile_label = factor(profile_labels[as.character(profile)],
                           levels = rev(profile_labels[main_profiles]))
  )

p_a <- ggplot(a_df, aes(x = a_hat, y = profile_label, color = profile_label)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
  geom_linerange(aes(xmin = ci_lo, xmax = ci_hi), orientation = "y", linewidth = 1.0) +
  geom_point(size = 3) +
  scale_color_manual(values = profile_colors, name = "胁迫情景") +
  labs(
    title = "图A：不同胁迫情景下的 dSM / dSR",
    x = "a(d, h, w) 与 95% bootstrap 置信区间"
  ) +
  base_theme

p_b <- ggplot(b_df, aes(x = b_hat, y = profile_label, color = profile_label)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
  geom_linerange(aes(xmin = ci_lo, xmax = ci_hi), orientation = "y", linewidth = 1.0) +
  geom_point(size = 3) +
  scale_color_manual(values = profile_colors, name = "胁迫情景") +
  labs(
    title = "图B：不同胁迫情景下的 dln(Y) / dSM",
    x = "b(d, h) 与 95% bootstrap 置信区间"
  ) +
  base_theme

dodge_pos <- position_dodge(width = 0.6)

p_decomp <- ggplot(decomp_df, aes(x = estimate, y = profile_label, color = stat_label, shape = stat_label)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
  geom_linerange(
    aes(xmin = ci_lo, xmax = ci_hi),
    position = dodge_pos,
    orientation = "y",
    linewidth = 0.9
  ) +
  geom_point(position = dodge_pos, size = 2.8) +
  scale_color_manual(values = stat_colors, name = "分解部分") +
  scale_shape_manual(values = stat_shapes, name = "分解部分") +
  labs(
    title = "图C：直接部分、SM中介部分与总部分",
    x = "估计值与 95% bootstrap 置信区间"
  ) +
  base_theme

p_share <- ggplot(share_df, aes(x = share_pct, y = profile_label, color = profile_label)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.5) +
  geom_linerange(aes(xmin = ci_lo_pct, xmax = ci_hi_pct), orientation = "y", linewidth = 1.0) +
  geom_point(size = 3) +
  scale_color_manual(values = profile_colors, name = "胁迫情景") +
  labs(
    title = "图D：总缓冲中的中介占比",
    x = "中介占比（%）与 95% bootstrap 置信区间"
  ) +
  base_theme

ggsave(file.path(figdir, "v3decomp_plot_a_hat.png"), p_a,
       width = 12, height = 5, dpi = 300, bg = "white")
ggsave(file.path(figdir, "v3decomp_plot_b_hat.png"), p_b,
       width = 12, height = 5, dpi = 300, bg = "white")
ggsave(file.path(figdir, "v3decomp_plot_decomp.png"), p_decomp,
       width = 12, height = 5.4, dpi = 300, bg = "white")
ggsave(file.path(figdir, "v3decomp_plot_share.png"), p_share,
       width = 12, height = 5, dpi = 300, bg = "white")

cat("Saved v3decomp plots to:", figdir, "\n")
