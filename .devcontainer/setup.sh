#!/bin/bash

# Setup script for PyBevy Polio development environment

set -e

echo "🦀 Setting up Rust environment..."
# Ensure cargo is in PATH
source ~/.cargo/env

echo "🐍 Setting up Python environment..."
# Install maturin for Python-Rust bindings
pip install --upgrade pip
pip install maturin

echo "📦 Installing Python dependencies..."
# Install the project with all optional dependencies
pip install -e .[full]

echo "🔧 Building the Rust project..."
# Build the Rust project
cargo build

echo "🏗️ Building Python bindings..."
# Build and install the Python package
maturin develop --release

echo "✅ Development environment setup complete!"
echo "📋 Available commands:"
echo "  - cargo run          # Run interactive Bevy visualization"
echo "  - python test.py     # Test Python bindings"
echo "  - maturin develop    # Rebuild Python bindings"
echo ""
echo "🎯 Try running: python test.py"