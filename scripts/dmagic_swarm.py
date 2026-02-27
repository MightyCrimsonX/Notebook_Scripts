# dmagic_swarm.py
"""
Mágica %download para IPython / Jupyter / Colab.
Lee el token de CivitAI desde ~/.civitai_token.pkl (pickle)
Incluye barra de progreso interactiva, renombrado con -o y autogeneración de metadata .swarm.json

Uso:
    import download_magic
    %download https://civitai.com/api/download/models/..., https://huggingface.co/...
    %download https://drive.google.com/file/d/123.../view -o MiModelo.safetensors
"""

from IPython import get_ipython
from IPython.core.magic import register_line_magic
from IPython.display import HTML, display, clear_output
from PIL import Image
from io import BytesIO
import ipywidgets as widgets
import os
import subprocess
import re
import requests
import pickle
import json
import base64
from pathlib import Path

# ---------- leer token desde pickle ----------
TOKEN_FILE = Path.home() / ".civitai_token.pkl"
token = None
if TOKEN_FILE.exists():
    try:
        token = pickle.loads(TOKEN_FILE.read_bytes())
    except Exception:
        pass
# ---------------------------------------------

def ejecutar_con_progreso(cmd, is_gdown=False):
    """Ejecuta el comando leyendo la salida para animar la barra de progreso."""
    progress_bar = widgets.IntProgress(
        value=0, min=0, max=100, 
        description='Progreso:', 
        bar_style='info', 
        orientation='horizontal', 
        layout=widgets.Layout(width='80%')
    )
    status_label = widgets.Label(value="Iniciando descarga...")
    display(widgets.VBox([progress_bar, status_label]))
    
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True, 
        bufsize=1, 
        universal_newlines=True
    )
    
    for line in process.stdout:
        if not is_gdown:
            match_pct = re.search(r'\((\d+)%\)', line)
            if match_pct:
                progress_bar.value = int(match_pct.group(1))
            
            match_speed = re.search(r'DL:([^\s]+)', line)
            if match_speed:
                status_label.value = f"Descargando... Velocidad: {match_speed.group(1)}"
        else:
            match_pct = re.search(r'(\d{1,3})%', line)
            if match_pct:
                progress_bar.value = int(match_pct.group(1))
                status_label.value = "Descargando con gdown..."

    process.wait()
    progress_bar.value = 100
    progress_bar.bar_style = 'success'
    status_label.value = "¡Descarga de este archivo completada! ✅"

