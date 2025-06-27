# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hybrid Rust/Python project implementing a polio within-host disease model using the Bevy game engine for interactive visualization and PyO3 for Python bindings. The project demonstrates real-time epidemiological simulation with visual feedback and provides Python bindings for data analysis.

## Core Architecture

### Project Structure
- **`model/`**: Shared Rust crate containing core disease logic
- **`app/`**: Interactive Bevy application for visualization
- **`src/`**: PyO3 bindings for Python export
- **`pybevy/`**: Python package output directory

### Dual Runtime System
- **Interactive App** (`app/src/main.rs`): Bevy-based visual simulation with real-time controls and egui UI
- **Python Export** (`src/lib.rs`): Headless simulation for data analysis via PyO3

### Entity-Component System (Bevy ECS)
- **Host Component** (`model/src/core.rs`): Individual disease hosts with birth timing
- **Immunity Component** (`model/src/polio/disease.rs`): Tracks immune status over time with waning
- **Infection Component** (`model/src/polio/disease.rs`): Manages active infections and viral shedding
- **SimulationTime Resource** (`model/src/core.rs`): Global time tracking with configurable speed

### Disease Model Structure
- **Parameters** (`model/src/polio/params.rs`): Disease-specific constants and rates for different strains/serotypes
- **State Functions** (`model/src/polio/disease.rs`): Core disease progression logic with probabilistic transitions
- **Challenge System**: Dose-response infection exposure with strain-specific parameters
- **Strain Support**: WPV (Wild Poliovirus) and OPV (Oral Polio Vaccine) with Type1/Type2/Type3 serotypes

## Development Commands

### Interactive Visualization
```bash
# Run interactive Bevy app with visualization
cd app && cargo run

# Run with debug logging
cd app && RUST_LOG=info cargo run
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
python pybevy/test.py

# Enable debug logging for Python
RUST_LOG=info python pybevy/test.py

# Run Jupyter demo notebook
jupyter notebook demo.ipynb
```

### Build Commands
```bash
# Build all Rust components
cargo build --release

# Build just the model crate
cd model && cargo build --release  

# Build just the app
cd app && cargo build --release

# Clean build artifacts
cargo clean
```

## Key Integration Points

### PyO3 Export Function
The `run_bevy_app()` function in `src/lib.rs` accepts Python dictionary parameters and returns NumPy arrays. Required parameters:
- `n_hosts`: Number of simulated individuals
- `max_days`: Simulation duration
- `incidence_rate`: Daily infection probability (0.0-1.0)
- `log10_dose`: Log10 of infectious challenge dose (typically 4.0-8.0)

### Data Output Format
Returns 3D NumPy array: `[host_index, day, metric]` where metrics are:
- Index 0: Current immunity level (log scale)
- Index 1: Viral shedding amount (CID50 units)

### Simulation Systems
Both runtimes share core systems from the `model` crate:
- `step_state()`: Advances disease progression including immunity waning and infection recovery
- `challenge()`: Applies infectious exposures with dose-response probability
- Parameter-driven probabilistic transitions using `rand_distr` distributions

### Strain Parameters
The system supports multiple strain/serotype combinations with distinct parameters:
- **WPV1/2/3**: Wild poliovirus types with higher transmission
- **OPV1/2/3**: Oral vaccine strains with reduced transmission and different shedding patterns
- Each combination has specific `sabin_scale_parameter`, `strain_take_modifier`, and `shed_duration` parameters

## Interactive Visualization Features

The Bevy app (`app/src/main.rs`) provides:
- Real-time immunity visualization (blue bars) 
- Viral shedding visualization (red bars when infected)
- Interactive parameter controls via egui:
  - Simulation speed multiplier (0.5x - 30x)
  - Incidence rate slider
  - Challenge dose adjustment
- Dynamic host spawning and state tracking

## Testing and Validation

Use `pybevy/test.py` to validate Python bindings - generates time series plots and heatmaps showing immunity and viral shedding patterns across multiple hosts over time. The test script demonstrates typical usage patterns for batch simulation runs.

## File Organization

### Core Model (`model/src/`)
- `lib.rs`: Module exports
- `core.rs`: Basic ECS components (Host, SimulationTime)
- `polio/mod.rs`: Polio module organization
- `polio/params.rs`: Disease parameters with strain-specific configurations  
- `polio/disease.rs`: Disease logic, state transitions, and ECS systems

### Applications
- `app/src/main.rs`: Interactive Bevy application with visualization
- `src/lib.rs`: PyO3 Python bindings with headless simulation
- `pybevy/test.py`: Python test script demonstrating usage