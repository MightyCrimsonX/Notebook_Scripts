#!/usr/bin/env python3
# temp_dir.py  –  enlaza carpetas temporales de ComfyUI a /tmp
import subprocess
import os
from pathlib import Path
HOME = "/teamspace/studios/this_studio"
TMP_MODELS= "/tmp/models"
TMP_LORAS = "/tmp/lora"
TMP_VAE = "/tmp/vae"
TMP_CONTROLNET = "/tmp/controlnet"
TMP_DIFFUSION = "/tmp/diffusion_models"
TMP_TEXT_ENCODERS = "/tmp/text_encoders"
TMP_UNET = "/tmp/unet"
TMP_KGEN = "/tmp/kgen"
TMP_CONTROLNET = "/tmp/controlnet"

def _run(cmd: str) -> None:
    print(f"+ {cmd}")
    subprocess.run(cmd, shell=True, check=False)

def enlaces_tmp_comfy() -> None:
    """Crea enlaces simbólicos para que ComfyUI use /tmp y libere espacio en disco."""
    base = Path("/teamspace/studios/this_studio")
    cmds = [
        "rm -rf /teamspace/studios/this_studio/tmp ~/tmp",
        "ln -vs /tmp ~/tmp",
        "rm -rf /teamspace/studios/this_studio/ComfyUI/models/checkpoints/tmp_models",
        "mkdir -p /tmp/models",
        "ln -vs /tmp/models /teamspace/studios/this_studio/ComfyUI/models/checkpoints/tmp_models",
        "rm -rf /teamspace/studios/this_studio/ComfyUI/models/loras/tmp_lora",
        "mkdir -p /tmp/lora",
        "ln -vs /tmp/lora /teamspace/studios/this_studio/ComfyUI/models/loras/tmp_lora",
        "rm -rf /teamspace/studios/this_studio/ComfyUI/models/diffusion_models",
        "mkdir -p /tmp/diffusion_models",
        "ln -vs /tmp/diffusion_models /teamspace/studios/this_studio/ComfyUI/models/diffusion_models",
        "rm -rf /teamspace/studios/this_studio/ComfyUI/models/text_encoders",
        "mkdir -p /tmp/text_encoders",
        "ln -vs /tmp/text_encoders /teamspace/studios/this_studio/ComfyUI/models/text_encoders",
        "rm -rf /teamspace/studios/this_studio/ComfyUI/models/unet",
        "mkdir -p /tmp/unet",
        "ln -vs /tmp/unet /teamspace/studios/this_studio/ComfyUI/models/unet",
        "rm -rf /teamspace/studios/this_studio/ComfyUI/models/controlnet",
        "mkdir -p /tmp/controlnet",
        "ln -vs /tmp/controlnet /teamspace/studios/this_studio/ComfyUI/models/controlnet",
        "rm -rf /teamspace/studios/this_studio/ComfyUI/models/kgen",
        "mkdir -p /tmp/kgen",
        "ln -vs /tmp/kgen /teamspace/studios/this_studio/ComfyUI/models/kgen",
    ]
    for c in cmds:
        _run(c)
    print("✅ Carpetas temporales de ComfyUI enlazadas.")

if __name__ == "__main__":
    enlaces_tmp_comfy()