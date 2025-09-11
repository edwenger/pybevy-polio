# Tests for Parameter Layer - Disease parameter classes and modification
# R equivalent of test_parameter_layer.py

source("setup-pybevy.R")

# Test ImmunityWaningParams class
test_that("ImmunityWaningParams default values are reasonable", {
  immunity_waning_params <- get_immunity_waning_params()
  
  expect_true(is.numeric(immunity_waning_params$rate))
  expect_in_range(immunity_waning_params$rate, 0.0, 2.0, "waning rate")
})

test_that("ImmunityWaningParams parameter modification works", {
  immunity_waning_params <- get_immunity_waning_params()
  
  original_rate <- immunity_waning_params$rate
  immunity_waning_params$rate <- 0.95  # Use different value than default 0.87
  
  expect_equal(immunity_waning_params$rate, 0.95, tolerance = 1e-6)
  expect_false(immunity_waning_params$rate == original_rate)
})

# Test ThetaNabsParams class
test_that("ThetaNabsParams default values are reasonable", {
  theta_nabs_params <- get_theta_nabs_params()
  
  expect_true(is.numeric(theta_nabs_params$a))
  expect_true(is.numeric(theta_nabs_params$b))
  expect_true(is.numeric(theta_nabs_params$c))
  expect_true(is.numeric(theta_nabs_params$d))
})

test_that("ThetaNabsParams parameter modification works", {
  theta_nabs_params <- get_theta_nabs_params()
  
  theta_nabs_params$a <- 4.82
  theta_nabs_params$b <- -0.30
  theta_nabs_params$c <- 3.31
  theta_nabs_params$d <- -0.32
  
  expect_equal(theta_nabs_params$a, 4.82, tolerance = 1e-6)
  expect_equal(theta_nabs_params$b, -0.30, tolerance = 1e-6)
  expect_equal(theta_nabs_params$c, 3.31, tolerance = 1e-6)
  expect_equal(theta_nabs_params$d, -0.32, tolerance = 1e-6)
})

# Test ViralSheddingParams class
test_that("ViralSheddingParams default values are reasonable", {
  viral_shedding_params <- get_viral_shedding_params()
  
  expect_true(is.numeric(viral_shedding_params$eta))
  expect_true(is.numeric(viral_shedding_params$v))
  expect_true(is.numeric(viral_shedding_params$epsilon))
  expect_true(viral_shedding_params$eta > 0)
  expect_true(viral_shedding_params$v > 0)
})

test_that("ViralSheddingParams parameter modification works", {
  viral_shedding_params <- get_viral_shedding_params()
  
  viral_shedding_params$eta <- 1.65
  viral_shedding_params$v <- 0.17
  viral_shedding_params$epsilon <- 0.32
  
  expect_equal(viral_shedding_params$eta, 1.65)
  expect_equal(viral_shedding_params$v, 0.17)
  expect_equal(viral_shedding_params$epsilon, 0.32)
})

# Test PeakCid50Params class
test_that("PeakCid50Params default values are reasonable", {
  peak_cid50_params <- get_peak_cid50_params()
  
  expect_true(is.numeric(peak_cid50_params$k))
  expect_true(is.numeric(peak_cid50_params$smax))
  expect_true(is.numeric(peak_cid50_params$smin))
  expect_true(is.numeric(peak_cid50_params$tau))
  expect_true(peak_cid50_params$smax > peak_cid50_params$smin)
})

test_that("PeakCid50Params parameter modification works", {
  peak_cid50_params <- get_peak_cid50_params()
  
  peak_cid50_params$k <- 0.056
  peak_cid50_params$smax <- 6.7
  peak_cid50_params$smin <- 4.3
  peak_cid50_params$tau <- 12.0
  
  expect_equal(peak_cid50_params$k, 0.056, tolerance = 1e-6)
  expect_equal(peak_cid50_params$smax, 6.7, tolerance = 1e-6)
  expect_equal(peak_cid50_params$smin, 4.3, tolerance = 1e-6)
  expect_equal(peak_cid50_params$tau, 12.0, tolerance = 1e-6)
})

