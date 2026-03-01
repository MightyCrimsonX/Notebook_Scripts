#!/usr/bin/env python3
"""
install_comfyui_lightning.py
Instala ComfyUI en Lightning.ai con extensiones y dependencias.
"""

import os
import subprocess
from pathlib import Path

BASE_DIR = Path("/teamspace/studios/this_studio").resolve()
COMFY_DIR = BASE_DIR / "ComfyUI"
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

def pull(repo_dir: Path) -> None:
    """Hace git pull en un repositorio existente."""
    _run("git pull", cwd=repo_dir)

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
    wget("https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/main/Comfyui-Lightning/on_start.sh",
         output=str(on_start))

    os.chdir(BASE_DIR)

    # 3. Clonar ComfyUI y descargas auxiliares
    if not COMFY_DIR.exists():
        clone("https://github.com/comfyanonymous/ComfyUI.git")
        _run("git pull", cwd=COMFY_DIR)

        wget("https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/main/Comfyui-Lightning/gestor_comfy.py",
         quiet=True)
    wget("https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/main/scripts/download_magic.py",
         quiet=True)
    wget("https://huggingface.co/datasets/Mightys/Notebook_Scripts/resolve/main/libmimalloc.so.2.1",
         quiet=True)
    wget("https://raw.githubusercontent.com/MightyCrimsonX/Notebook_Scripts/refs/heads/main/Comfyui-Lightning/temp_dir.py",
         quiet=True)
    
      # 4. Dependencias Python
    _run("sudo apt install git python3-pip -y")

    os.chdir(COMFY_DIR)
    _run("uv pip install -U transformers peft")
    aria2c("https://github.com/JamePeng/llama-cpp-python/releases/download/v0.3.17-cu128-AVX2-linux-20251209/llama_cpp_python-0.3.17-cp312-cp312-linux_x86_64.whl",
           "llama_cpp_python-0.3.17-cp312-cp312-linux_x86_64.whl")
    _run("uv pip install llama_cpp_python-0.3.17-cp312-cp312-linux_x86_64.whl")
    _run("uv pip install torch==2.9.1 torchvision==0.24.1 xformers==0.0.33.post2 triton==3.5.1 "
         "--index-url https://download.pytorch.org/whl/cu128 --no-progress")
    _run("uv pip install tipo-kgen rembg ultralytics==8.3.216 onnxruntime gdown pickleshare insightface clip numpy==2.3.0 "
         "--no-progress")
    _run("uv pip install -r requirements.txt --no-progress")

    # 6. SageAttention
    wheel = "sageattention-2.1.2-cp312-cp312-linux_x86_64.whl"
    llama = "llama_cpp_python-0.3.17-cp312-cp312-linux_x86_64.whl"
    wget("https://huggingface.co/datasets/WhiteAiZ/T4_SageAttention2_For_Google_Colab/resolve/main/python%203.12/" + wheel)
    _run(f"uv pip install {wheel}")
    os.remove(wheel)
    os.remove(llama)

    # 7. Extensiones/custom nodes
    os.chdir(NODES_DIR)
    
    clone("https://github.com/Comfy-Org/ComfyUI-Manager.git")
    clone("https://github.com/crystian/ComfyUI-Crystools.git")
    clone("https://github.com/city96/ComfyUI-GGUF.git")
    clone("https://github.com/rgthree/rgthree-comfy.git")
    clone("https://github.com/MightyCrimsonX/Euler-Smea-Dyn-Sampler-Comfyui.git")
    clone("https://github.com/ltdrdata/ComfyUI-Impact-Pack.git")
    clone("https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git")
    clone("https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git")
    clone("https://github.com/newtextdoc1111/ComfyUI-Autocomplete-Plus.git")
    clone("https://github.com/yolain/ComfyUI-Easy-Use.git")
    clone("https://github.com/kijai/ComfyUI-KJNodes.git")
    clone("https://github.com/KohakuBlueleaf/z-tipo-extension.git")

    # 8. Instalar requirements de cada nodo
    nodes_reqs = [
        "comfyui-manager",
        "ComfyUI-Crystools",
        "ComfyUI-GGUF",
        "rgthree-comfy",
        "ComfyUi-Impact-Pack",
        "ComfyUI-Impact-Subpack",
        "ComfyUI_UltimateSDUpscale",
        "ComfyUI-easy-use",
        "ComfyUI-KJNodes",
        "z-tipo-extension",
    ]

    for node in nodes_reqs:
        node_path = NODES_DIR / node
        if (node_path / "requirements.txt").exists():
            os.chdir(node_path)
            _run("uv pip install -r requirements.txt --no-progress")

    # 9. Limpieza y enlaces simbólicos
    _run("rm -rf /teamspace/studios/this_studio/.cache")

    # 10. Ejecutar temp_dir.py si existe
    os.chdir(BASE_DIR)
    temp_dir_path = BASE_DIR / "temp_dir.py"
    if temp_dir_path.exists():
        _run(f"python {temp_dir_path}")

     # Mensaje final
    os.system("clear" if os.name != "nt" else "cls")
    print("\n" + "=" * 50)
    print("🎉 Instalación completada")
    print("=" * 50)

if __name__ == "__main__":
    main()

