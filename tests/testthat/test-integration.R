# Tests for Integration Layer - Cross-layer integration and end-to-end workflows
# R equivalent of test_integration.py

source("setup-pybevy.R")

# Test high-level simulation functionality
test_that("run_bevy_app basic functionality works", {
  params <- list(
    n_hosts = 10L,
    max_days = 30L,
    incidence_rate = 0.05,
    log10_dose = 5.0
  )
  
  result <- pb$run_bevy_app(params)
  
  # Check output structure
  expect_true(is.array(result))
  expect_equal(dim(result), c(10, 31, 2))  # [host, day, metric] - includes day 0
  
  # Check data types
  expect_true(is.numeric(result))
  
  # Check that immunity values are reasonable
  immunity_data <- result[, , 1]  # Immunity is metric 1
  expect_true(all(immunity_data >= 0.0))
  expect_true(all(immunity_data < 1e6))  # Very generous upper bound
  
  # Check that viral shedding values are reasonable
  shedding_data <- result[, , 2]  # Viral shedding is metric 2
  expect_true(all(shedding_data >= 0.0))
})

test_that("run_bevy_app works with different population sizes", {
  n_hosts_list <- c(1L, 5L, 20L)
  
  for (n_hosts in n_hosts_list) {
    params <- list(
      n_hosts = n_hosts,
      max_days = 10L,
      incidence_rate = 0.1,
      log10_dose = 4.5
    )
    
    result <- pb$run_bevy_app(params)
    expect_equal(dim(result)[1], n_hosts)
  }
})

test_that("run_bevy_app works with different simulation lengths", {
  max_days_list <- c(1L, 10L, 50L)
  
  for (max_days in max_days_list) {
    params <- list(
      n_hosts = 5L,
      max_days = max_days,
      incidence_rate = 0.05,
      log10_dose = 5.0
    )
    
    result <- pb$run_bevy_app(params)
    expect_equal(dim(result)[2], max_days + 1)  # Includes day 0
  }
})

test_that("run_bevy_app works with different incidence rates", {
  incidence_rate_list <- c(0.0, 0.05, 0.2)
  
  for (incidence_rate in incidence_rate_list) {
    params <- list(
      n_hosts = 10L,
      max_days = 20L,
      incidence_rate = incidence_rate,
      log10_dose = 5.0
    )
    
    result <- pb$run_bevy_app(params)
    
    # Higher incidence should generally lead to more infections
    # (though this is stochastic so we just check basic properties)
    shedding_data <- result[, , 2]
    if (incidence_rate > 0) {
      # Should see some viral shedding with positive incidence (or very low rate)
      expect_true(any(shedding_data > 0) || incidence_rate < 0.01)
    }
  }
})

test_that("run_bevy_app works with different dose levels", {
  log10_dose_list <- c(3.0, 5.0, 7.0)
  
  for (log10_dose in log10_dose_list) {
    params <- list(
      n_hosts = 10L,
      max_days = 15L,
      incidence_rate = 0.1,
      log10_dose = log10_dose
    )
    
    result <- pb$run_bevy_app(params)
    
    # Higher doses should generally lead to more infections
    # (though this is stochastic so we just check basic properties)
    shedding_data <- result[, , 2]
    expect_true(all(shedding_data >= 0.0))
  }
})

# Test three-layer API integration
test_that("Parameter to state integration works", {
  default_params <- get_default_params()
  
  # Create immunity with specific parameters
  immunity <- pb$Immunity$with_values(5.0, 5.0, 0.0, NULL)
  
  # Modify transmission parameters
  original_alpha <- default_params$p_transmit$alpha
  default_params$p_transmit$alpha <- 0.8  # High transmission
  
  prob_high <- immunity$calculate_infection_probability(
    dose = 1000.0,
    strain = pb$InfectionStrain$WPV,
    serotype = pb$InfectionSerotype$Type2,
    params = default_params
  )
  
  # Reset to lower transmission
  default_params$p_transmit$alpha <- 0.2  # Low transmission
  
  prob_low <- immunity$calculate_infection_probability(
    dose = 1000.0,
    strain = pb$InfectionStrain$WPV,
    serotype = pb$InfectionSerotype$Type2,
    params = default_params
  )
  
  # Higher alpha should give higher infection probability
  expect_true(prob_high >= prob_low)
  
  # Reset original value
  default_params$p_transmit$alpha <- original_alpha
})

