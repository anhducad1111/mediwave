#!/bin/bash

# Exit on error
set -e

echo "Installing mediwave dependencies for Ubuntu..."

# Update package lists
sudo apt-get update

# Install system dependencies
echo "Installing system packages..."
sudo apt-get install -y \
    python3-pip \
    python3-opencv \
    python3-dev \
    libx11-dev \
    libudev-dev \
    v4l-utils \
    python3-numpy \
    python3-opencv \
    python3-mediapipe \
    python3-venv \
    python3-pytest \
    python3-tk \
    python3-dev \
    scrot \
    python3-xlib \
    libxtst-dev \
    python3-wheel

# Enable uinput module
echo "Enabling uinput module..."
sudo modprobe uinput
# Make uinput load at boot
echo "uinput" | sudo tee /etc/modules-load.d/uinput.conf

# Add current user to input and video groups
sudo usermod -a -G input,video $USER

# Set up udev rules for input devices
echo "Setting up udev rules..."
echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/99-input.rules

# Set up video device permissions
echo "Setting up video device permissions..."
echo 'SUBSYSTEM=="video4linux", GROUP="video", MODE="0660"' | sudo tee /etc/udev/rules.d/99-camera.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Create virtual environment
echo "Setting up Python environment..."
python3 -m venv /home/ad/Desktop/WS/venv
source /home/ad/Desktop/WS/venv/bin/activate

# Install Python packages in venv
echo "Installing Python packages in virtual environment..."
pip3 install \
    opencv-python \
    mediapipe \
    numpy \
    pyautogui \
    pytest

echo "Installation complete!"
echo "Please reboot your system for all changes to take effect."
echo "After reboot, run the program with:"
echo "source /home/ad/Desktop/WS/venv/bin/activate"
echo "python3 main.py"

# To run tests:
echo ""
echo "To run tests:"
echo "source /home/ad/Desktop/WS/venv/bin/activate"
echo "pytest mediwave/test.py"