# Test ProbTransmitParams class  
test_that("ProbTransmitParams default values are reasonable", {
  prob_transmit_params <- get_prob_transmit_params()
  
  expect_true(is.numeric(prob_transmit_params$alpha))
  expect_true(is.numeric(prob_transmit_params$gamma))
  expect_in_range(prob_transmit_params$alpha, 0.0, 1.0, "alpha")
  expect_in_range(prob_transmit_params$gamma, 0.0, 1.0, "gamma")
})

test_that("ProbTransmitParams parameter modification works", {
  prob_transmit_params <- get_prob_transmit_params()
  
  prob_transmit_params$alpha <- 0.44
  prob_transmit_params$gamma <- 0.46
  
  expect_equal(prob_transmit_params$alpha, 0.44)
  expect_equal(prob_transmit_params$gamma, 0.46)
})

# Test ShedDurationParams class
test_that("ShedDurationParams default values are reasonable", {
  shed_duration_params <- get_shed_duration_params()
  
  expect_true(is.numeric(shed_duration_params$u))
  expect_true(is.numeric(shed_duration_params$delta))
  expect_true(is.numeric(shed_duration_params$sigma))
  expect_true(shed_duration_params$u > 0)
})

test_that("ShedDurationParams parameter modification works", {
  shed_duration_params <- get_shed_duration_params()
  
  shed_duration_params$u <- 43.0
  shed_duration_params$delta <- 1.16
  shed_duration_params$sigma <- 1.69
  
  expect_equal(shed_duration_params$u, 43.0, tolerance = 1e-6)
  expect_equal(shed_duration_params$delta, 1.16, tolerance = 1e-6)
  expect_equal(shed_duration_params$sigma, 1.69, tolerance = 1e-6)
})

# Test StrainParams class
test_that("StrainParams default values are reasonable", {
  strain_params <- get_strain_params()
  
  expect_true(is.numeric(strain_params$sabin_scale_parameter))
  expect_true(is.numeric(strain_params$strain_take_modifier))
  expect_true(strain_params$strain_take_modifier > 0)
})

test_that("StrainParams parameter modification works", {
  strain_params <- get_strain_params()
  shed_duration_params <- get_shed_duration_params()
  
  strain_params$sabin_scale_parameter <- 2.3
  strain_params$strain_take_modifier <- 1.0
  strain_params$shed_duration <- shed_duration_params
  
  expect_equal(strain_params$sabin_scale_parameter, 2.3, tolerance = 1e-6)
  expect_equal(strain_params$strain_take_modifier, 1.0, tolerance = 1e-6)
  expect_equal(strain_params$shed_duration, shed_duration_params)
})

# Test main Params struct
test_that("Params default construction works", {
  default_params <- get_default_params()
  
  expect_true(!is.null(default_params))
  expect_true(!is.null(default_params$immunity_waning))
  expect_true(!is.null(default_params$theta_nabs))
  expect_true(!is.null(default_params$viral_shedding))
  expect_true(!is.null(default_params$peak_cid50))
  expect_true(!is.null(default_params$p_transmit))
})

test_that("Params parameter assignment works", {
  default_params <- get_default_params()
  immunity_waning_params <- get_immunity_waning_params()
  theta_nabs_params <- get_theta_nabs_params()
  viral_shedding_params <- get_viral_shedding_params()
  
  default_params$immunity_waning <- immunity_waning_params
  default_params$theta_nabs <- theta_nabs_params
  default_params$viral_shedding <- viral_shedding_params
  
  expect_equal(default_params$immunity_waning, immunity_waning_params)
  expect_equal(default_params$theta_nabs, theta_nabs_params)
  expect_equal(default_params$viral_shedding, viral_shedding_params)
})

test_that("Params nested parameter access works", {
  default_params <- get_default_params()
  
  # Modify nested parameter
  original_rate <- default_params$immunity_waning$rate
  default_params$immunity_waning$rate <- 0.99
  
  expect_equal(default_params$immunity_waning$rate, 0.99)
  expect_false(default_params$immunity_waning$rate == original_rate)
})