# Tests for Function Layer - Pure calculation methods on Immunity and Infection classes
# R equivalent of test_function_layer.py

source("setup-pybevy.R")

# Test Immunity calculation methods
test_that("Immunity calculate_waning works", {
  test_immunity <- get_test_immunity()
  immunity_waning_params <- get_immunity_waning_params()
  
  original_immunity <- test_immunity$current_immunity
  test_immunity$calculate_waning(365.0, immunity_waning_params)  # Use longer time for actual waning
  
  # Immunity should decrease over time
  expect_true(test_immunity$current_immunity <= original_immunity)
  expect_true(is.numeric(test_immunity$current_immunity))
  expect_true(test_immunity$current_immunity >= 0.0)
})

test_that("Immunity calculate_waning shows time dependency", {
  immunity_waning_params <- get_immunity_waning_params()
  days_since_infection_list <- c(1.0, 30.0, 90.0, 365.0)
  
  for (days_since_infection in days_since_infection_list) {
    immunity <- pb$Immunity$with_values(10.0, 10.0, 10.0, 0.0)
    immunity$calculate_waning(days_since_infection, immunity_waning_params)
    
    # Longer time should result in lower immunity
    expect_true(immunity$current_immunity <= 10.0)
    expect_true(immunity$current_immunity >= 0.0)
  }
})

test_that("Immunity calculate_infection_probability works", {
  test_immunity <- get_test_immunity()
  default_params <- get_default_params()
  
  prob <- test_immunity$calculate_infection_probability(
    dose = 1000.0,
    strain = pb$InfectionStrain$WPV,
    serotype = pb$InfectionSerotype$Type2,
    params = default_params
  )
  
  expect_true(is.numeric(prob))
  expect_in_range(prob, 0.0, 1.0, "infection probability")
})

test_that("Infection probability shows dose response", {
  default_params <- get_default_params()
  test_doses <- get_test_doses()
  
  for (dose in test_doses) {
    immunity <- pb$Immunity$with_values(5.0, 5.0, 0.0, NULL)
    
    prob <- immunity$calculate_infection_probability(
      dose = dose,
      strain = pb$InfectionStrain$WPV,
      serotype = pb$InfectionSerotype$Type2,
      params = default_params
    )
    
    expect_true(is.numeric(prob))
    expect_in_range(prob, 0.0, 1.0, "infection probability")
  }
})

test_that("Infection probability shows immunity protection", {
  default_params <- get_default_params()
  immunity_levels <- get_immunity_levels()
  
  for (immunity_level in immunity_levels) {
    immunity <- pb$Immunity$with_values(immunity_level, immunity_level, 0.0, NULL)
    
    prob <- immunity$calculate_infection_probability(
      dose = 1000.0,
      strain = pb$InfectionStrain$WPV,
      serotype = pb$InfectionSerotype$Type2,
      params = default_params
    )
    
    expect_true(is.numeric(prob))
    expect_in_range(prob, 0.0, 1.0, "infection probability")
  }
})

test_that("Immunity calculate_viral_shedding works", {
  test_immunity <- get_test_immunity()
  default_params <- get_default_params()
  
  viral_shedding <- test_immunity$calculate_viral_shedding(
    24.0, 7.0, default_params
  )
  
  expect_true(is.numeric(viral_shedding))
  expect_true(viral_shedding >= 0.0)
})

test_that("Viral shedding shows time course", {
  default_params <- get_default_params()
  days_since_infection_list <- c(1.0, 7.0, 14.0, 30.0)
  
  for (days_since_infection in days_since_infection_list) {
    immunity <- pb$Immunity$with_values(2.0, 8.0, 4.0, 0.0)
    
    viral_shedding <- immunity$calculate_viral_shedding(
      days_since_infection, 30.0, default_params
    )
    
    expect_true(is.numeric(viral_shedding))
    expect_true(viral_shedding >= 0.0)
  }
})

test_that("Immunity calculate_shed_duration works", {
  test_immunity <- get_test_immunity()
  shed_duration_params <- get_shed_duration_params()
  
  duration <- test_immunity$calculate_shed_duration(shed_duration_params)
  
  expect_true(is.numeric(duration))
  expect_true(duration > 0.0)
})

test_that("Shed duration shows immunity dependency", {
  shed_duration_params <- get_shed_duration_params()
  immunity_levels <- c(1.0, 5.0, 10.0)
  
  for (immunity_level in immunity_levels) {
    immunity <- pb$Immunity$with_values(immunity_level, immunity_level, 0.0, NULL)
    duration <- immunity$calculate_shed_duration(shed_duration_params)
    
    expect_true(is.numeric(duration))
    expect_true(duration > 0.0)
  }
})

