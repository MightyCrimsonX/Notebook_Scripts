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

BASE_DIR = Path("/teamspace/studios/this_studio").resolve()
FORGE_DIR = BASE_DIR / "stable-diffusion-webui-reForge"
MODELS_DIR = FORGE_DIR / "models"
VAE_DIR = MODELS_DIR / "VAE"
LORA_DIR = MODELS_DIR / "Lora"
EXT_DIR = FORGE_DIR / "extensions"
TMP_DIR = Path("/tmp")
TMP_MODELS = TMP_DIR / "models"
TMP_LORAS = TMP_DIR / "lora"
TMP_CONTROLNET = TMP_DIR / "controlnet"
UPSCALERS_DIR = MODELS_DIR / "ESRGAN"
ADETAILER_DIR = MODELS_DIR / "adetailer"
EMBEDDINGS_DIR = FORGE_DIR / "embeddings"

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
    
    # === NUEVO: Instalación de dependencias para Python 3.12 y uv ===
    _run("curl -LsSf https://astral.sh/uv/install.sh | sh")
    
    # Configurar variables de entorno para uv
    os.environ["PATH"] += os.pathsep + os.path.expanduser("~/.cargo/bin")
    os.environ['UV_LINK_MODE'] = 'copy'

    # 2. Clonar forge-classic
    shutil.rmtree(FORGE_DIR, ignore_errors=True)
    _run("git clone https://github.com/Panchovix/stable-diffusion-webui-reForge.git", cwd=BASE_DIR)
    # 2.5 Fix requirements_versions.txt

    requirements_path = FORGE_DIR / "requirements_versions.txt"
    os.remove(requirements_path)  # Eliminar el archivo original
    wget(
        "https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/Dev/Reforge-Kaggle/requirements_versions.txt",
        output=str(requirements_path),
        quiet=True
    )

    # === NUEVO: Creación de entorno virtual e instalación de paquetes con uv ===
    # Ejecutamos esto DENTRO de FORGE_DIR para que encuentre el requirements.txt
    _run("uv pip install --upgrade pip setuptools wheel", cwd=FORGE_DIR)
    _run("uv pip install mediapipe==0.10.32 --no-progress", cwd=FORGE_DIR)
    _run("uv pip install https://github.com/huchenlei/Depth-Anything/releases/download/v1.0.0/depth_anything-2024.1.22.0-py2.py3-none-any.whl --no-progress", cwd=FORGE_DIR)
    _run("uv pip install https://github.com/huchenlei/HandRefinerPortable/releases/download/v1.0.1/handrefinerportable-2024.2.12.0-py2.py3-none-any.whl --no-progress", cwd=FORGE_DIR)
    _run("uv pip install https://github.com/MackinationsAi/UDAV2-ControlNet/releases/download/v1.0.0/depth_anything_v2-2024.7.1.0-py2.py3-none-any.whl --no-progress", cwd=FORGE_DIR)
    _run("uv pip install addict fvcore onnxruntime svglib yapf --no-progress", cwd=FORGE_DIR)
    _run("uv pip install numpy==1.26.4 --reinstall --no-progress", cwd=FORGE_DIR)
    _run("uv pip install clip gradio==3.41.2 ultralytics insightface send2trash ZipUnicode bs4 pysocks gdown aria2 pv lz4 --no-progress", cwd=FORGE_DIR)
    _run("uv pip install -r requirements_versions.txt --no-progress", cwd=FORGE_DIR)

    # Descargar e instalar sageattention
    _run("uv pip install --python /usr/bin/python3.12 torch==2.9.1 torchvision==0.24.1 xformers==0.0.33.post2 triton==3.5.1 --index-url https://download.pytorch.org/whl/cu128 --no-progress", cwd=FORGE_DIR)
    sage_whl = "sageattention-2.1.2-cp312-cp312-linux_x86_64.whl"
    wget(f"https://huggingface.co/datasets/WhiteAiZ/T4_SageAttention2_For_Google_Colab/resolve/main/python%203.12/{sage_whl}", output=str(FORGE_DIR / sage_whl), quiet=True)
    _run(f"uv pip install --python /usr/bin/python3.12 {sage_whl}", cwd=FORGE_DIR)
    # =================================================================

    # 3. Descargar ui-config.json, styles.csv y scripts
    wget(
        "https://huggingface.co/datasets/WhiteAiZ/stable-diffusion-webui-reForge/resolve/main/ui-config.json",
        output=str(FORGE_DIR / "ui-config.json"),
        quiet=True
    )
    wget(
        "https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/Dev/Reforge-Kaggle/configreforge.json",
        output=str(FORGE_DIR / "config.json"),
        quiet=True
    )
    wget(
        "https://huggingface.co/datasets/WhiteAiZ/sd-webui-forge-classic/resolve/main/styles.csv",
        output=str(FORGE_DIR / "styles.csv"),
        quiet=True
    )
    wget(
        "https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/Dev/Forge_classic_Kaggle/download_magic.py",
        output=str(BASE_DIR / "download_magic.py"),
        quiet=True
    )
    wget(
        "https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/libmimalloc.so.2.1",
        output=str(BASE_DIR / "libmimalloc.so.2.1"),
        quiet=True
    )
    wget(
        "https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/Dev/Reforge_Lightning/temp_dir.py",
        output=str(BASE_DIR / "temp_dir.py"),
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
    _run("uv pip install numpy==1.26.4 --no-progress", cwd=FORGE_DIR)
    # 5. Sistema + aria2
    _run("uv pip install gdown", cwd=FORGE_DIR) # Cambiado a uv pip para instalarlo en el entorno virtual
    

    # 7. Enlaces simbólicos
    os.makedirs(LORA_DIR, exist_ok=True)
    # tmp
    _run("rm -rf /teamspace/studios/this_studio/tmp ~/tmp")
    _run("ln -vs /tmp ~/tmp")
    
    # models
    _run("rm -rf /teamspace/studios/this_studio/stable-diffusion-webui-reForge/models/Stable-diffusion/tmp_models")
    _run("mkdir -p /tmp/models")
    _run("ln -vs /tmp/models /teamspace/studios/this_studio/stable-diffusion-webui-reForge/models/Stable-diffusion/tmp_models")
    
    # lora
    _run("rm -rf /teamspace/studios/this_studio/stable-diffusion-webui-reForge/models/Lora/tmp_lora")
    _run("mkdir -p /tmp/lora")
    _run("ln -vs /tmp/lora /teamspace/studios/this_studio/stable-diffusion-webui-reForge/models/Lora/tmp_lora")

    # Controlnet
    _run("rm -rf /teamspace/studios/this_studio/stable-diffusion-webui-reForge/models/ControlNet")
    _run("mkdir -p /tmp/controlnet")
    _run("ln -vs /tmp/controlnet /teamspace/studios/this_studio/stable-diffusion-webui-reForge/models/ControlNet")
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