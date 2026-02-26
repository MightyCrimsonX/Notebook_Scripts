#!/usr/bin/env python3
"""
install_forge_classic.py
Script standalone que reproduce todo el setup de tu celda Jupyter
(enlaces, dependencias, extensiones, wheel de SageAttention, etc.)
"""

import os
import subprocess
import shutil
from pathlib import Path

ROOT = Path("/teamspace/studios/this_studio").expanduser().resolve()
FORGE_DIR = ROOT / "sd-webui-forge-classic"
EXT_DIR   = FORGE_DIR / "extensions"

# ---------- helpers ----------
def run(cmd: str, cwd: Path | None = None, capture: bool = False) -> None:
    """Ejecuta un comando shell y muestra salida en tiempo real."""
    print(f"+ {cmd}")
    subprocess.run(cmd, shell=True, check=False, cwd=cwd)

def clone(repo: str, depth: int | None = None) -> None:
    """Clona un repo en EXT_DIR."""
    cmd = f"git clone {repo}"
    if depth:
        cmd = f"git clone --depth {depth} {repo}"
    run(cmd, cwd=EXT_DIR)

# ---------- main ----------
def main() -> None:
    os.chdir(ROOT)

    # 1.  download_magic.py & temp_dir.py
    run("wget -q https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/scripts/download_magic.py")
    run("wget -q https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/scripts/temp_dir.py")

    # 2.  clonar forge-classic si no existe
    if not FORGE_DIR.exists():
        run("git clone https://github.com/MightyCrimsonX/sd-webui-forge-classic.git")

    # 3.  PyTorch + extras
    run("uv pip install torch==2.9.1 torchvision==0.24.1 xformers==0.0.33.post2 triton==3.5.1 "
        "--index-url https://download.pytorch.org/whl/cu128 --no-progress")

    # 4.  ui-config.json y styles.csv
    run("wget -q --show-progress https://huggingface.co/datasets/WhiteAiZ/sd-webui-forge-classic/resolve/main/ui-config.json "
        "-O sd-webui-forge-classic/ui-config.json")
    run("wget -q --show-progress https://huggingface.co/datasets/WhiteAiZ/sd-webui-forge-classic/resolve/main/styles.csv "
        "-O sd-webui-forge-classic/styles.csv")

    # 5.  extensiones
    EXT_DIR.mkdir(exist_ok=True)
    repos = [
        "https://github.com/pamparamm/sd-perturbed-attention",
        "https://github.com/gutris1/sd-image-encryption",
        "https://github.com/yankooliveira/sd-webui-photopea-embed.git",
        "https://github.com/gutris1/sd-hub",
        "https://github.com/Haoming02/sd-forge-couple",
        "https://github.com/gutris1/sd-civitai-browser-plus-plus",
        "https://github.com/AlUlkesh/stable-diffusion-webui-images-browser",
        "https://github.com/DominikDoom/a1111-sd-webui-tagcomplete",
        "https://github.com/Bing-su/adetailer",
        "https://github.com/NoCrypt/sd-fast-pnginfo",
        "https://github.com/viyiviyi/stable-diffusion-webui-zoomimage",
        "https://github.com/gutris1/sd-simple-dimension-preset",
    ]
    for r in repos:
        clone(r, depth=1)

    # 6.  sistema + aria2
    run("sudo apt update -qq")
    run("sudo apt install aria2 -q")

    # 7.  paquetes extra
    run("uv pip install gdown clip gradio==3.41.2 ultralytics==8.3.216 insightface --no-progress")

    # 8.  SageAttention wheel
    wheel = "sageattention-2.1.2-cp312-cp312-linux_x86_64.whl"
    run(f"wget -q --show-progress https://huggingface.co/datasets/WhiteAiZ/T4_SageAttention2_For_Google_Colab/resolve/main/python%203.12/{wheel}")
    run(f"uv pip install {wheel}")
    Path(wheel).unlink(missing_ok=True)

    # 9.  limpieza
    run("rm -rf ~/.cache")

    # 10. on_start.sh (opcional)
    lightning_studio = ROOT / ".lightning_studio"
    lightning_studio.mkdir(exist_ok=True)
    run("wget -q https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/scripts/on_start.sh -O .lightning_studio/on_start.sh")

    print("\n🎉 Instalación completada.")

if __name__ == "__main__":
    main()