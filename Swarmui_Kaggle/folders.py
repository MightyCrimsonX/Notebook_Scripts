import os
base_path = "/kaggle/working/"
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

# Asegurar que las carpetas existan
os.makedirs(BASE_MODELS_DIR, exist_ok=True)
os.makedirs(LORA_DIR, exist_ok=True)
os.makedirs(VAE_DIR, exist_ok=True)
os.makedirs(UPSCALER_DIR, exist_ok=True)
os.makedirs(CONTROLNET_DIR, exist_ok=True)
os.makedirs(DIFFUSION_DIR, exist_ok=True)
os.makedirs(TEXT_ENCODER_DIR, exist_ok=True)
os.makedirs(UNET_DIR, exist_ok=True)
os.makedirs(CLIP_DIR, exist_ok=True)

os.environ["HOME"] = base_path