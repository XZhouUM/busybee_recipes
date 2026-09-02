#!/bin/bash
set -e

# Set hooks path to the version-controlled directory
git config core.hooksPath .githooks

# Ensure the pre-push hook is executable
if [ -f .githooks/pre-push ]; then
  chmod +x .githooks/pre-push
  echo "Pre-push hook is installed and executable."
else
  echo "Warning: .githooks/pre-push not found!"
fi

# Create virtual environment to install dependencies
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
  echo "Virtual environment created."
else
  echo "Virtual environment already exists."
fi
echo "Installing Python dependencies..."
source .venv/bin/activate
pip install -r requirements.txt
echo "Dependencies installed in virtual environment."

# Option to install Antigravity CLI
read -p "[LINUX/MAC Only] Do you want to install Antigravity CLI? You can install other agents of your preference instead. (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Installing Antigravity CLI..."
  curl -fsSL https://antigravity.google/cli/install.sh | bash
else
  echo "Skipping Antigravity CLI installation."
fi

echo "Repo setup complete."
