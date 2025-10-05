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

echo "Repo setup complete."
