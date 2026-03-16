#!/usr/bin/env python3
"""
install_forge_neo.py
Instala sd-webui-forge-classic (rama neo) en Kaggle con Python 3.13, SageAttention y enlaces temporales.
"""

import os
import subprocess
from pathlib import Path

WORK_DIR = Path("/kaggle/working").resolve()
FORGE_DIR = WORK_DIR / "sd-webui-forge-classic"
EXT_DIR = FORGE_DIR / "extensions"

def _run(cmd: str, cwd: Path | None = None) -> None:
    """Ejecuta un comando shell."""
    print(f"+ {cmd}")
    subprocess.run(cmd, shell=True, check=False, cwd=cwd)

def clone(repo: str, depth: int | None = None, cwd: Path | None = None) -> None:
    """Clona un repositorio git."""
    cmd = "git clone"
    if depth:
        cmd += f" --depth {depth}"
    cmd += f" {repo}"
    _run(cmd, cwd=cwd)

def wget(url: str, output: str | None = None) -> None:
    """Descarga con wget."""
    cmd = "wget"
    if output:
        cmd += f" -O {output}"
    cmd += f" {url}"
    _run(cmd)

def main() -> None:
    os.chdir(WORK_DIR)

    # 1. Descargas iniciales
    wget("https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/libmimalloc.so.2.1")
    wget("https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/main/Forge_classic_Kaggle/download_magic.py")

    # 2. Clonar forge-classic (rama neo)
    if not FORGE_DIR.exists():
        clone("https://github.com/Haoming02/sd-webui-forge-classic.git -b neo")
    else:
        _run("git pull", cwd=FORGE_DIR)

    # 3. Extensiones
    EXT_DIR.mkdir(parents=True, exist_ok=True)
    
    repos = [
        ("https://github.com/gutris1/sd-image-encryption", None),
        ("https://github.com/gutris1/sd-hub", 1),
        ("https://github.com/Haoming02/sd-forge-couple", 1),
        ("https://github.com/AlUlkesh/stable-diffusion-webui-images-browser", 1),
        ("https://github.com/DominikDoom/a1111-sd-webui-tagcomplete", 1),
        ("https://github.com/gutris1/sd-image-info", 1),
        ("https://github.com/viyiviyi/stable-diffusion-webui-zoomimage", 1),
        ("https://github.com/gutris1/sd-simple-dimension-preset", 1),
        ("https://github.com/Bing-su/adetailer", 1),
        ("https://github.com/gutris1/sd-civitai-browser-plus-plus", 1),
    ]
    
    for repo, depth in repos:
        clone(repo, depth=depth, cwd=EXT_DIR)

    # 4. Sistema + aria2 + gdown
    _run("sudo apt update -qq")
    _run("sudo apt install aria2 -q")
    _run("pip install gdown -q")

    # 5. Instalar uv
    _run("curl -LsSf https://astral.sh/uv/install.sh | sh")

    # 6. Python 3.13 y venv
    os.chdir(FORGE_DIR)
    _run("sudo apt install -y python3.13 python3.13-dev python3.13-venv build-essential")
    _run("curl -LsSf https://astral.sh/uv/install.sh | sh")
    _run("uv venv .venv --python /usr/bin/python3.13 --seed --clear")
    _run("/usr/bin/python3.13 -m ensurepip --upgrade")
    _run("/usr/bin/python3.13 -m pip install --upgrade pip setuptools wheel")

    # 7. SageAttention
    wheel = "sageattention-2.1.2-cp313-cp313-linux_x86_64.whl"
    wget(f"https://huggingface.co/datasets/WhiteAiZ/T4_SageAttention2_For_Google_Colab/resolve/main/{wheel}")
    _run(f"uv pip install --python /usr/bin/python3.13 {wheel}")

    # 8. Dependencias de Forge
    _run("uv pip install --python /usr/bin/python3.13 -r requirements.txt --no-progress")
    _run("uv pip install --python /usr/bin/python3.13 torch torchvision xformers triton==3.5.1 --index-url https://download.pytorch.org/whl/cu128 --no-progress")

    # 9. Enlaces temporales
    links = [
        "rm -rf /kaggle/working/tmp ~/tmp",
        "ln -vs /tmp ~/tmp",
        "rm -rf /kaggle/working/sd-webui-forge-classic/models/Stable-diffusion/tmp_models",
        "mkdir -p /tmp/models",
        "ln -vs /tmp/models /kaggle/working/sd-webui-forge-classic/models/Stable-diffusion/tmp_models",
        "rm -rf /kaggle/working/sd-webui-forge-classic/models/Lora/tmp_lora",
        "mkdir -p /tmp/lora",
        "ln -vs /tmp/lora /kaggle/working/sd-webui-forge-classic/models/Lora/tmp_lora",
        "rm -rf /kaggle/working/sd-webui-forge-classic/models/ControlNet",
        "mkdir -p /tmp/controlnet",
        "ln -vs /tmp/controlnet /kaggle/working/sd-webui-forge-classic/models/ControlNet",
        "rm -rf /kaggle/working/sd-webui-forge-classic/models/text_encoder",
        "mkdir -p /tmp/text_encoder",
        "ln -vs /tmp/text_encoder /kaggle/working/sd-webui-forge-classic/models/text_encoder",
    ]
    for cmd in links:
        _run(cmd)

    # 10. Mensaje final
    print("\n" + "=" * 50)
    print("🎉 Instalación completada")
    print("=" * 50)

if __name__ == "__main__":
    main()