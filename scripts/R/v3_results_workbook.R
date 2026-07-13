# =============================================================================
# v3_results_workbook.R
# Purpose: Collect non-mediation v3 log outputs into one review workbook
# Author:  YangSu + Codex
# Date:    2026-04-07
# Input:   output/tables/v3_step1_baseline.csv
#          output/tables/v3_step1_baseline_full.csv
#          output/tables/v3_step2_stage_single.csv
#          output/tables/v3_step2_single_table.csv
#          output/tables/v3_step2_stage_horserace.csv
#          output/tables/v3_step2_horserace_table.csv
#          output/tables/v3_step3_attenuation.csv
#          output/tables/v3_step3_apath.csv
#          output/tables/v3_step4_full_coefs.csv
#          output/tables/v3_step4_interaction_grid.csv
#          output/tables/v3_step4_attenuation.csv
#          output/tables/v3_step5_robustness.csv
#          output/tables/v3_step8_zone.csv
#          output/tables/v3_step8_irrigation.csv
# Output:  output/tables/v3_report_results_equation_first.xlsx
# =============================================================================

set.seed(42)
options(scipen = 999)

ensure_package <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
}

ensure_package("openxlsx")

suppressPackageStartupMessages({
  library(openxlsx)
})

projdir <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
if (!file.exists(file.path(projdir, "AGENTS.md"))) {
  stop("Run this script from the project root so relative paths resolve correctly.")
}

outdir <- file.path(projdir, "output", "tables")
outfile <- file.path(outdir, "v3_report_results_equation_first.xlsx")

escape_excel <- function(x) {
  out <- ifelse(is.na(x), "", as.character(x))
  needs_quote <- grepl("^=", out)
  out[needs_quote] <- paste0("'", out[needs_quote])
  out
}

read_csv_block <- function(path, header = TRUE) {
  if (header) {
    df <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
    names(df) <- escape_excel(names(df))
  } else {
    df <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE, header = FALSE)
  }

  df[] <- lapply(df, escape_excel)
  df
}

write_merged_text <- function(wb, sheet, row, text, ncols, style, height = NULL) {
  writeData(wb, sheet, x = text, startRow = row, startCol = 1, colNames = FALSE)
  mergeCells(wb, sheet, cols = 1:ncols, rows = row)
  addStyle(wb, sheet, style = style, rows = row, cols = 1:ncols, gridExpand = TRUE, stack = TRUE)
  if (!is.null(height)) {
    setRowHeights(wb, sheet, rows = row, heights = height)
  }
}

write_table_block <- function(wb,
                              sheet,
                              start_row,
                              title,
                              note,
                              data,
                              styles,
                              has_header = TRUE) {
  ncols <- ncol(data)
  if (ncols == 0) {
    stop(sprintf("No columns available for block '%s' on sheet '%s'.", title, sheet))
  }

  write_merged_text(wb, sheet, start_row, title, ncols, styles$title, height = 22)
  write_merged_text(wb, sheet, start_row + 1, note, ncols, styles$note, height = 34)

  writeData(
    wb,
    sheet,
    x = data,
    startRow = start_row + 2,
    startCol = 1,
    colNames = has_header,
    rowNames = FALSE,
    withFilter = FALSE
  )

  if (has_header) {
    addStyle(
      wb,
      sheet,
      style = styles$header,
      rows = start_row + 2,
      cols = seq_len(ncols),
      gridExpand = TRUE,
      stack = TRUE
    )

    if (nrow(data) > 0) {
      addStyle(
        wb,
        sheet,
        style = styles$body,
        rows = (start_row + 3):(start_row + 2 + nrow(data)),
        cols = seq_len(ncols),
        gridExpand = TRUE,
        stack = TRUE
      )
    }
  } else if (nrow(data) > 0) {
    addStyle(
      wb,
      sheet,
      style = styles$body,
      rows = (start_row + 2):(start_row + 1 + nrow(data)),
      cols = seq_len(ncols),
      gridExpand = TRUE,
      stack = TRUE
    )
  }

  setColWidths(wb, sheet, cols = seq_len(ncols), widths = "auto")

  if (has_header) {
    return(start_row + 2 + nrow(data) + 2)
  }

  start_row + 1 + nrow(data) + 2
}

required_files <- c(
  "output/tables/v3_step1_baseline.csv",
  "output/tables/v3_step1_baseline_full.csv",
  "output/tables/v3_step2_stage_single.csv",
  "output/tables/v3_step2_single_table.csv",
  "output/tables/v3_step2_stage_horserace.csv",
  "output/tables/v3_step2_horserace_table.csv",
  "output/tables/v3_step3_attenuation.csv",
  "output/tables/v3_step3_apath.csv",
  "output/tables/v3_step4_full_coefs.csv",
  "output/tables/v3_step4_interaction_grid.csv",
  "output/tables/v3_step4_attenuation.csv",
  "output/tables/v3_step5_robustness.csv",
  "output/tables/v3_step8_zone.csv",
  "output/tables/v3_step8_irrigation.csv"
)

