#!/usr/bin/env python3
"""
install_swarmui.py
Instala SwarmUI en Kaggle con ComfyUI backend, extensiones, modelos y configuraciones.
"""

import os
import subprocess
from pathlib import Path
WORK_DIR = Path("/kaggle/working").resolve()
SWARM_DIR = WORK_DIR / "SwarmUI"
COMFY_DIR = SWARM_DIR / "dlbackend" / "ComfyUI"
HOME = "/kaggle/working"
BASE_MODELS_DIR = "/kaggle/working/SwarmUI/Models/Stable-Diffusion"
LORA_DIR = "/kaggle/working/SwarmUI/Models/Lora"
VAE_DIR = "/kaggle/working/SwarmUI/Models/VAE"
UPSCALER_DIR = "/kaggle/working/SwarmUI/Models/upscale_models"
CONTROLNET_DIR = "/kaggle/working/SwarmUI/Models/controlnet"
DIFFUSION_DIR = "/kaggle/working/SwarmUI/Models/diffusion_models"
TEXT_ENCODER_DIR = "/kaggle/working/SwarmUI/Models/text_encoders"
UNET_DIR = "/kaggle/working/SwarmUI/Models/unet"
CLIP_DIR = "/kaggle/working/SwarmUI/Models/clip"
COMFY_EXT_DIR = "/kaggle/working/SwarmUI/dlbackend/ComfyUI/custom_nodes"
TMP_MODELS= "/tmp/models"
TMP_LORAS = "/tmp/loras"
TMP_VAE = "/tmp/vae"
TMP_CONTROLNET = "/tmp/controlnet"
TMP_DIFFUSION = "/tmp/diffusion_models"
TMP_TEXT_ENCODERS = "/tmp/text_encoders"
EMBEDDINGS = "/kaggle/working/SwarmUI/Models/Embeddings"

