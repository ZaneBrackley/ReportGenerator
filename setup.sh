#!/bin/bash

# Remove any previous virtual environment
rm -rf venv

# Create a new virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Ensure pip is installed (in case it's missing)
python -m ensurepip --upgrade

# Install required packages from requirements.txt
pip install -r requirements.txt

# Inform the user
echo "Virtual environment created and activated."
echo "All requirements installed."
