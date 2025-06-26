# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hybrid Rust/Python project that implements a polio within-host disease model using the Bevy game engine for interactive visualization and PyO3 for Python bindings. The project demonstrates real-time epidemiological simulation with visual feedback.

## Core Architecture

### Dual Runtime System
- **Interactive App** (`src/app.rs`): Bevy-based visual simulation with real-time controls
- **Python Export** (`src/lib.rs`): Headless simulation for data analysis via PyO3

### Entity-Component System (Bevy ECS)
- **Host Component** (`src/core.rs`): Individual disease hosts with birth timing
- **Immunity Component** (`src/polio/disease.rs`): Tracks immune status over time  
- **Infection Component** (`src/polio/disease.rs`): Manages active infections and viral shedding
- **SimulationTime Resource** (`src/core.rs`): Global time tracking with configurable speed

### Disease Model Structure
- **Parameters** (`src/polio/params.rs`): Disease-specific constants and rates
- **State Functions** (`src/polio/disease.rs`): Core disease progression logic
- **Challenge System**: Probabilistic infection exposure with dose-response

## Development Commands

### Rust Development
```bash
# Run interactive visualization
cargo run

# Build Rust components
cargo build --release

# Enable debug logging
RUST_LOG=info cargo run
```

### Python Package Development
```bash
# Set up Python environment (first time)
python -m venv .venv
source .venv/bin/activate
pip install numpy

# Build Python package with maturin
maturin develop --release

# Test Python bindings
python test.py

# Enable debug logging for Python
RUST_LOG=info python test.py
```

## Key Integration Points

### PyO3 Export Function
The `run_bevy_app()` function in `src/lib.rs` accepts Python dictionary parameters and returns NumPy arrays. Parameters include:
- `n_hosts`: Number of simulated individuals
- `max_days`: Simulation duration
- `incidence_rate`: Daily infection probability
- `log10_dose`: Log10 of infectious challenge dose

### Data Output Format
Returns 3D NumPy array: `[host_index, day, metric]` where metrics are:
- Index 0: Current immunity level
- Index 1: Viral shedding amount

### Simulation Systems
Both runtimes share core systems:
- `step_state()`: Advances disease progression
- `challenge()`: Applies infectious exposures
- Parameter-driven probabilistic transitions

## Testing and Validation

Use `test.py` to validate Python bindings - it generates time series plots and heatmaps showing immunity and viral shedding patterns across multiple hosts over time.