test_that("State to function integration works", {
  default_params <- get_default_params()
  shed_duration_params <- get_shed_duration_params()
  
  # Create host and immunity
  host <- pb$Host(birth_sim_day = -365L * 10L)  # 10 years old
  immunity <- pb$Immunity$with_values(3.0, 3.0, 0.0, NULL)
  
  # Calculate infection probability
  infection_prob <- immunity$calculate_infection_probability(
    dose = 2000.0,
    strain = pb$InfectionStrain$WPV,
    serotype = pb$InfectionSerotype$Type1,
    params = default_params
  )
  
  # If infected, create infection state
  if (infection_prob > 0.1) {  # Simulate infection
    shed_duration <- immunity$calculate_shed_duration(shed_duration_params)
    
    infection <- pb$Infection(
      shed_duration = shed_duration,
      viral_shedding = 1000.0,
      strain = pb$InfectionStrain$WPV,
      serotype = pb$InfectionSerotype$Type1
    )
    
    # Test function calculations with state data
    viral_shedding <- immunity$calculate_viral_shedding(
      10.0, infection$shed_duration, default_params
    )
    
    should_clear <- infection$should_clear_infection(
      days_since_infection = infection$shed_duration + 5.0
    )
    
    expect_true(is.numeric(viral_shedding))
    expect_true(viral_shedding >= 0.0)
    expect_true(should_clear)  # Should clear after shed duration
  }
})

test_that("Full disease progression workflow works", {
  default_params <- get_default_params()
  immunity_waning_params <- get_immunity_waning_params()
  shed_duration_params <- get_shed_duration_params()
  
  # Initial setup
  host <- pb$Host(birth_sim_day = -365L * 15L)  # 15 years old
  immunity <- pb$Immunity$with_values(2.0, 2.0, 0.0, NULL)
  infection <- NULL
  
  simulation_days <- 100L
  dose <- 5000.0
  
  for (day in seq_len(simulation_days)) {
    # Daily exposure chance
    if (is.null(infection) && (day %% 20L == 0L)) {  # Exposure every 20 days
      infection_prob <- immunity$calculate_infection_probability(
        dose = dose,
        strain = pb$InfectionStrain$WPV,
        serotype = pb$InfectionSerotype$Type2,
        params = default_params
      )
      
      # Simulate stochastic infection
      if (infection_prob > 0.5) {  # Deterministic for testing
        # Update immunity state for infection
        immunity$ti_infected <- as.numeric(day)
        immunity$postchallenge_peak_immunity <- 8.0  # Boost from infection
        
        # Create infection
        shed_duration <- immunity$calculate_shed_duration(shed_duration_params)
        infection <- pb$Infection(
          shed_duration = shed_duration,
          viral_shedding = 1000.0,
          strain = pb$InfectionStrain$WPV,
          serotype = pb$InfectionSerotype$Type2
        )
      }
    }
    
    # Update infection state
    if (!is.null(infection)) {
      days_since_infection <- day - immunity$ti_infected
      
      # Calculate viral shedding
      viral_shedding <- immunity$calculate_viral_shedding(
        days_since_infection, infection$shed_duration, default_params
      )
      infection$viral_shedding <- viral_shedding
      
      # Check for clearance
      if (infection$should_clear_infection(days_since_infection)) {
        infection <- NULL
      }
    }
    
    # Update immunity (waning)
    if (!is.null(immunity$ti_infected)) {
      days_since_infection <- day - immunity$ti_infected
      if (days_since_infection > 30L) {  # Start waning after 30 days
        immunity$calculate_waning(days_since_infection, immunity_waning_params)
      }
    }
  }
  
  # Verify final state makes sense
  expect_true(is.numeric(immunity$current_immunity))
  expect_true(immunity$current_immunity >= 0.0)
  
  if (!is.null(immunity$ti_infected)) {
    expect_true(immunity$ti_infected >= 0.0)
    expect_true(immunity$ti_infected <= simulation_days)  # Allow infection on last day
  }
})

# Test error handling and edge cases
test_that("run_bevy_app handles invalid parameters", {
  # Missing required parameter - should error
  expect_error(pb$run_bevy_app(list(n_hosts = 10L)))
  
  # Invalid parameter types - should error
  expect_error(pb$run_bevy_app(list(
    n_hosts = -1L,  # Negative hosts
    max_days = 30L,
    incidence_rate = 0.05,
    log10_dose = 5.0
  )))
})

test_that("Calculations work with extreme parameter values", {
  default_params <- get_default_params()
  
  immunity <- pb$Immunity$with_values(0.1, 0.1, 0.0, NULL)  # Very low immunity
  
  # Very high dose
  prob_high_dose <- immunity$calculate_infection_probability(
    dose = 1000000.0,
    strain = pb$InfectionStrain$WPV,
    serotype = pb$InfectionSerotype$Type1,
    params = default_params
  )
  expect_in_range(prob_high_dose, 0.0, 1.0, "high dose probability")
  
  # Very low dose
  prob_low_dose <- immunity$calculate_infection_probability(
    dose = 1.0,
    strain = pb$InfectionStrain$WPV,
    serotype = pb$InfectionSerotype$Type1,
    params = default_params
  )
  expect_in_range(prob_low_dose, 0.0, 1.0, "low dose probability")
  expect_true(prob_high_dose >= prob_low_dose)
})