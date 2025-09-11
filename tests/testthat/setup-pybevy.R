# Setup utilities for PyBevy-Polio R unit tests
# Provides shared fixtures and test utilities consistent with Python conftest.py

# Load required packages with error handling
tryCatch({
  library(reticulate)
  library(testthat)
}, error = function(e) {
  skip("Required R packages not available: reticulate, testthat")
})

# Import PyBevy with error handling
tryCatch({
  pb <<- import("pybevy")$pybevy  # Global assignment for test access
}, error = function(e) {
  skip("PyBevy not available. Run: maturin develop --release")
})

# Test fixture functions (equivalent to Python fixtures)

get_default_params <- function() {
  "Default parameter set for testing."
  pb$Params()
}

get_immunity_waning_params <- function() {
  "Default immunity waning parameters."
  pb$ImmunityWaningParams()
}

get_theta_nabs_params <- function() {
  "Default theta nabs parameters."
  pb$ThetaNabsParams()
}

get_viral_shedding_params <- function() {
  "Default viral shedding parameters."
  pb$ViralSheddingParams()
}

get_peak_cid50_params <- function() {
  "Default peak CID50 parameters."
  pb$PeakCid50Params()
}

get_prob_transmit_params <- function() {
  "Default transmission probability parameters."
  pb$ProbTransmitParams()
}

get_shed_duration_params <- function() {
  "Default shedding duration parameters."
  pb$ShedDurationParams()
}

get_strain_params <- function() {
  "Default strain parameters."
  params <- pb$StrainParams()
  params$shed_duration <- get_shed_duration_params()
  params
}

get_test_host <- function() {
  "Test host with standard age (20 years old)."
  pb$Host(birth_sim_day = -365L * 20L)
}

get_test_immunity <- function() {
  "Test immunity with standard values."
  pb$Immunity$with_values(
    current_immunity = 2.0,
    prechallenge_immunity = 8.0,
    postchallenge_peak_immunity = 4.0,
    ti_infected = 10.0
  )
}

get_test_infection <- function() {
  "Test infection with WPV Type2."
  pb$Infection(
    shed_duration = 42.5,
    viral_shedding = 1000.0,
    strain = pb$InfectionStrain$WPV,
    serotype = pb$InfectionSerotype$Type2
  )
}

get_infection_strains <- function() {
  "All infection strains for parametrized tests."
  list(pb$InfectionStrain$WPV, pb$InfectionStrain$OPV)
}

get_infection_serotypes <- function() {
  "All infection serotypes for parametrized tests."
  list(
    pb$InfectionSerotype$Type1,
    pb$InfectionSerotype$Type2,
    pb$InfectionSerotype$Type3
  )
}

get_test_doses <- function() {
  "Range of test doses for dose-response testing."
  c(100.0, 1000.0, 10000.0, 100000.0)
}

get_immunity_levels <- function() {
  "Range of immunity levels for testing."
  c(0.5, 2.0, 5.0, 10.0)
}

# Helper function to check if value is within expected range
expect_in_range <- function(value, min_val, max_val, label = "value") {
  expect_true(value >= min_val && value <= max_val, 
              info = paste(label, "should be between", min_val, "and", max_val, 
                          "but got", value))
}