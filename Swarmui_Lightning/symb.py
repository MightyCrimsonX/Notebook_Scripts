#!/usr/bin/env python3
# swarmui_tmp_links.py  –  solo enlaza carpetas temporales de SwarmUI
import subprocess
from pathlib import Path

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