missing_files <- required_files[!file.exists(file.path(projdir, required_files))]
if (length(missing_files) > 0) {
  stop(sprintf("Missing required inputs: %s", paste(missing_files, collapse = ", ")))
}

styles <- list(
  title = createStyle(
    fontSize = 13,
    textDecoration = "bold",
    fgFill = "#D9EAF7",
    halign = "left",
    valign = "center",
    border = "TopBottomLeftRight",
    borderStyle = "thin"
  ),
  note = createStyle(
    fontSize = 10,
    textDecoration = "italic",
    wrapText = TRUE,
    fgFill = "#F7F7F7",
    halign = "left",
    valign = "top",
    border = "TopBottomLeftRight",
    borderStyle = "thin"
  ),
  header = createStyle(
    fontSize = 10,
    textDecoration = "bold",
    fontColour = "#FFFFFF",
    fgFill = "#4F81BD",
    halign = "center",
    valign = "center",
    border = "TopBottomLeftRight",
    borderStyle = "thin"
  ),
  body = createStyle(
    fontSize = 10,
    halign = "center",
    valign = "center",
    border = "TopBottomLeftRight",
    borderStyle = "thin",
    wrapText = TRUE
  )
)

wb <- createWorkbook(creator = "Codex")
sheet_names <- c(
  "00_log_map",
  "01_step1_baseline",
  "02_step2_stage_effects",
  "03_step3_sm_comparison",
  "04_step4_nonmediation",
  "05_step5_robustness",
  "06_step8_heterogeneity"
)

for (sheet in sheet_names) {
  addWorksheet(wb, sheet, gridLines = FALSE, zoom = 90)
}

log_map <- data.frame(
  log_file = c(
    "output/logs/v3_step0_preamble.log",
    "output/logs/v3_step1_baseline.log",
    "output/logs/v3_step2_stage_effects.log",
    "output/logs/v3_step3_sm_comparison.log",
    "output/logs/v3_step4_full_coefs_20260406.log",
    "output/logs/v3_step4_interaction_grid_20260405.log",
    "output/logs/v3_step4_mediation.log",
    "output/logs/v3_step5_robustness.log",
    "output/logs/v3_step6b_mediation_countyFE_20260405.log",
    "output/logs/v3_step8_heterogeneity_20260405.log"
  ),
  status = c(
    "excluded",
    "included",
    "included",
    "included",
    "included",
    "included",
    "excluded",
    "included",
    "excluded",
    "included"
  ),
  workbook_sheet = c(
    "",
    "01_step1_baseline",
    "02_step2_stage_effects",
    "03_step3_sm_comparison",
    "04_step4_nonmediation",
    "04_step4_nonmediation",
    "",
    "05_step5_robustness",
    "",
    "06_step8_heterogeneity"
  ),
  outputs_or_reason = c(
    "Setup only; no empirical results exported.",
    "v3_step1_baseline.csv; v3_step1_baseline_full.csv",
    "v3_step2_stage_single.csv; v3_step2_single_table.csv; v3_step2_stage_horserace.csv; v3_step2_horserace_table.csv",
    "v3_step3_attenuation.csv; v3_step3_apath.csv",
    "v3_step4_full_coefs.csv",
    "v3_step4_interaction_grid.csv; v3_step4_attenuation.csv",
    "Excluded because the user requested no mediation effects.",
    "v3_step5_robustness.csv",
    "Excluded because the user requested no mediation effects.",
    "v3_step8_zone.csv; v3_step8_irrigation.csv"
  ),
  stringsAsFactors = FALSE
)

row_ptr <- 1
row_ptr <- write_table_block(
  wb = wb,
  sheet = "00_log_map",
  start_row = row_ptr,
  title = "v3 non-mediation log coverage map",
  note = paste(
    "This workbook tries to list all empirical results backed by v3 logs,",
    "while excluding mediation-specific logs and outputs."
  ),
  data = log_map,
  styles = styles,
  has_header = TRUE
)

