packages <- c(
  "grf",
  "ranger",
  "fixest",
  "sandwich",
  "lmtest",
  "tidyverse",
  "data.table"
)

repos <- "https://cloud.r-project.org"
installed <- rownames(installed.packages())
missing <- setdiff(packages, installed)

if (length(missing) > 0) {
  install.packages(missing, repos = repos, dependencies = TRUE)
}

status <- data.frame(
  package = packages,
  installed = vapply(packages, requireNamespace, logical(1), quietly = TRUE),
  version = vapply(
    packages,
    function(pkg) {
      if (requireNamespace(pkg, quietly = TRUE)) {
        as.character(utils::packageVersion(pkg))
      } else {
        NA_character_
      }
    },
    character(1)
  )
)

print(status)

if (!all(status$installed)) {
  stop("Some R ML dependencies failed to install")
}
