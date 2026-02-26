#!/usr/bin/env python3
# temp_files.py
import os
import subprocess
import pickle
from pathlib import Path

# -------------- configuración --------------
STORE_FILE    = Path.home() / ".civitai_token.pkl"
TOKEN_CIVITAI = ""   # valor por defecto
# -------------------------------------------

def leer_token() -> str:
    """Devuelve el token en este orden:
       1) archivo pickle, 2) env-var, 3) valor por defecto."""
    if STORE_FILE.exists():
        return pickle.loads(STORE_FILE.read_bytes())
    return os.getenv("CIVITAI_TOKEN", TOKEN_CIVITAI)

def guardar_token(val: str) -> None:
    """Persiste el token."""
    if not val.strip():
        print("⚠️ No se ingresó token.")
        return
    STORE_FILE.write_bytes(pickle.dumps(val))
    print(f"✅ Token guardado en {STORE_FILE}")

def _run(cmd: str) -> None:
    print(f"+ {cmd}")
    subprocess.run(cmd, shell=True, check=False)

def preparar():
    """Prepara enlaces para sd-webui-forge-classic."""
    token = leer_token()
    guardar_token(token)          # lo re-escribe (por si acaso)

    cmds = [
        "rm -rf /teamspace/studios/this_studio/tmp ~/tmp",
        "ln -vs /tmp ~/tmp",
        "rm -rf /teamspace/studios/this_studio/sd-webui-forge-classic/models/Stable-diffusion/tmp_models",
        "mkdir -p /tmp/models",
        "ln -vs /tmp/models /teamspace/studios/this_studio/sd-webui-forge-classic/models/Stable-diffusion/tmp_models",
        "rm -rf /teamspace/studios/this_studio/sd-webui-forge-classic/models/Lora/tmp_lora",
        "mkdir -p /tmp/lora",
        "ln -vs /tmp/lora /teamspace/studios/this_studio/sd-webui-forge-classic/models/Lora/tmp_lora",
        "rm -rf /teamspace/studios/this_studio/sd-webui-forge-classic/models/ControlNet",
        "mkdir -p /tmp/controlnet",
        "ln -vs /tmp/controlnet /teamspace/studios/this_studio/sd-webui-forge-classic/models/ControlNet",
    ]
    for c in cmds:
        _run(c)
    print("🎉 Entorno Forge listo.")

if __name__ == "__main__":
    preparar()