step_configs <- list(
  list(
    sheet = "01_step1_baseline",
    blocks = list(
      list(
        title = "Step 1 key results",
        note = paste(
          "Log source: output/logs/v3_step1_baseline.log.",
          "Equation family: full-season baseline across Spec(1), Spec(2), Spec(3) by SM source,",
          "Spec(4) by SM source, plus one province-year FE comparison."
        ),
        path = "output/tables/v3_step1_baseline.csv",
        header = TRUE
      ),
      list(
        title = "Step 1 full regression table",
        note = paste(
          "Raw table exported by esttab from v3_step1_baseline.log.",
          "Full-season, nine columns: Spec1, Spec2, Spec3-G, Spec3-S, Spec3-E, Spec4-G, Spec4-S, Spec4-E, Spec2-ProvYr."
        ),
        path = "output/tables/v3_step1_baseline_full.csv",
        header = FALSE
      )
    )
  ),
  list(
    sheet = "02_step2_stage_effects",
    blocks = list(
      list(
        title = "Step 2A single-window Spec(2) results",
        note = paste(
          "Log source: output/logs/v3_step2_stage_effects.log.",
          "Equation: Spec(2) re-estimated over six windows."
        ),
        path = "output/tables/v3_step2_stage_single.csv",
        header = TRUE
      ),
      list(
        title = "Step 2A single-window table export",
        note = "Raw esttab export from Step 2A. This reproduces the regression table shown in the log.",
        path = "output/tables/v3_step2_single_table.csv",
        header = FALSE
      ),
      list(
        title = "Step 2B horserace postfile",
        note = paste(
          "Alternative stage-grouping schemes from v3_step2_stage_effects.log.",
          "Rows identify scheme, window, and coefficient type."
        ),
        path = "output/tables/v3_step2_stage_horserace.csv",
        header = TRUE
      ),
      list(
        title = "Step 2B horserace table export",
        note = "Raw esttab export from the horserace section of v3_step2_stage_effects.log.",
        path = "output/tables/v3_step2_horserace_table.csv",
        header = FALSE
      )
    )
  ),
  list(
    sheet = "03_step3_sm_comparison",
    blocks = list(
      list(
        title = "Step 3 attenuation matrix",
        note = paste(
          "Log source: output/logs/v3_step3_sm_comparison.log.",
          "Non-mediation channel diagnostic: attenuation from Spec(1) to Spec(3) by SM source and window."
        ),
        path = "output/tables/v3_step3_attenuation.csv",
        header = TRUE
      ),
      list(
        title = "Step 3 a-path style diagnostics",
        note = paste(
          "Log source: output/logs/v3_step3_sm_comparison.log.",
          "Non-mediation diagnostics relating drought, SR, and SM outcomes."
        ),
        path = "output/tables/v3_step3_apath.csv",
        header = TRUE
      )
    )
  ),
  list(
    sheet = "04_step4_nonmediation",
    blocks = list(
      list(
        title = "Step 4 full coefficient grid",
        note = paste(
          "Log source: output/logs/v3_step4_full_coefs_20260406.log.",
          "All coefficients from Spec(1)-Spec(4), six windows, three SM sources where applicable."
        ),
        path = "output/tables/v3_step4_full_coefs.csv",
        header = TRUE
      ),
      list(
        title = "Step 4 interaction grid",
        note = paste(
          "Log source: output/logs/v3_step4_interaction_grid_20260405.log.",
          "Compact evidence matrix for SR, compound, and SM interaction terms."
        ),
        path = "output/tables/v3_step4_interaction_grid.csv",
        header = TRUE
      ),
      list(
        title = "Step 4 attenuation summaries",
        note = paste(
          "Derived from the interaction-grid log and exported as v3_step4_attenuation.csv.",
          "This section is retained because it is not a mediation-effect estimate."
        ),
        path = "output/tables/v3_step4_attenuation.csv",
        header = TRUE
      )
    )
  ),
  list(
    sheet = "05_step5_robustness",
    blocks = list(
      list(
        title = "Step 5 robustness results",
        note = paste(
          "Log source: output/logs/v3_step5_robustness.log.",
          "Includes FE sensitivity, heat-threshold sensitivity, year-drop tests, and province-year window variants."
        ),
        path = "output/tables/v3_step5_robustness.csv",
        header = TRUE
      )
    )
  ),
  list(
    sheet = "06_step8_heterogeneity",
    blocks = list(
      list(
        title = "Step 8 heterogeneity by zone",
        note = paste(
          "Log source: output/logs/v3_step8_heterogeneity_20260405.log.",
          "Spec(2) re-estimated within maize production zones across six windows."
        ),
        path = "output/tables/v3_step8_zone.csv",
        header = TRUE
      ),
      list(
        title = "Step 8 heterogeneity by irrigation split",
        note = paste(
          "Log source: output/logs/v3_step8_heterogeneity_20260405.log.",
          "Spec(2) re-estimated within low- and high-irrigation groups across six windows."
        ),
        path = "output/tables/v3_step8_irrigation.csv",
        header = TRUE
      )
    )
  )
)

for (cfg in step_configs) {
  row_ptr <- 1
  for (block in cfg$blocks) {
    block_data <- read_csv_block(file.path(projdir, block$path), header = block$header)
    row_ptr <- write_table_block(
      wb = wb,
      sheet = cfg$sheet,
      start_row = row_ptr,
      title = block$title,
      note = block$note,
      data = block_data,
      styles = styles,
      has_header = block$header
    )
  }
}

saveWorkbook(wb, outfile, overwrite = TRUE)

cat("Saved workbook:", outfile, "\n")
cat("Sheets:", paste(names(wb), collapse = ", "), "\n")
