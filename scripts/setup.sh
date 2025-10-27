#!/bin/bash

# SenseTop Setup Script for Raspberry Pi OS
# This script installs dependencies and sets up SenseTop on a Raspberry Pi

set -e

echo "======================================"
echo "SenseTop Setup Script"
echo "======================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -qi "raspberry" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This does not appear to be running on a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Update package lists
echo ""
echo "Updating package lists..."
sudo apt-get update

# Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-numpy \
    libi2c-dev \
    i2c-tools \
    build-essential \
    git

# Enable I2C if not already enabled
echo ""
echo "Checking I2C status..."
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt 2>/dev/null && \
   ! grep -q "^dtparam=i2c_arm=on" /boot/firmware/config.txt 2>/dev/null; then
    echo "I2C is not enabled. Attempting to enable..."
    if [ -f /boot/firmware/config.txt ]; then
        sudo bash -c 'echo "dtparam=i2c_arm=on" >> /boot/firmware/config.txt'
    elif [ -f /boot/config.txt ]; then
        sudo bash -c 'echo "dtparam=i2c_arm=on" >> /boot/config.txt'
    fi
    echo "I2C has been enabled. Please reboot for changes to take effect."
else
    echo "I2C is already enabled"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install --upgrade pip setuptools wheel

# Install in development mode if in git repo
if [ -d .git ]; then
    echo ""
    echo "Installing SenseTop in development mode..."
    pip3 install -e ".[dev]"
else
    echo ""
    echo "Installing SenseTop..."
    pip3 install -e .
fi

echo ""
echo "======================================"
echo "Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Test I2C connection: i2cdetect -y 1"
echo "2. Run tests: make test"
echo "3. Start application: python -m sensetop"
echo ""
