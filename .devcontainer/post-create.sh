#!/bin/bash

# Post-create script for development environment setup
echo "Setting up development environment..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv /workspace/venv

# Activate virtual environment
echo "Activating virtual environment..."
source /workspace/venv/bin/activate

# Upgrade pip to latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install development tools
echo "Installing development tools..."
pip install pylint black ipykernel

# Check if requirements.txt exists and install dependencies
if [ -f "/workspace/requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r /workspace/requirements.txt
else
    echo "No requirements.txt found, skipping dependency installation"
fi

# Make sure virtual environment is activated in shell profile
echo "Configuring shell environment..."
echo 'source /workspace/venv/bin/activate' >> ~/.bashrc

echo "Development environment setup complete!"
echo "Virtual environment activated and ready to use."
