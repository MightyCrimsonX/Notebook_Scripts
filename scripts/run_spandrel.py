import os
import sys
import glob
import math
import argparse
import torch
import cv2
import numpy as np
from PIL import Image
from spandrel import ModelLoader, ImageModelDescriptor

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model_path", required=True, help="Ruta al modelo .pth")
parser.add_argument("-i", "--input_dir", required=True, help="Carpeta de entrada")
parser.add_argument("-o", "--output_dir", required=True, help="Carpeta de salida")
parser.add_argument("-s", "--scale", type=float, default=2.0, help="Escala final")
parser.add_argument("-t", "--tile", type=int, default=512, help="Tamaño de tile")
args = parser.parse_args()

os.makedirs(args.output_dir, exist_ok=True)

# 1. Cargar modelo con Spandrel
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
loader = ModelLoader(device=device)
descriptor = loader.load_from_file(args.model_path)

if not isinstance(descriptor, ImageModelDescriptor):
    raise TypeError("El archivo seleccionado no es un modelo de imagen compatible.")

model = descriptor.model.eval().to(device)
print(f"✅ Modelo cargado con Spandrel: {descriptor.architecture} (Escala nativa: {descriptor.scale}x)")

# 2. Función de inferencia con Tiling manual para evitar CUDA OOM
def process_tiled(img_tensor, tile_size=512, tile_pad=16):
    _, _, h, w = img_tensor.shape
    scale = descriptor.scale
    out_h, out_w = h * scale, w * scale
    out_tensor = torch.zeros((1, 3, out_h, out_w), dtype=torch.float32, device=device)

    tiles_x = math.ceil(w / tile_size)
    tiles_y = math.ceil(h / tile_size)

    with torch.no_grad():
        for y in range(tiles_y):
            for x in range(tiles_x):
                # Coordenadas del tile
                x1 = x * tile_size
                x2 = min(x1 + tile_size, w)
                y1 = y * tile_size
                y2 = min(y1 + tile_size, h)

                # Padding
                x1_pad = max(x1 - tile_pad, 0)
                x2_pad = min(x2 + tile_pad, w)
                y1_pad = max(y1 - tile_pad, 0)
                y2_pad = min(y2 + tile_pad, h)

                crop = img_tensor[:, :, y1_pad:y2_pad, x1_pad:x2_pad]
                out_crop = model(crop)

                # Quitar padding del resultado
                crop_x1 = (x1 - x1_pad) * scale
                crop_x2 = crop_x1 + (x2 - x1) * scale
                crop_y1 = (y1 - y1_pad) * scale
                crop_y2 = crop_y1 + (y2 - y1) * scale

                out_tensor[:, :, y1 * scale:y2 * scale, x1 * scale:x2 * scale] = out_crop[:, :, crop_y1:crop_y2, crop_x1:crop_x2]

    return out_tensor

# 3. Procesar lote
valid_exts = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
images = [f for f in os.listdir(args.input_dir) if f.lower().endswith(valid_exts)]

for idx, img_name in enumerate(images):
    src = os.path.join(args.input_dir, img_name)
    base_name = os.path.splitext(img_name)[0]
    dst = os.path.join(args.output_dir, f"{base_name}.png")

    print(f"[{idx+1}/{len(images)}] Procesando: {img_name}")

    # Cargar con PIL en RGB puro (evita alteraciones de espacio de color)
    pil_img = Image.open(src).convert("RGB")
    img_np = np.array(pil_img).astype(np.float32) / 255.0
    img_t = torch.from_numpy(img_np).permute(2, 0, 1).unsqueeze(0).to(device)

    # Upscale
    out_t = process_tiled(img_t, tile_size=args.tile)

    # Convertir a imagen final
    out_np = (out_t.squeeze(0).permute(1, 2, 0).clamp(0, 1).cpu().numpy() * 255.0).astype(np.uint8)
    res_img = Image.fromarray(out_np)

    # Reescalar al tamaño elegido por el usuario si difiere de la escala nativa
    target_w = int(pil_img.width * args.scale)
    target_h = int(pil_img.height * args.scale)
    if (res_img.width, res_img.height) != (target_w, target_h):
        res_img = res_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    res_img.save(dst)
