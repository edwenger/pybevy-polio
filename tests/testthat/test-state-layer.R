# Tests for State Layer - Individual component management (Host, Immunity, Infection)
# R equivalent of test_state_layer.py

source("setup-pybevy.R")

# Test Host component class
test_that("Host default construction works", {
  host <- pb$Host(birth_sim_day = -365L * 20L)
  expect_equal(host$birth_sim_day, -365L * 20L)
})

test_that("Host birth_sim_day modification works", {
  test_host <- get_test_host()
  
  original_birth <- test_host$birth_sim_day
  test_host$birth_sim_day <- -365L * 5L
  
  expect_equal(test_host$birth_sim_day, -365L * 5L)
  expect_false(test_host$birth_sim_day == original_birth)
})

test_that("Host works with different ages", {
  age_years_list <- c(0, 5, 20, 50, 80)
  
  for (age_years in age_years_list) {
    birth_day <- -365L * age_years
    host <- pb$Host(birth_sim_day = birth_day)
    expect_equal(host$birth_sim_day, birth_day)
  }
})

# Test Immunity component class
test_that("Immunity default construction works", {
  immunity <- pb$Immunity()
  
  expect_true(is.numeric(immunity$current_immunity))
  expect_true(is.numeric(immunity$prechallenge_immunity))
  expect_true(is.numeric(immunity$postchallenge_peak_immunity))
  # ti_infected should be NULL initially or numeric
  expect_true(is.null(immunity$ti_infected) || is.numeric(immunity$ti_infected))
})

test_that("Immunity with_values construction works", {
  immunity <- pb$Immunity$with_values(2.0, 5.0, 4.0, 7.5)
  
  # Check actual parameter mapping based on the constructor implementation
  expect_equal(immunity$prechallenge_immunity, 2.0, tolerance = 1e-6)  # 1st param
  expect_equal(immunity$postchallenge_peak_immunity, 5.0, tolerance = 1e-6)  # 2nd param
  expect_equal(immunity$current_immunity, 4.0, tolerance = 1e-6)  # 3rd param
  expect_equal(immunity$ti_infected, 7.5, tolerance = 1e-6)  # 4th param
})

test_that("Immunity property modification works", {
  test_immunity <- get_test_immunity()
  
  test_immunity$current_immunity <- 8.5
  test_immunity$prechallenge_immunity <- 3.2
  test_immunity$postchallenge_peak_immunity <- 12.1
  test_immunity$ti_infected <- 15.0
  
  expect_equal(test_immunity$current_immunity, 8.5, tolerance = 1e-6)
  expect_equal(test_immunity$prechallenge_immunity, 3.2, tolerance = 1e-6)
  expect_equal(test_immunity$postchallenge_peak_immunity, 12.1, tolerance = 1e-6)
  expect_equal(test_immunity$ti_infected, 15.0, tolerance = 1e-6)
})

test_that("Immunity works with different immunity levels", {
  immunity_levels <- c(0.1, 1.0, 5.0, 15.0)
  
  for (immunity_level in immunity_levels) {
    immunity <- pb$Immunity$with_values(
      current_immunity = immunity_level,
      prechallenge_immunity = immunity_level,
      postchallenge_peak_immunity = 0.0,
      ti_infected = NULL
    )
    
    expect_equal(immunity$current_immunity, immunity_level, tolerance = 1e-6)
    expect_equal(immunity$prechallenge_immunity, immunity_level, tolerance = 1e-6)
  }
})

# Test Infection component class
test_that("Infection construction works", {
  infection <- pb$Infection(
    shed_duration = 42.5,
    viral_shedding = 1000.0,
    strain = pb$InfectionStrain$WPV,
    serotype = pb$InfectionSerotype$Type2
  )
  
  expect_equal(infection$shed_duration, 42.5)
  expect_equal(infection$viral_shedding, 1000.0)
  expect_equal(infection$strain, pb$InfectionStrain$WPV)
  expect_equal(infection$serotype, pb$InfectionSerotype$Type2)
})

test_that("Infection property modification works", {
  test_infection <- get_test_infection()
  
  test_infection$shed_duration <- 30.0
  test_infection$viral_shedding <- 500.0
  test_infection$strain <- pb$InfectionStrain$OPV
  test_infection$serotype <- pb$InfectionSerotype$Type3
  
  expect_equal(test_infection$shed_duration, 30.0)
  expect_equal(test_infection$viral_shedding, 500.0)
  expect_equal(test_infection$strain, pb$InfectionStrain$OPV)
  expect_equal(test_infection$serotype, pb$InfectionSerotype$Type3)
})

test_that("Infection works with different strains", {
  infection_strains <- get_infection_strains()
  
  for (strain in infection_strains) {
    infection <- pb$Infection(
      shed_duration = 40.0,
      viral_shedding = 1000.0,
      strain = strain,
      serotype = pb$InfectionSerotype$Type1
    )
    expect_equal(infection$strain, strain)
  }
})

test_that("Infection works with different serotypes", {
  infection_serotypes <- get_infection_serotypes()
  
  for (serotype in infection_serotypes) {
    infection <- pb$Infection(
      shed_duration = 40.0,
      viral_shedding = 1000.0,
      strain = pb$InfectionStrain$WPV,
      serotype = serotype
    )
    expect_equal(infection$serotype, serotype)
  }
})

# Test InfectionStrain and InfectionSerotype enums
test_that("InfectionStrain enum values work", {
  wpv <- pb$InfectionStrain$WPV
  opv <- pb$InfectionStrain$OPV
  
  expect_false(identical(wpv, opv))
  expect_true(is.character(as.character(wpv)))
  expect_true(is.character(as.character(opv)))
})

test_that("InfectionSerotype enum values work", {
  type1 <- pb$InfectionSerotype$Type1
  type2 <- pb$InfectionSerotype$Type2
  type3 <- pb$InfectionSerotype$Type3
  
  expect_false(identical(type1, type2))
  expect_false(identical(type2, type3))
  expect_false(identical(type1, type3))
  expect_true(is.character(as.character(type1)))
  expect_true(is.character(as.character(type2)))
  expect_true(is.character(as.character(type3)))
})

test_that("Infection works with all enum combinations", {
  infection_strains <- get_infection_strains()
  infection_serotypes <- get_infection_serotypes()
  
  for (strain in infection_strains) {
    for (serotype in infection_serotypes) {
      infection <- pb$Infection(
        shed_duration = 40.0,
        viral_shedding = 1000.0,
        strain = strain,
        serotype = serotype
      )
      expect_equal(infection$strain, strain)
      expect_equal(infection$serotype, serotype)
    }
  }
})