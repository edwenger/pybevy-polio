#!/usr/bin/env Rscript
# R Integration Example for PyBevy-Polio
# Demonstrates granular access to polio disease model via reticulate

# Load required packages with error handling
tryCatch({
  library(reticulate)
  library(ggplot2) 
  library(dplyr)
  library(tidyr)
}, error = function(e) {
  cat("❌ Missing required R packages. Please install:\n")
  cat("   install.packages(c('reticulate', 'ggplot2', 'dplyr', 'tidyr'))\n")
  stop(e)
})

cat("🐍 Python Environment Configuration\n")
cat("===================================\n")

# Show current Python configuration
py_config()

# Try to import PyBevy with helpful error messages
tryCatch({
  pb <- import("pybevy")$pybevy  # Access the nested module
  cat("✅ PyBevy successfully imported!\n")
  
  # Show available classes and functions
  available_items <- names(pb)
  cat("📦 Available classes and functions:\n")
  cat(paste("  ", available_items, collapse="\n"))
  cat("\n\n")
}, error = function(e) {
  cat("❌ Failed to import PyBevy. Troubleshooting steps:\n")
  cat("1. Build PyBevy: cd /path/to/pybevy-polio && maturin develop --release\n")
  cat("2. Test in Python: python -c 'import pybevy'\n")
  cat("3. Check Python path in R: py_config()\n")
  cat("4. Specify Python explicitly: use_python('/path/to/python', required=TRUE)\n\n")
  cat("Current Python configuration:\n")
  print(py_config())
  stop(e)
})

cat("🦠 PyBevy-Polio R Integration Example\n")
cat("====================================\n\n")

# =============================================================================
# PART 1: Parameter Layer - Disease Parameter Exploration
# =============================================================================
cat("📊 PART 1: Parameter Layer - Exploring Disease Parameters\n")
cat("---------------------------------------------------------\n")

# Create parameter objects and examine defaults
immunity_params <- pb$ImmunityWaningParams()
theta_nabs <- pb$ThetaNabsParams()
viral_shedding <- pb$ViralSheddingParams()
peak_cid50 <- pb$PeakCid50Params()
p_transmit <- pb$ProbTransmitParams()

cat(sprintf("Immunity waning rate: %.2f\n", immunity_params$rate))
cat(sprintf("Transmission alpha: %.2f, gamma: %.2f\n", p_transmit$alpha, p_transmit$gamma))
cat(sprintf("Viral shedding eta: %.2f, v: %.2f\n", viral_shedding$eta, viral_shedding$v))

# Modify parameters for sensitivity analysis
cat("\n🔧 Parameter Sensitivity Analysis:\n")
original_alpha <- p_transmit$alpha
sensitivity_results <- data.frame(
  alpha = numeric(0),
  infection_prob = numeric(0)
)

for (alpha_val in seq(0.2, 0.8, by = 0.1)) {
  p_transmit$alpha <- alpha_val
  
  # Test infection probability with standard inputs
  prob <- pb$calculate_infection_probability(
    current_immunity = 4.0,
    dose = 1000.0,
    sabin_scale = 2.3,
    alpha = alpha_val,
    gamma = 0.46,
    take_modifier = 1.0
  )
  
  sensitivity_results <- rbind(sensitivity_results, 
                              data.frame(alpha = alpha_val, infection_prob = prob))
}

cat(sprintf("Alpha sensitivity range: %.3f - %.3f (infection probability)\n", 
           min(sensitivity_results$infection_prob), 
           max(sensitivity_results$infection_prob)))

# =============================================================================
# PART 2: State Layer - Individual Host Management  
# =============================================================================
cat("\n👤 PART 2: State Layer - Individual Host Simulation\n")
cat("----------------------------------------------------\n")

# Create a small population of hosts with different ages
n_hosts <- 10
hosts <- list()
immunities <- list()

cat("Creating host population:\n")
for (i in 1:n_hosts) {
  # Hosts born at different times (age diversity)
  birth_day <- rnorm(1, mean = -365*10, sd = 365*5)  # ~10 years old ± 5 years
  hosts[[i]] <- pb$Host(birth_sim_day = birth_day)
  
  # Different immunity levels
  initial_immunity <- rlnorm(1, meanlog = log(2), sdlog = 0.5)
  immunities[[i]] <- pb$Immunity$with_values(
    prechallenge_immunity = initial_immunity,
    postchallenge_peak_immunity = 0.0,
    current_immunity = initial_immunity,
    ti_infected = NULL
  )
  
  age_years <- (-birth_day) / 365
  cat(sprintf("  Host %d: Age %.1f years, Immunity %.2f\n", 
             i, age_years, initial_immunity))
}

# Simulate disease progression over time
cat("\n🦠 Simulating disease progression:\n")
days <- seq(0, 180, by = 30)  # 6 months, monthly snapshots
immunity_data <- data.frame()

for (day in days) {
  for (i in 1:n_hosts) {
    host <- hosts[[i]]
    immunity <- immunities[[i]]
    
    # Calculate age at this time point
    age_months <- (day - host$birth_sim_day) * 12 / 365
    
    # Simulate immunity waning if infected
    current_immunity <- immunity$current_immunity
    if (!is.null(immunity$ti_infected)) {
      days_since_infection <- day - immunity$ti_infected
      if (days_since_infection > 30) {
        current_immunity <- pb$calculate_immunity_waning(
          peak_immunity = immunity$postchallenge_peak_immunity,
          days_since_infection = days_since_infection,
          waning_rate = immunity_params$rate
        )
        immunity$current_immunity <- current_immunity
      }
    }
    
    immunity_data <- rbind(immunity_data, data.frame(
      host_id = i,
      day = day,
      age_months = age_months,
      immunity = current_immunity,
      infected = !is.null(immunity$ti_infected)
    ))
  }
}

