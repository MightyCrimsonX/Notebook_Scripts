#!/bin/bash

# This script runs every time your Studio starts, from your home directory.
echo "Preparando carpetas temporales..."
python ~/symb.py

# Logs from previous runs can be found in ~/.lightning_studio/logs/

# aseg\u00farate de que la ruta sea correcta desde la ra\u00edz de tu studio

# LD_PRELOAD se establece para esta \u00fanica ejecuci\u00f3n, y el '&' lo env\u00eda al fondo.


# List files under fast_load that need to load quickly on start (e.g. model checkpoints).
#
# ! fast_load
# <your file here>

# Add your startup commands below.
#
# Example: streamlit run my_app.py
# Example: gradio my_app.py
