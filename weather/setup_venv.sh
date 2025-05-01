#!/bin/bash

# Set the name of the virtual environment directory and requirements file
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

# Check if the virtual environment directory is specified
if [ -z "$VENV_DIR" ]; then
  echo "Error: VENV_DIR is not specified."
  exit 1
fi

# Check if the requirements file is specified
if [ -z "$REQUIREMENTS_FILE" ]; then
  echo "Error: REQUIREMENTS_FILE is not specified."
  exit 1
fi

# Check if the virtual environment already exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"

  # Activate the virtual environment
  source "$VENV_DIR/bin/activate"

  # Install dependencies from requirements file if it exists
  if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r "$REQUIREMENTS_FILE"
  else
    echo "Error: $REQUIREMENTS_FILE not found."
    deactivate
    exit 1
  fi
else
  echo "Virtual environment already exists. Activating..."
  source "$VENV_DIR/bin/activate"
fi

