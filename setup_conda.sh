#!/bin/bash

# Create or update the Conda environment
conda env update --file environment.yml

# Activate the environment
source activate myenv

# Install pip packages
pip install -r requirements.txt

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "gunicorn could not be found, installing..."
    pip install gunicorn
fi

# Run gunicorn
gunicorn app:app --bind 0.0.0.0:$PORT