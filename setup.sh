#!/bin/bash

# Remove any previous virtual environment
rm -rf venv

echo "Previous virtual environment removed."

# Create a new virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

echo "Virtual environment created and activated."

# Ensure pip is installed (in case it's missing)
python -m pip install --upgrade pip

echo "Pip updated and installed."

# Install required packages from requirements.txt
pip install -r requirements.txt

# Inform the user
echo "All requirements installed."
