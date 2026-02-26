#!/bin/bash

# This script runs every time your Studio starts, from your home directory.
echo "Preparando carpetas temporales..."
python ~/temp_dir.py

# Logs from previous runs can be found in ~/.lightning_studio/logs/

# List files under fast_load that need to load quickly on start (e.g. model checkpoints).
#
# ! fast_load
# <your file here>

# Add your startup commands below.
#
# Example: streamlit run my_app.py
# Example: gradio my_app.py
