# PyBevy-Polio Unit Tests

Comprehensive unit test suite covering all three API layers with consistent Python/R implementations.

## Python Tests

**Prerequisites:**
```bash
pip install pytest
maturin develop --release
```

**Run tests:**
```bash
# All tests
python -m pytest tests/ -v

# By layer
python -m pytest tests/test_parameter_layer.py -v
python -m pytest tests/test_state_layer.py -v  
python -m pytest tests/test_function_layer.py -v
python -m pytest tests/test_integration.py -v

# Quick summary
python -m pytest tests/ --tb=no -q
```

## R Tests

**Prerequisites:**
```r
install.packages(c('reticulate', 'testthat'))
```
```bash
maturin develop --release  # Rebuild Python bindings
```

**Run tests:**
```bash
# All tests
Rscript tests/testthat.R

# Individual test files (from R console)
library(testthat)
test_file("tests/testthat/test-parameter-layer.R")
test_file("tests/testthat/test-state-layer.R")
test_file("tests/testthat/test-function-layer.R") 
test_file("tests/testthat/test-integration.R")
```

## Test Coverage

- **Parameter Layer**: 17 Python + ~47 R tests - All parameter classes
- **State Layer**: 24 Python + ~46 R tests - Host, Immunity, Infection components
- **Function Layer**: 34 Python + ~81 R tests - All calculation methods  
- **Integration Layer**: 18 Python + ~30 R tests - Cross-layer workflows + simulations

**Total: 93 Python + ~204 R tests (100% passing)**