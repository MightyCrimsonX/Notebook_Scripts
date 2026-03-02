#!/usr/bin/env python3
"""
Forge_Classic_Setup.py
Instala sd-webui-forge-classic en Kaggle con extensiones y dependencias,
incluyendo la configuración de uv y el entorno virtual en Python 3.11.
"""

import os
import subprocess
import shutil
from pathlib import Path

BASE_DIR = Path("/kaggle/working").resolve()
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

def _run(cmd: str, cwd: Path | None = None) -> None:
    """Ejecuta un comando shell."""
    print(f"+ {cmd}")
    subprocess.run(cmd, shell=True, check=False, cwd=cwd)

def wget(url: str, output: str | None = None, quiet: bool = False) -> None:
    """Descarga con wget."""
    cmd = "wget"
    if quiet:
        cmd += " -q"
    if output:
        cmd += f" -O {output}"
    cmd += f" {url}"
    _run(cmd)

def aria2c(url: str, output: str, cwd: Path | None = None) -> None:
    """Descarga con aria2c."""
    cmd = (f'aria2c --console-log-level=error -c -x 16 -s 16 -k 1M '
           f'"{url}" -o {output}')
    _run(cmd, cwd=cwd)

def clone(repo: str, cwd: Path | None = None, depth: int | None = None) -> None:
    """Clona un repositorio git."""
    cmd = f"git clone {repo}"
    if depth is not None:
        cmd += f" --depth {depth}"
    _run(cmd, cwd=cwd)

def main() -> None:
    # 1. Sistema: Dependencias base y aria2
    _run("sudo apt-get update")
    _run("sudo apt install aria2 -q")
    
    # === NUEVO: Instalación de dependencias para Python 3.11 y uv ===
    _run("sudo apt install -y python3.11-dev python3.11-venv python3.11-distutils build-essential")
    _run("curl -LsSf https://astral.sh/uv/install.sh | sh")
    
    # Configurar variables de entorno para uv
    os.environ["PATH"] += os.pathsep + os.path.expanduser("~/.cargo/bin")
    os.environ['UV_LINK_MODE'] = 'copy'

    # 2. Clonar forge-classic
    shutil.rmtree(FORGE_DIR, ignore_errors=True)
    _run("git clone -b classic https://github.com/Haoming02/sd-webui-forge-classic.git", cwd=BASE_DIR)
    # === NUEVO: Creación de entorno virtual e instalación de paquetes con uv ===
    # Ejecutamos esto DENTRO de FORGE_DIR para que encuentre el requirements.txt
    _run("uv venv .venv --python /usr/bin/python3.11 --clear --seed", cwd=FORGE_DIR)
    _run("uv pip install --python .venv --upgrade pip setuptools wheel", cwd=FORGE_DIR)
    _run("uv pip install --python .venv mediapipe==0.10.32 --no-progress", cwd=FORGE_DIR)
    _run("uv pip install --python .venv addict fvcore onnxruntime svglib yapf handrefinerportable depth_anything depth_anything_v2 --no-progress", cwd=FORGE_DIR)
    _run("uv pip install --python .venv numpy==1.26.4 --reinstall --no-progress", cwd=FORGE_DIR)
    _run("uv pip install --python .venv clip gradio==3.41.2 ultralytics==8.3.216 insightface send2trash ZipUnicode bs4 pysocks gdown aria2 pv lz4 --no-progress", cwd=FORGE_DIR)
    _run("uv pip install --python .venv -r requirements.txt --no-progress", cwd=FORGE_DIR)
    
    # Descargar e instalar sageattention
    _run("uv pip install --python .venv torch==2.9.1 torchvision==0.24.1 xformers==0.0.33.post2 triton==3.5.1 --index-url https://download.pytorch.org/whl/cu128 --no-progress", cwd=FORGE_DIR)
    sage_whl = "sageattention-2.1.2-cp311-cp311-linux_x86_64.whl"
    wget(f"https://huggingface.co/datasets/WhiteAiZ/T4_SageAttention2_For_Google_Colab/resolve/main/python%203.11/{sage_whl}", output=str(FORGE_DIR / sage_whl))
    _run(f"uv pip install --python .venv {sage_whl}", cwd=FORGE_DIR)
    # =================================================================

    # 3. Descargar ui-config.json, styles.csv y scripts
    wget(
        "https://huggingface.co/datasets/WhiteAiZ/sd-webui-forge-classic/resolve/main/ui-config.json",
        output=str(FORGE_DIR / "ui-config.json"),
        quiet=True
    )
    wget(
        "https://huggingface.co/datasets/WhiteAiZ/sd-webui-forge-classic/resolve/main/styles.csv",
        output=str(FORGE_DIR / "styles.csv"),
        quiet=True
    )
    wget(
        "https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/main/scripts/download_magic.py",
        output=str(BASE_DIR / "download_magic.py"),
        quiet=True
    )
    wget(
        "https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/libmimalloc.so.2.1",
        output=str(BASE_DIR / "libmimalloc.so.2.1"),
        quiet=True
    )

    # 4. Extensiones
    EXT_DIR.mkdir(parents=True, exist_ok=True)
    
    repos = [
        ("https://github.com/pamparamm/sd-perturbed-attention", None),
        ("https://github.com/gutris1/sd-image-encryption", None),
        ("https://github.com/yankooliveira/sd-webui-photopea-embed.git", None),
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
        clone(repo, cwd=EXT_DIR, depth=depth)
    _run("uv pip install --python .venv numpy==1.26.4 --no-progress", cwd=FORGE_DIR)
    # 5. Sistema + aria2
    _run("uv pip install --python .venv gdown", cwd=FORGE_DIR) # Cambiado a uv pip para instalarlo en el entorno virtual
    
    # 6. Enlaces simbólicos
    # tmp
    _run("rm -rf /kaggle/working/tmp ~/tmp")
    _run("ln -vs /tmp ~/tmp")
    
    # models
    _run("rm -rf /kaggle/working/sd-webui-forge-classic/models/Stable-diffusion/tmp_models")
    _run("mkdir -p /tmp/models")
    _run("ln -vs /tmp/models /kaggle/working/sd-webui-forge-classic/models/Stable-diffusion/tmp_models")
    
    # lora
    _run("rm -rf /kaggle/working/sd-webui-forge-classic/models/Lora/tmp_lora")
    _run("mkdir -p /tmp/lora")
    _run("ln -vs /tmp/lora /kaggle/working/sd-webui-forge-classic/models/Lora/tmp_lora")

    # Controlnet
    _run("rm -rf /kaggle/working/sd-webui-forge-classic/models/ControlNet")
    _run("mkdir -p /tmp/controlnet")
    _run("ln -vs /tmp/controlnet /kaggle/working/sd-webui-forge-classic/models/ControlNet")
    print("\n✅ Enlaces simbólicos creados.")
    os.makedirs(ADETAILER_DIR, exist_ok=True)
    os.makedirs(UPSCALERS_DIR, exist_ok=True)
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

    # 7. Limpiar output y mostrar mensaje
    os.system("clear" if os.name != "nt" else "cls")
    print("\n" + "=" * 50)
    print("🎉 Instalación completada")
    print("=" * 50 + "\n")



if __name__ == "__main__":
    main()