# Summary statistics
immunity_summary <- immunity_data %>%
  group_by(day) %>%
  summarise(
    mean_immunity = mean(immunity),
    median_immunity = median(immunity),
    n_infected = sum(infected),
    .groups = 'drop'
  )

cat(sprintf("Day %d: Mean immunity %.2f, %d hosts infected\n", 
           immunity_summary$day[nrow(immunity_summary)], 
           immunity_summary$mean_immunity[nrow(immunity_summary)],
           immunity_summary$n_infected[nrow(immunity_summary)]))

# =============================================================================
# PART 3: Function Layer - Dose-Response Analysis
# =============================================================================
cat("\n📈 PART 3: Function Layer - Dose-Response Modeling\n")
cat("--------------------------------------------------\n")

# Dose-response curve analysis
doses <- 10^seq(2, 7, by = 0.5)  # 100 to 10M viral particles
immunity_levels <- c(1.5, 3.0, 6.0, 12.0)  # Different immunity levels

dose_response_data <- expand.grid(
  dose = doses,
  immunity = immunity_levels,
  stringsAsFactors = FALSE
)

dose_response_data$infection_prob <- mapply(function(dose, immunity) {
  pb$calculate_infection_probability(
    current_immunity = immunity,
    dose = dose,
    sabin_scale = 2.3,
    alpha = p_transmit$alpha,
    gamma = p_transmit$gamma,
    take_modifier = 1.0
  )
}, dose_response_data$dose, dose_response_data$immunity)

# Calculate ID50 (dose for 50% infection probability) for each immunity level
id50_results <- dose_response_data %>%
  group_by(immunity) %>%
  arrange(dose) %>%
  mutate(
    diff_from_50 = abs(infection_prob - 0.5)
  ) %>%
  slice_min(diff_from_50, n = 1) %>%
  select(immunity, dose, infection_prob) %>%
  rename(id50_dose = dose, id50_prob = infection_prob)

cat("ID50 analysis (dose for ~50% infection probability):\n")
for (i in 1:nrow(id50_results)) {
  cat(sprintf("  Immunity %.1f: ID50 = %.0e (%.1f%% infection)\n", 
             id50_results$immunity[i], 
             id50_results$id50_dose[i],
             id50_results$id50_prob[i] * 100))
}

# =============================================================================
# PART 4: Batch Processing Example - Population Simulation
# =============================================================================
cat("\n🏘️  PART 4: Batch Processing - Population-Level Analysis\n")
cat("-------------------------------------------------------\n")

# Simulate a more realistic population-level scenario
set.seed(42)
pop_size <- 100
sim_days <- 365

# Generate population with realistic age structure
pop_ages <- rexp(pop_size, rate = 1/20) * 365  # Exponential age distribution
pop_hosts <- lapply(seq_len(pop_size), function(i) {
  pb$Host(birth_sim_day = -pop_ages[i])
})

# Initial immunity distribution (log-normal)
initial_immunities <- rlnorm(pop_size, meanlog = log(3), sdlog = 0.8)
pop_immunities <- lapply(seq_len(pop_size), function(i) {
  pb$Immunity$with_values(
    prechallenge_immunity = initial_immunities[i],
    postchallenge_peak_immunity = 0.0,
    current_immunity = initial_immunities[i],
    ti_infected = NULL
  )
})

# Simulate daily exposure events
daily_dose <- 1000  # Fixed dose per exposure
daily_incidence <- 0.01  # 1% daily attack rate

# Track population-level outcomes
pop_data <- data.frame()
infections_by_day <- numeric(sim_days)

cat("Running population simulation...\n")
for (day in 1:min(sim_days, 30)) {  # Limit to 30 days for demo
  daily_infections <- 0
  
  for (i in sample(seq_len(pop_size), size = round(pop_size * daily_incidence))) {
    immunity <- pop_immunities[[i]]
    
    # Calculate infection probability
    infection_prob <- pb$calculate_infection_probability(
      current_immunity = immunity$current_immunity,
      dose = daily_dose,
      sabin_scale = 2.3,
      alpha = p_transmit$alpha,
      gamma = p_transmit$gamma,
      take_modifier = 1.0
    )
    
    # Stochastic infection event
    if (runif(1) < infection_prob) {
      if (is.null(immunity$ti_infected)) {  # Not already infected
        immunity$ti_infected <- day
        daily_infections <- daily_infections + 1
      }
    }
  }
  
  infections_by_day[day] <- daily_infections
  
  if (day %% 10 == 0 || day <= 5) {
    cat(sprintf("Day %d: %d new infections\n", day, daily_infections))
  }
}

total_infected <- sum(infections_by_day[1:30])
cat(sprintf("\nTotal infections in 30 days: %d (%.1f%% of population)\n", 
           total_infected, total_infected / pop_size * 100))

# =============================================================================
# SUMMARY AND CONCLUSIONS
# =============================================================================
cat("\n✅ SUMMARY: R Integration Capabilities Demonstrated\n")
cat("==================================================\n")
cat("✓ Parameter Layer: Accessed and modified disease parameters from R\n")
cat("✓ State Layer: Created and managed individual host/immunity objects\n") 
cat("✓ Function Layer: Called pure calculation functions for dose-response analysis\n")
cat("✓ Batch Processing: Simulated population-level disease dynamics\n")
cat("\n🎯 Ready for production epidemiological modeling in R!\n")
cat("📊 All disease model calculations available via familiar R interface\n")
cat("🔗 Full interoperability between Rust performance and R analytics\n\n")