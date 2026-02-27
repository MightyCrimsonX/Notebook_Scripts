#!/usr/bin/env python3
# swarmui_tmp_links.py  –  solo enlaza carpetas temporales de SwarmUI
import subprocess
from pathlib import Path
import os
WORK_DIR = Path("/teamspace/studios/this_studio").resolve()
SWARM_DIR = WORK_DIR / "SwarmUI"
COMFY_DIR = SWARM_DIR / "dlbackend" / "ComfyUI"
HOME = "/teamspace/studios/this_studio"
BASE_MODELS_DIR = "/teamspace/studios/this_studio/SwarmUI/Models/Stable-Diffusion"
LORA_DIR = "/teamspace/studios/this_studio/SwarmUI/Models/Lora"
VAE_DIR = "/teamspace/studios/this_studio/SwarmUI/Models/VAE"
UPSCALER_DIR = "/teamspace/studios/this_studio/SwarmUI/Models/upscale_models"
CONTROLNET_DIR = "/teamspace/studios/this_studio/SwarmUI/Models/controlnet"
DIFFUSION_DIR = "/teamspace/studios/this_studio/SwarmUI/Models/diffusion_models"
TEXT_ENCODER_DIR = "/teamspace/studios/this_studio/SwarmUI/Models/text_encoders"
UNET_DIR = "/teamspace/studios/this_studio/SwarmUI/Models/unet"
CLIP_DIR = "/teamspace/studios/this_studio/SwarmUI/Models/clip"
COMFY_EXT_DIR = "/teamspace/studios/this_studio/SwarmUI/dlbackend/ComfyUI/custom_nodes"
TMP_MODELS= "/tmp/models"
TMP_LORAS = "/tmp/lora"
TMP_VAE = "/tmp/vae"
TMP_CONTROLNET = "/tmp/controlnet"
TMP_DIFFUSION = "/tmp/diffusion_models"
TMP_TEXT_ENCODERS = "/tmp/text_encoders"

def _run(cmd: str) -> None:
    print(f"+ {cmd}")
    subprocess.run(cmd, shell=True, check=False)

def enlaces_tmp_swarm() -> None:
    """Crea enlaces simbólicos para que SwarmUI use /tmp y libere espacio en disco."""
    base = Path("/teamspace/studios/this_studio")
    cmds = [
        "mkdir -p /teamspace/studios/this_studio/SwarmUI/Models/Stable-Diffusion",
        "mkdir -p /teamspace/studios/this_studio/SwarmUI/Models/Lora",
        "rm -rf /teamspace/studios/this_studio/.cache",
        "rm -rf /teamspace/studios/this_studio/tmp ~/tmp",
        "ln -vs /tmp ~/tmp",
        "rm -rf /teamspace/studios/this_studio/SwarmUI/Models/Stable-Diffusion/tmp_models",
        "mkdir -p /tmp/models",
        "ln -vs /tmp/models /teamspace/studios/this_studio/SwarmUI/Models/Stable-Diffusion/tmp_models",
        "rm -rf /teamspace/studios/this_studio/SwarmUI/Models/Lora/tmp_lora",
        "mkdir -p /tmp/lora",
        "ln -vs /tmp/lora /teamspace/studios/this_studio/SwarmUI/Models/Lora/tmp_lora",
        "rm -rf /teamspace/studios/this_studio/SwarmUI/Models/diffusion_models",
        "mkdir -p /tmp/diffusion_models",
        "ln -vs /tmp/diffusion_models /teamspace/studios/this_studio/SwarmUI/Models/diffusion_models",
        "rm -rf /teamspace/studios/this_studio/SwarmUI/Models/text_encoders",
        "mkdir -p /tmp/text_encoders",
        "ln -vs /tmp/text_encoders /teamspace/studios/this_studio/SwarmUI/Models/text_encoders",
        "rm -rf /teamspace/studios/this_studio/SwarmUI/Models/unet",
        "mkdir -p /tmp/unet",
        "ln -vs /tmp/unet /teamspace/studios/this_studio/SwarmUI/Models/unet",
        "rm -rf /teamspace/studios/this_studio/SwarmUI/Models/controlnet",
        "mkdir -p /tmp/controlnet",
        "ln -vs /tmp/controlnet /teamspace/studios/this_studio/SwarmUI/Models/controlnet",
    ]
    for c in cmds:
        _run(c)
    print("✅ Carpetas temporales de SwarmUI enlazadas.")

if __name__ == "__main__":
    enlaces_tmp_swarm()