def _run(cmd: str, cwd: Path | None = None) -> None:
    """Ejecuta un comando shell."""
    print(f"+ {cmd}")
    subprocess.run(cmd, shell=True, check=False, cwd=cwd)

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
    os.chdir(WORK_DIR)

    # 1. Descargas iniciales y clonar SwarmUI
    wget("https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/main/scripts/dmagic_swarm.py")
    wget("https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/main/Swarmui_Kaggle/gestor_swarm.py")
    if not SWARM_DIR.exists():
        clone("https://github.com/mcmonkeyprojects/SwarmUI")
    
    (SWARM_DIR / "Models").mkdir(parents=True, exist_ok=True)
    (SWARM_DIR / "dlbackend").mkdir(parents=True, exist_ok=True)
    
    _run("pip install aria2 gdown")

    # 2. Configuración de SwarmUI (Data)
    data_dir = SWARM_DIR / "Data"
    data_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(data_dir)
    
    wget("https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/Swarmui_Kaggle/Settings.fds",
         quiet=True, show_progress=False)
    wget("https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/Swarmui_Kaggle/Backends.fds",
         quiet=True, show_progress=False)
    wget("https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/Swarmui_Kaggle/Users.ldb",
         quiet=True, show_progress=False)
    
    # Autocompletions
    auto_dir = data_dir / "Autocompletions"
    auto_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(auto_dir)
    wget("https://huggingface.co/datasets/Mightys/SwarmuiColab/resolve/main/Data/Autocompletions/danbooru_e621_merged.csv",
         quiet=True, show_progress=False)

    # 3. Instalar .NET
    os.chdir(WORK_DIR)
    wget("https://dot.net/v1/dotnet-install.sh", output="dotnet-install.sh")
    _run("chmod +x dotnet-install.sh")
    _run("./dotnet-install.sh --channel 8.0")

    # 5. Clonar ComfyUI
    os.chdir(SWARM_DIR / "dlbackend")
    if not COMFY_DIR.exists():
        clone("https://github.com/comfyanonymous/ComfyUI.git")
    else:
        _run("git pull", cwd=COMFY_DIR)

    # 6. Dependencias de ComfyUI
    os.chdir(COMFY_DIR)
    _run("uv pip install comfy-aimdo==0.2.8 --no-progress")
    _run("uv pip install -r requirements.txt --no-progress")
    _run("uv pip install --upgrade pip diffusers transformers --no-progress")
    _run("uv pip install -U transformers peft --no-progress")
    _run("uv pip install torch==2.9.1 torchvision==0.24.1 torchaudio xformers==0.0.33.post2 triton==3.5.1 --index-url https://download.pytorch.org/whl/nightly/cu128 --no-progress")
    _run("uv pip install onnxruntime gdown pickleshare tipo-kgen==0.1.9 insightface clip rembg fastcore==1.8.0 ultralytics==8.3.197 --no-progress")
    # 7. Extensiones de SwarmUI
    ext_dir = SWARM_DIR / "src" / "Extensions"
    ext_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(ext_dir)
    clone("https://github.com/jtreminio/SwarmUI-PromptBuilderExtension.git")
    clone("https://github.com/yoinked-h/MaHiRon-SwarmUI.git")
    clone("https://github.com/Hugs288/TipoForSwarmUI.git")

    # 8. SageAttention
    os.chdir(WORK_DIR)
    wheel = "sageattention-2.1.2-cp312-cp312-linux_x86_64.whl"
    wget(f"https://huggingface.co/datasets/WhiteAiZ/T4_SageAttention2_For_Google_Colab/resolve/main/python%203.12/{wheel}", 
         quiet=True, show_progress=False)
    _run(f"uv pip install {wheel}")

    # 9. Wildcards
    wild_dir = SWARM_DIR / "Data" / "Wildcards"
    wild_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(wild_dir)
    aria2c("https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/Wildcards/artist_tags_danbooru5000.txt",
           "5000-booru-artist.txt")

    # 10. Modelos YOLO (segmentación/adetailers)
    yolo_dir = SWARM_DIR / "Models" / "yolov8"
    yolo_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(yolo_dir)
    
    yolo_models = [
        ("https://huggingface.co/Anzhc/Anzhcs_YOLOs/resolve/main/Anzhc%20Eyes%20-seg-hd.pt", "Anzhc_Eyes-seg-hd.pt"),
        ("https://huggingface.co/Anzhc/Anzhcs_YOLOs/resolve/main/Anzhc%20Face%20seg%20640%20v3%20y11n.pt", "Anzhc_Face_seg_v3_y11n.pt"),
        ("https://huggingface.co/Anzhc/Anzhcs_YOLOs/resolve/main/Anzhc%20Breasts%20Seg%20v1%201024n.pt", "Anzhc_Breasts_Seg_v1_1024n.pt"),
        ("https://huggingface.co/Anzhc/Anzhcs_YOLOs/resolve/main/Anzhc%20HeadHair%20seg%20y8n.pt", "Anzhc_HeadHair_seg_y8n.pt"),
        ("https://huggingface.co/Nudimmud/adetailers/resolve/main/assdetailer-seg.pt", "assdetailer.pt"),
        ("https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8n.pt", "face_yolov8n.pt"),
        ("https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8m.pt", "face_yolov8m.pt"),
        ("https://huggingface.co/Bingsu/adetailer/resolve/main/hand_yolov8n.pt", "hand_yolov8n.pt"),
        ("https://huggingface.co/Bingsu/adetailer/resolve/main/hand_yolov9c.pt", "hand_yolov9c.pt"),
        ("https://huggingface.co/Bingsu/adetailer/resolve/main/hand_yolov8s.pt", "hand_yolov8s.pt"),
    ]
    
    for url, out in yolo_models:
        aria2c(url, out)

    # 11. VAE
    vae_dir = SWARM_DIR / "Models" / "VAE"
    vae_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(vae_dir)
    # Nota: %download es una magic de IPython, aquí usamos wget directamente
    wget("https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl_vae.safetensors",
         quiet=True, show_progress=False)

    # 12. Gradio tunnel
    gradio_script = SWARM_DIR / "gradio-tunnel.py"
    if not gradio_script.exists():
        wget("https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/scripts/gradio-tunnel.py",
             output=str(gradio_script))

    # 13. Parche de memoria (libmimalloc)
    print("🛠️ Instalando parche de memoria (libmimalloc.so.2.1)...")
    mimalloc_path = WORK_DIR / "libmimalloc.so.2.1"
    if not mimalloc_path.exists():
        wget("https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/libmimalloc.so.2.1",
             output=str(mimalloc_path))
        print("✅ Parche descargado.")
    else:
        print("✅ Parche listo.")
    
    _run("pip install -q requests")

    # 14. Configuración de enlaces simbólicos para modelos y recursos
    # Asegurar que las carpetas existan
    os.makedirs(HOME, exist_ok=True)
    os.makedirs(BASE_MODELS_DIR, exist_ok=True)
    os.makedirs(LORA_DIR, exist_ok=True)
    os.makedirs(VAE_DIR, exist_ok=True)
    os.makedirs(UPSCALER_DIR, exist_ok=True)
    os.makedirs(CONTROLNET_DIR, exist_ok=True)
    os.makedirs(DIFFUSION_DIR, exist_ok=True)
    os.makedirs(TEXT_ENCODER_DIR, exist_ok=True)
    os.makedirs(UNET_DIR, exist_ok=True)
    os.makedirs(CLIP_DIR, exist_ok=True)
    os.makedirs(EMBEDDINGS, exist_ok=True)
    _run("rm -rf /kaggle/working/tmp ~/tmp")
    _run("ln -vs /tmp ~/tmp")

    _run("rm -rf /kaggle/working/SwarmUI/Models/Stable-Diffusion/tmp_models")
    _run("mkdir -p /tmp/models")
    _run("ln -vs /tmp/models /kaggle/working/SwarmUI/Models/Stable-Diffusion/tmp_models")

    _run("rm -rf /kaggle/working/SwarmUI/Models/Lora/tmp_loras")
    _run("mkdir -p /tmp/loras")
    _run("ln -vs /tmp/loras /kaggle/working/SwarmUI/Models/Lora/tmp_loras")

    _run("rm -rf /kaggle/working/SwarmUI/Models/VAE")
    _run("mkdir -p /tmp/vae")
    _run("ln -vs /tmp/vae /kaggle/working/SwarmUI/Models/VAE")

    _run("rm -rf /kaggle/working/SwarmUI/Models/controlnet")
    _run("mkdir -p /tmp/controlnet")
    _run("ln -vs /tmp/controlnet /kaggle/working/SwarmUI/Models/controlnet")

    _run("rm -rf /kaggle/working/SwarmUI/Models/diffusion_models")
    _run("mkdir -p /tmp/diffusion_models")
    _run("ln -vs /tmp/diffusion_models /kaggle/working/SwarmUI/Models/diffusion_models")

    _run("rm -rf /kaggle/working/SwarmUI/Models/text_encoders")
    _run("mkdir -p /tmp/text_encoders")
    _run("ln -vs /tmp/text_encoders /kaggle/working/SwarmUI/Models/text_encoders")


    #15 instalacion de custom nodes para comfyui
    os.chdir(COMFY_EXT_DIR)
    clone("https://github.com/MightyCrimsonX/Euler-Smea-Dyn-Sampler-Comfyui.git")
    clone("https://github.com/mcmonkeyprojects/sd-dynamic-thresholding.git")
    clone("https://github.com/KohakuBlueleaf/z-tipo-extension.git")
    clone("https://github.com/Fannovel16/comfyui_controlnet_aux.git")
    CNET_AUX_DIR = os.path.join(COMFY_EXT_DIR, "comfyui_controlnet_aux")
    os.chdir(CNET_AUX_DIR)
    _run("uv pip install -r requirements.txt --no-progress")

    comfymodels = os.path.join(COMFY_DIR, "models")
    kgen = os.path.join(comfymodels, "kgen")
    os.makedirs(kgen, exist_ok=True)
    os.chdir(kgen)
    aria2c("https://huggingface.co/KBlueLeaf/TIPO-500M-ft/resolve/main/TIPO-500M-ft-F16.gguf", "TIPO-500M-ft-F16.gguf")


    # Limpiar y mensaje final
    os.system("clear" if os.name != "nt" else "cls")
    print("\n" + "=" * 50)
    print("🎉 Instalación completada")
    print("=" * 50)

if __name__ == "__main__":
    main()