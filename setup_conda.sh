#!/bin/bash

# Install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda

# Initialize Conda
export PATH="$HOME/miniconda/bin:$PATH"
source $HOME/miniconda/etc/profile.d/conda.sh
conda init bash

# Update or create the environment from the environment.yml file
conda env update --file environment.yml

# Activate the environment
source activate myenv

# # Install additional Python packages from requirements.txt
# pip install -r requirements.txt