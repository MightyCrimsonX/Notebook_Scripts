#!/usr/bin/env python3
"""
install_swarmui_lightning.py
Instala SwarmUI en Lightning.ai con ComfyUI backend, extensiones y dependencias.
"""

import os
import subprocess
from pathlib import Path

BASE_DIR = Path("/teamspace/studios/this_studio").resolve()
SWARM_DIR = BASE_DIR / "SwarmUI"
COMFY_DIR = SWARM_DIR / "dlbackend" / "ComfyUI"
NODES_DIR = COMFY_DIR / "custom_nodes"

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

def clone(repo: str, cwd: Path | None = None) -> None:
    """Clona un repositorio git."""
    _run(f"git clone {repo}", cwd=cwd)

def main() -> None:
    # 1. Sistema: .NET, aria2, ffmpeg
    _run("sudo apt-get update")
    _run("sudo apt-get install -y dotnet-sdk-8.0")
    _run("sudo apt install aria2 -q")
    _run("sudo apt install ffmpeg -y")

    # 2. Descargar on_start.sh
    lightning_dir = BASE_DIR / ".lightning_studio"
    lightning_dir.mkdir(parents=True, exist_ok=True)
    on_start = lightning_dir / "on_start.sh"
    if on_start.exists():
        on_start.unlink()
    wget("https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/Swarmui_Lightning/on_start.sh",
         output=str(on_start))

    os.chdir(BASE_DIR)

    # 3. Clonar SwarmUI y descargas auxiliares
    if not SWARM_DIR.exists():
        clone("https://github.com/mcmonkeyprojects/SwarmUI")

    wget("https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/main/Swarmui_Lightning/gestor_swarm.py",
         quiet=True)
    wget("https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/main/scripts/dmagic_swarm.py",
         quiet=True)
    wget("https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/libmimalloc.so.2.1",
         quiet=True)
    wget("https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/main/scripts/temp_dir.py",
         quiet=True)

    # 4. Preparar directorios y clonar ComfyUI
    _run("sudo apt install git python3-pip -y")
    (SWARM_DIR / "dlbackend").mkdir(parents=True, exist_ok=True)
    
    os.chdir(SWARM_DIR / "dlbackend")
    if not COMFY_DIR.exists():
        clone("https://github.com/comfyanonymous/ComfyUI.git")

    # 5. Dependencias de ComfyUI
    os.chdir(COMFY_DIR)
    _run("uv pip install -U transformers peft")
    aria2c("https://github.com/JamePeng/llama-cpp-python/releases/download/v0.3.17-cu128-AVX2-linux-20251209/llama_cpp_python-0.3.17-cp312-cp312-linux_x86_64.whl")
    _run("uv pip install llama_cpp_python-0.3.17-cp312-cp312-linux_x86_64.whl")
    _run("uv pip install torch==2.9.1 torchvision==0.24.1 xformers==0.0.33.post2 triton==3.5.1 "
         "--index-url https://download.pytorch.org/whl/cu128 --no-progress")
    _run("uv pip install tipo-kgen rembg ultralytics==8.3.216 onnxruntime gdown pickleshare insightface clip numpy==2.3.0 "
         "--no-progress")
    _run("uv pip install -r requirements.txt --no-progress")

    # 6. SageAttention
    wheel = "sageattention-2.1.2-cp312-cp312-linux_x86_64.whl"
    wget("https://huggingface.co/datasets/WhiteAiZ/T4_SageAttention2_For_Google_Colab/resolve/main/python%203.12/" + wheel)
    _run(f"uv pip install {wheel}")

    # 7. Custom nodes de ComfyUI
    NODES_DIR.mkdir(parents=True, exist_ok=True)
    os.chdir(NODES_DIR)
    
    clone("https://github.com/Comfy-Org/ComfyUI-Manager.git")
    clone("https://github.com/crystian/ComfyUI-Crystools.git")
    clone("https://github.com/city96/ComfyUI-GGUF.git")
    clone("https://github.com/rgthree/rgthree-comfy.git")
    clone("https://github.com/MightyCrimsonX/Euler-Smea-Dyn-Sampler-Comfyui.git")

    HOME = "/teamspace/studios/this_studio"
    MODELS= "/teamspace/studios/this_studio/SwarmUI/Models"
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
    
    os.makedirs(MODELS, exist_ok=True)
    os.makedirs(BASE_MODELS_DIR, exist_ok=True)
    os.makedirs(LORA_DIR, exist_ok=True)
    os.makedirs(VAE_DIR, exist_ok=True)
    os.makedirs(UPSCALER_DIR, exist_ok=True)
    os.makedirs(CONTROLNET_DIR, exist_ok=True)
    os.makedirs(DIFFUSION_DIR, exist_ok=True)
    os.makedirs(TEXT_ENCODER_DIR, exist_ok=True)
    os.makedirs(UNET_DIR, exist_ok=True)
    os.makedirs(CLIP_DIR, exist_ok=True)
    os.makedirs(COMFY_EXT_DIR, exist_ok=True)

    # 8. Instalar requirements de cada nodo
    nodes_reqs = [
        "ComfyUI-Manager",
        "ComfyUI-Crystools",
        "ComfyUI-GGUF",
        "rgthree-comfy",
    ]

    for node in nodes_reqs:
        node_path = NODES_DIR / node
        if (node_path / "requirements.txt").exists():
            os.chdir(node_path)
            _run("uv pip install -r requirements.txt --no-progress")

    # 9. Limpieza y enlaces simbólicos
    _run("rm -rf /teamspace/studios/this_studio/.cache")
    (SWARM_DIR / "Models").mkdir(parents=True, exist_ok=True)
    
    os.chdir(BASE_DIR)
    # Ejecutar symb.py si existe
    symb_path = BASE_DIR / "symb.py"
    if symb_path.exists():
        _run(f"python {symb_path}")

    # Mensaje final
    os.system("clear" if os.name != "nt" else "cls")
    print("\n" + "=" * 50)
    print("🎉 Instalación completada")
    print("=" * 50)

if __name__ == "__main__":
    main()