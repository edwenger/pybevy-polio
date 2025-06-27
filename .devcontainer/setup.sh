#!/bin/bash

# Setup script for PyBevy Polio development environment

set -e

# echo "📦 Installing Claude Code..."
# npm install -g @anthropic-ai/claude-code

# echo "📦 Installing Bevy Linux dependencies..."
# sudo apt-get update
# sudo apt-get install -y g++ pkg-config libx11-dev libasound2-dev libudev-dev libxkbcommon-x11-0

echo "🦀 Setting up Rust environment..."
# Ensure cargo is in PATH
# source ~/.cargo/env

echo "🔧 Building the Rust project..."
# Build the Rust project
cargo build --lib

echo "🐍 Setting up Python environment..."
# Install maturin for Python-Rust bindings
# pip install --upgrade pip
# pip install maturin

echo "📦 Installing Python dependencies..."
# Install the project with all optional dependencies
pip install -e .[full]

echo "🏗️ Building Python bindings..."
# Build and install the Python package
# maturin develop --release

echo "✅ Development environment setup complete!"
echo "📋 Available commands:"
echo "  - cd app && cargo run        # Run interactive Bevy visualization"
echo "  - python pybevy/test.py      # Test Python bindings"
echo "  - maturin develop --release  # Rebuild Python bindings"
echo ""
echo "🎯 Try running: python pybevy/test.py"