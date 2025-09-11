# R Integration Setup Guide

## Prerequisites

### 1. Build PyBevy Package
First, ensure the PyBevy Python package is built and available:

```bash
# From the project root directory
maturin develop --release

# Test that it works
python -c "import pybevy; print('PyBevy available')"
```

### 2. Install Required R Packages
```r
# In R console or RStudio
install.packages(c("reticulate", "ggplot2", "dplyr", "tidyr"))
```

### 3. Configure Python Environment
reticulate needs to find the correct Python environment. You have several options:

#### Option A: Let reticulate auto-detect
```r
library(reticulate)
py_config()  # Shows detected Python configuration
```

#### Option B: Specify Python explicitly
```r
library(reticulate)
use_python("/path/to/your/python", required = TRUE)
# Example paths:
# use_python("/usr/bin/python3", required = TRUE)
# use_python("~/.venv/bin/python", required = TRUE) 
# use_python("/opt/homebrew/bin/python3", required = TRUE)
```

#### Option C: Use a virtual environment
```r
library(reticulate)
use_virtualenv("~/.venv", required = TRUE)
# or
use_condaenv("your-conda-env", required = TRUE)
```

## Execution Options

### Option 1: Command Line Execution
```bash
Rscript R/demo.R
```

### Option 2: Interactive RStudio
1. Open RStudio
2. Open `R/demo.R`
3. Run sections interactively or source the entire file
4. Plots will appear in the Plots pane

### Option 3: R Console
```r
# In R console
source("R/demo.R")
```

## Troubleshooting

### Common Issues:

1. **"Error: Python module pybevy was not found"**
   - Ensure maturin develop was successful
   - Check Python path with `py_config()`
   - Try specifying Python path explicitly

2. **"reticulate not found"**
   - Install: `install.packages("reticulate")`

3. **Python import errors**
   - Verify PyBevy works in pure Python first
   - Check virtual environment activation
   - Use `py_config()` to debug Python detection

### Verification Steps:
```r
library(reticulate)
py_config()
py_run_string("import pybevy; print('Success!')")
```

## Expected Output
The R script will produce:
- Console output showing parameter analysis
- Population simulation results  
- Dose-response analysis
- Batch processing statistics
- Summary of all three API layers working correctly