def generar_metadata_civitai(url, dest_path, pretty_name):
    """Descarga información del modelo desde la API de Civitai y crea el .swarm.json"""
    match = re.search(r'models/(\d+)', url)
    if not match:
        match = re.search(r'modelVersionId=(\d+)', url)
    if not match:
        return

    version_id = match.group(1)

    try:
        display(HTML(f"<p style='color:#4682B4;'>📄 Obteniendo metadata y preview desde Civitai para el ID <code>{version_id}</code>...</p>"))
        
        # Obtener datos de la versión del modelo
        v_resp = requests.get(f"https://civitai.com/api/v1/model-versions/{version_id}", timeout=10)
        if v_resp.status_code != 200:
            display(HTML(f"<p style='color:orange;'>⚠️ No se pudo obtener la metadata (Puede que el modelo esté oculto). Saltando .json...</p>"))
            return
            
        v_data = v_resp.json()

        # Obtener datos generales del modelo (para autor y tags)
        m_id = v_data.get("modelId")
        m_data = {}
        if m_id:
            m_resp = requests.get(f"https://civitai.com/api/v1/models/{m_id}", timeout=10)
            if m_resp.status_code == 200:
                m_data = m_resp.json()

        # Procesar imagen a base64
        # Procesar imagen a base64 (Evitando videos para SwarmUI)
        # Procesar imagen a base64 (Evitando videos y comprimiendo para SwarmUI)
        thumbnail_b64 = ""
        images = v_data.get("images", [])
        
        for img in images:
            img_url = img.get("url")
            if not img_url:
                continue
                
            # Detectar si el archivo es un video
            is_video = img.get("type") == "video" or img_url.lower().endswith(('.mp4', '.webm'))
            
            if is_video:
                continue
                
            try:
                i_resp = requests.get(img_url, timeout=10)
                if i_resp.status_code == 200:
                    # Abrir la imagen en memoria con Pillow
                    img_data = Image.open(BytesIO(i_resp.content))
                    
                    # Convertir a RGB (elimina transparencias/canal alfa para guardar como JPEG sin error)
                    if img_data.mode != 'RGB':
                        img_data = img_data.convert('RGB')
                        
                    # Redimensionar manteniendo la proporción (máximo 512x512)
                    img_data.thumbnail((512, 512), Image.Resampling.LANCZOS)
                    
                    # Guardar la imagen optimizada en un buffer como JPEG
                    buffer = BytesIO()
                    img_data.save(buffer, format="JPEG", quality=80)
                    
                    # Convertir el buffer optimizado a base64
                    b64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    thumbnail_b64 = f"data:image/jpeg;base64,{b64_str}"
                    break # Salimos del loop apenas procesamos la primera imagen
            except Exception as e:
                # Si hay algún error procesando esta imagen, pasamos a la siguiente
                continue

        # Construir diccionario de Swarm
        tags = ", ".join(m_data.get("tags", []))
        trigger_words = ", ".join(v_data.get("trainedWords", []))
        model_name = m_data.get("name", v_data.get("name", "Modelo"))
        version_name = v_data.get("name", "")
        
        desc_html = f'<p>From <a href="https://civitai.com/models/{m_id}?modelVersionId={version_id}" target="_blank">Civitai</a></p><hr />'
        desc_html += v_data.get("description", "") or m_data.get("description", "")

        swarm_metadata = {
            "modelspec.title": f"{model_name} - {version_name}",
            "modelspec.description": desc_html,
            "modelspec.date": v_data.get("createdAt", ""),
            "modelspec.author": m_data.get("creator", {}).get("username", ""),
            "modelspec.trigger_phrase": trigger_words,
            "modelspec.tags": tags,
            "modelspec.thumbnail": thumbnail_b64,
            "modelspec.usage_hint": v_data.get("baseModel", "")
        }

        # Guardar el JSON
        base_name = os.path.splitext(pretty_name)[0]
        if base_name == "Desconocido":
            return
            
        json_filename = f"{base_name}.swarm.json"
        json_path = os.path.join(dest_path, json_filename)
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(swarm_metadata, f, ensure_ascii=False, indent=2)
            
        display(HTML(f"<p style='color:lightgreen;'>✅ Archivo de Swarm <code>{json_filename}</code> creado con éxito.</p>"))

    except Exception as e:
        display(HTML(f"<p style='color:orange;'>⚠️ Error construyendo metadata: {e}</p>"))

