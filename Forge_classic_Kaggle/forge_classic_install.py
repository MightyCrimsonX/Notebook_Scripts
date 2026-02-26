#!/usr/bin/env python3
"""
forge_classic_install.py
Instala WhiteRF (sd-webui-forge-classic) con extensiones y enlaces simbólicos para Kaggle.
"""

import os
import subprocess
from pathlib import Path

WORK_DIR = Path("/kaggle/working").resolve()
FORGE_DIR = WORK_DIR / "sd-webui-forge-classic"
EXT_DIR = FORGE_DIR / "extensions"

# ---------- helpers ----------
def run(cmd: str, cwd: Path | None = None, check: bool = False) -> None:
    """Ejecuta un comando shell."""
    print(f"+ {cmd}")
    subprocess.run(cmd, shell=True, check=check, cwd=cwd)

def clone(repo: str, depth: int | None = None) -> None:
    """Clona un repo en EXT_DIR."""
    cmd = "git clone"
    if depth:
        cmd += f" --depth {depth}"
    cmd += f" {repo}"
    run(cmd, cwd=EXT_DIR)

def wget(url: str, output: str | None = None, quiet: bool = False, show_progress: bool = False) -> None:
    """Descarga con wget."""
    cmd = "wget"
    if quiet:
        cmd += " -q"
    if show_progress:
        cmd += " --show-progress"
    if output:
        cmd += f" -O {output}"
    cmd += f" {url}"
    run(cmd)

# ---------- main ----------
def main() -> None:
    os.chdir(WORK_DIR)

    # 1. Clonar forge-classic
    if not FORGE_DIR.exists():
        run("git clone https://github.com/MightyCrimsonX/sd-webui-forge-classic.git")

    # 2. Descargar ui-config.json y styles.csv
    wget(
        "https://huggingface.co/datasets/WhiteAiZ/sd-webui-forge-classic/resolve/main/ui-config.json",
        output=str(FORGE_DIR / "ui-config.json"),
        quiet=True,
        show_progress=True
    )
    wget(
        "https://huggingface.co/datasets/WhiteAiZ/sd-webui-forge-classic/resolve/main/styles.csv",
        output=str(FORGE_DIR / "styles.csv"),
        quiet=True,
        show_progress=True
    )

    # 3. Extensiones
    EXT_DIR.mkdir(parents=True, exist_ok=True)
    
    repos = [
        ("https://github.com/pamparamm/sd-perturbed-attention", None),
        ("https://github.com/gutris1/sd-image-encryption", None),
        ("https://github.com/yankooliveira/sd-webui-photopea-embed.git", None),
        ("https://github.com/gutris1/sd-hub", 1),
        ("https://github.com/uorufu/stable-diffusion-webui-wildcards-adetailer.git", 1),
        ("https://github.com/Haoming02/sd-forge-couple", 1),
        ("https://github.com/etherealxx/batchlinks-webui", None),
        ("https://github.com/gutris1/sd-civitai-browser-plus-plus", None),
        ("https://github.com/AlUlkesh/stable-diffusion-webui-images-browser", 1),
        ("https://github.com/DominikDoom/a1111-sd-webui-tagcomplete", 1),
        ("https://github.com/Anzhc/aadetailer-reforge.git", 1),
        ("https://github.com/NoCrypt/sd-fast-pnginfo", 1),
        ("https://github.com/viyiviyi/stable-diffusion-webui-zoomimage", 1),
        ("https://github.com/gutris1/sd-simple-dimension-preset", 1),
    ]
    
    for repo, depth in repos:
        clone(repo, depth=depth)

    # 4. Sistema + aria2
    run("sudo apt update -qq")
    run("sudo apt install aria2 -q")

    # 5. gdown
    run("pip install gdown -q")

    # 6. Limpiar output y mostrar mensaje
    os.system("clear" if os.name != "nt" else "cls")
    print("\n" + "=" * 50)
    print("🎉 Instalación completada")
    print("=" * 50 + "\n")

    # 7. Enlaces simbólicos
    # tmp
    run("rm -rf /kaggle/working/tmp ~/tmp")
    run("ln -vs /tmp ~/tmp")
    
    # models
    run("rm -rf /kaggle/working/sd-webui-forge-classic/models/Stable-diffusion/tmp_models")
    run("mkdir -p /tmp/models")
    run("ln -vs /tmp/models /kaggle/working/sd-webui-forge-classic/models/Stable-diffusion/tmp_models")
    
    # lora
    run("rm -rf /kaggle/working/sd-webui-forge-classic/models/Lora/tmp_lora")
    run("mkdir -p /tmp/lora")
    run("ln -vs /tmp/lora /kaggle/working/sd-webui-forge-classic/models/Lora/tmp_lora")

    print("\n✅ Enlaces simbólicos creados.")

if __name__ == "__main__":
    main()