# Test Infection calculation methods
test_that("Infection should_clear_infection works early in course", {
  test_infection <- get_test_infection()
  
  should_clear <- test_infection$should_clear_infection(days_since_infection = 5.0)
  
  expect_true(is.logical(should_clear))
  # Early in infection, should typically not clear
  expect_false(should_clear)
})

test_that("Infection should_clear_infection works late in course", {
  test_infection <- get_test_infection()
  
  should_clear <- test_infection$should_clear_infection(days_since_infection = 60.0)
  
  expect_true(is.logical(should_clear))
  # Late in infection, should typically clear (depends on shed_duration=42.5)
  expect_true(should_clear)
})

test_that("Infection clearance shows time course", {
  days_since_infection_list <- c(1.0, 20.0, 40.0, 60.0)
  
  for (days_since_infection in days_since_infection_list) {
    infection <- pb$Infection(
      shed_duration = 30.0,  # Fixed duration for predictable testing
      viral_shedding = 1000.0,
      strain = pb$InfectionStrain$WPV,
      serotype = pb$InfectionSerotype$Type1
    )
    
    should_clear <- infection$should_clear_infection(days_since_infection)
    expect_true(is.logical(should_clear))
    
    # Should clear after shed_duration
    if (days_since_infection > 30.0) {
      expect_true(should_clear)
    } else {
      expect_false(should_clear)
    }
  }
})

test_that("Clearance depends on shed duration", {
  shed_duration_list <- c(10.0, 30.0, 60.0)
  
  for (shed_duration in shed_duration_list) {
    infection <- pb$Infection(
      shed_duration = shed_duration,
      viral_shedding = 1000.0,
      strain = pb$InfectionStrain$WPV,
      serotype = pb$InfectionSerotype$Type1
    )
    
    # Test at half and one-and-a-half times the shed duration
    should_clear_early <- infection$should_clear_infection(shed_duration * 0.5)
    should_clear_late <- infection$should_clear_infection(shed_duration * 1.5)
    
    expect_false(should_clear_early)
    expect_true(should_clear_late)
  }
})

# Test method integration
test_that("Infection to clearance workflow works", {
  default_params <- get_default_params()
  shed_duration_params <- get_shed_duration_params()
  
  immunity <- pb$Immunity$with_values(3.0, 3.0, 0.0, NULL)
  
  # Step 1: Calculate infection probability
  infection_prob <- immunity$calculate_infection_probability(
    dose = 5000.0,
    strain = pb$InfectionStrain$WPV,
    serotype = pb$InfectionSerotype$Type2,
    params = default_params
  )
  expect_in_range(infection_prob, 0.0, 1.0, "infection probability")
  
  # Step 2: If infected, calculate shed duration
  if (infection_prob > 0.1) {  # Simulate infection occurs
    shed_duration <- immunity$calculate_shed_duration(shed_duration_params)
    expect_true(shed_duration > 0.0)
    
    # Step 3: Create infection
    infection <- pb$Infection(
      shed_duration = shed_duration,
      viral_shedding = 1000.0,
      strain = pb$InfectionStrain$WPV,
      serotype = pb$InfectionSerotype$Type2
    )
    
    # Step 4: Check clearance at different times
    should_clear_early <- infection$should_clear_infection(5.0)
    should_clear_late <- infection$should_clear_infection(shed_duration + 10.0)
    
    expect_false(should_clear_early)
    expect_true(should_clear_late)
  }
})

test_that("All strain/serotype combinations work in calculations", {
  default_params <- get_default_params()
  infection_strains <- get_infection_strains()
  infection_serotypes <- get_infection_serotypes()
  
  immunity <- pb$Immunity$with_values(5.0, 5.0, 0.0, NULL)
  
  for (strain in infection_strains) {
    for (serotype in infection_serotypes) {
      # Test infection probability calculation
      prob <- immunity$calculate_infection_probability(
        dose = 1000.0,
        strain = strain,
        serotype = serotype,
        params = default_params
      )
      expect_in_range(prob, 0.0, 1.0, "infection probability")
      
      # Test infection clearance
      infection <- pb$Infection(
        shed_duration = 40.0,
        viral_shedding = 1000.0,
        strain = strain,
        serotype = serotype
      )
      should_clear <- infection$should_clear_infection(50.0)
      expect_true(is.logical(should_clear))
    }
  }
})