@register_line_magic
def download(line):
    """
    %download url1 [-o nombre1.ext], url2, ...
    Muestra solo el nombre real y respeta la carpeta actual (%cd).
    Auto-detecta enlaces de Drive para usar gdown y permite renombrado.
    """
    dest = os.getcwd()
    # Separar por comas para soportar múltiples descargas en la misma línea
    items = [item.strip() for item in line.split(",") if item.strip()]

    for item in items:
        # Extraer URL y el posible nombre personalizado usando regex para atrapar " -o "
        parts = re.split(r'\s+-o\s+', item, maxsplit=1)
        url = parts[0].strip()
        custom_name = parts[1].strip() if len(parts) > 1 else None

        # ---------- Google Drive (gdown) ----------
        if "drive.google.com" in url:
            is_folder = "/folders/" in url
            tipo = "Carpeta" if is_folder else "Archivo"
            
            pretty = custom_name if custom_name else f"{tipo} de Google Drive (Gdown gestiona el nombre)"
            display(HTML(f"<hr><h3 style='color:yellow;'>🛸 Descargando (gdown): <code>{pretty}</code></h3>"
                         f"<h4 style='color:cyan;'>📁 Destino: <code>{dest}</code></h4>"))
            
            cmd = ["gdown"]
            if is_folder:
                cmd.append("--folder")
            else:
                cmd.append("--fuzzy")
            
            cmd.append(url)
            
            # Si hay nombre custom, le damos la ruta exacta, si no, el directorio
            if custom_name:
                cmd.extend(["-O", os.path.join(dest, custom_name)])
            else:
                cmd.extend(["-O", f"{dest}/"]) 
            
            ejecutar_con_progreso(cmd, is_gdown=True)

        # ---------- CivitAI y CivitaiArchive (aria2) ----------
        elif "civitai.com" in url or "civitaiarchive.com" in url:
            if not token and "civitai.com" in url:
                display(HTML("<h4 style='color:red;'>⚠️ Token de CivitAI no encontrado (algunos modelos pueden fallar).</h4>"))
            
            url_token = url
            if token and ("civitai.com" in url or "civitaiarchive.com" in url):
                url_token = f"{url}{'&' if '?' in url else '?'}token={token}"

            # Si el usuario mandó nombre manual, lo usamos. Si no, consultamos la API para saberlo.
            if custom_name:
                pretty = custom_name
            else:
                try:
                    with requests.get(url_token, stream=True, timeout=5) as r:
                        cd = r.headers.get('Content-Disposition', '')
                        match = re.findall(r'filename[*]?=(?:UTF-8\'\')?["\']?([^"\';]+)["\']?', cd)
                        pretty = match[0] if match else url.split('/')[-1].split('?')[0]
                except Exception:
                    pretty = url.split('/')[-1].split('?')[0]

            display(HTML(f"<hr><h3 style='color:yellow;'>📥 Descargando (aria2): <code>{pretty}</code></h3>"
                         f"<h4 style='color:cyan;'>📁 Destino: <code>{dest}</code></h4>"))

            cmd = [
                "aria2c", "--summary-interval=1",
                "-c", "-x", "16", "-s", "16", "-k", "1M",
                "-d", dest
            ]
            
            # Si hay nombre personalizado, usamos -o. Si no, usamos content-disposition
            if custom_name:
                cmd.extend(["-o", custom_name])
            else:
                cmd.append("--content-disposition")
                
            cmd.append(url_token)
            ejecutar_con_progreso(cmd, is_gdown=False)

            # Generar metadata de Civitai al finalizar
            if pretty and pretty != "Desconocido":
                generar_metadata_civitai(url, dest, pretty)

        # ---------- HuggingFace / Otros (aria2) ----------
        else:
            pretty = custom_name if custom_name else url.split('/')[-1].split('?')[0]
            display(HTML(f"<hr><h3 style='color:yellow;'>📥 Descargando (aria2): <code>{pretty}</code></h3>"
                         f"<h4 style='color:cyan;'>📁 Destino: <code>{dest}</code></h4>"))
            
            cmd = [
                "aria2c", "--summary-interval=1",
                "-c", "-x", "16", "-s", "16", "-k", "1M",
                "-d", dest
            ]
            
            if custom_name:
                cmd.extend(["-o", custom_name])
            else:
                cmd.extend(["-o", pretty])
                
            cmd.append(url)
            ejecutar_con_progreso(cmd, is_gdown=False)

            # Limpiar hashes de 64 caracteres típicos de HuggingFace si quedó suelto y no hay nombre custom
            if not custom_name and ("huggingface.co" in url):
                for f in os.listdir(dest):
                    if re.fullmatch(r'[0-9a-f]{64}', f):
                        os.rename(os.path.join(dest, f), os.path.join(dest, pretty))
                        break

# Registramos la línea mágica al importar el módulo
get_ipython().register_magic_function(download, magic_kind='line')