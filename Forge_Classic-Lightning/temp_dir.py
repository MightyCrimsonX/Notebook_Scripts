#!/usr/bin/env python3
# temp_dir.py  –  enlaza carpetas temporales de ComfyUI a /tmp
import subprocess
import os
from pathlib import Path
BASE_DIR = Path("/teamspace/studios/this_studio").resolve()
FORGE_DIR = BASE_DIR / "sd-webui-forge-classic"
MODELS_DIR = FORGE_DIR / "models"
VAE_DIR = MODELS_DIR / "VAE"
EXT_DIR = FORGE_DIR / "extensions"
TMP_DIR = Path("/tmp")
TMP_MODELS = TMP_DIR / "models"
TMP_LORAS = TMP_DIR / "lora"
TMP_CONTROLNET = TMP_DIR / "controlnet"
UPSCALERS_DIR = MODELS_DIR / "ESRGAN"
ADETAILER_DIR = MODELS_DIR / "adetailer"
EMBEDDINGS_DIR = MODELS_DIR / "embeddings"

def _run(cmd: str) -> None:
    print(f"+ {cmd}")
    subprocess.run(cmd, shell=True, check=False)

def enlaces_tmp_comfy() -> None:
    """Crea enlaces simbólicos para que ComfyUI use /tmp y libere espacio en disco."""
    base = Path("/teamspace/studios/this_studio")
    cmds = [
        "rm -rf /teamspace/studios/this_studio/tmp ~/tmp",
        "ln -vs /tmp ~/tmp",
        "rm -rf /teamspace/studios/this_studio/sd-webui-forge-classic/models/Stable-diffusion/tmp_models",
        "mkdir -p /tmp/models",
        "ln -vs /tmp/models /teamspace/studios/this_studio/sd-webui-forge-classic/models/Stable-diffusion/tmp_models",
        "rm -rf /teamspace/studios/this_studio/sd-webui-forge-classic/models/Lora/tmp_lora",
        "mkdir -p /tmp/lora",
        "ln -vs /tmp/lora /teamspace/studios/this_studio/sd-webui-forge-classic/models/Lora/tmp_lora",
        "rm -rf /teamspace/studios/this_studio/sd-webui-forge-classic/models/ControlNet",
        "mkdir -p /tmp/controlnet",
        "ln -vs /tmp/controlnet /teamspace/studios/this_studio/sd-webui-forge-classic/models/ControlNet",
    ]
    for c in cmds:
        _run(c)
    print("✅ Carpetas temporales de ComfyUI enlazadas.")

if __name__ == "__main__":
    enlaces_tmp_comfy()