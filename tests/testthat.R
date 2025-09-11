# Main testthat test runner for PyBevy-Polio R tests
# Run with: Rscript tests/testthat.R

library(testthat)

# Set working directory to project root if needed
if (!file.exists("CLAUDE.md")) {
  if (file.exists("../../CLAUDE.md")) {
    setwd("../..")
  } else {
    stop("Cannot find project root directory with CLAUDE.md")
  }
}

# Run all tests in testthat directory
test_dir("tests/testthat", reporter = "summary")

cat("\n✅ R unit tests completed!\n")