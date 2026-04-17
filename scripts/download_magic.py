# download_magic.py
"""
Mágica %download para IPython / Jupyter / Colab.
Lee el token de CivitAI desde ~/.civitai_token.pkl (pickle)
Incluye barra de progreso interactiva, renombrado con -o y autogeneración de metadata (.json y .png) para Forge.
Resuelve redirecciones de Civitai, captura errores y evita conflictos de headers S3 (Error 400).

Uso:
    import download_magic
    %download https://civitai.com/api/download/models/..., https://huggingface.co/...
    %download https://drive.google.com/file/d/123.../view -o MiModelo.safetensors
"""

from IPython import get_ipython
from IPython.core.magic import register_line_magic
from IPython.display import HTML, display, clear_output
import ipywidgets as widgets
import os
import subprocess
import re
import requests
import pickle
import json
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
    """Ejecuta el comando leyendo la salida para animar la barra de progreso y captura errores."""
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
    
    log_salida = []
    
    for line in process.stdout:
        line_clean = line.strip()
        if line_clean:
            log_salida.append(line_clean)
            if len(log_salida) > 20:
                log_salida.pop(0)

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
    
    if process.returncode != 0:
        progress_bar.bar_style = 'danger'
        status_label.value = f"❌ Error en la descarga (Código de error: {process.returncode})"
        
        error_details = "<br>".join(log_salida)
        display(HTML(f"""
        <div style='color:#a94442; background-color:#f2dede; border-color:#ebccd1; padding:10px; border-radius:5px; margin-top:5px; font-family:monospace; font-size:12px;'>
            <b>Detalles del error (últimas líneas del log):</b><br>
            {error_details}
        </div>
        """))
        return False
    else:
        progress_bar.value = 100
        progress_bar.bar_style = 'success'
        status_label.value = "¡Descarga de este archivo completada! ✅"
        return True


def generar_metadata_civitai_forge(url, dest_path, pretty_name):
    """Descarga información del modelo desde la API de Civitai y crea el .json y .png para Forge"""
    match = re.search(r'models/(\d+)', url)
    if not match:
        match = re.search(r'modelVersionId=(\d+)', url)
    if not match:
        return

    version_id = match.group(1)

    try:
        display(HTML(f"<p style='color:#4682B4;'>📄 Obteniendo metadata y preview para Forge (ID: <code>{version_id}</code>)...</p>"))
        
        v_resp = requests.get(f"https://civitai.com/api/v1/model-versions/{version_id}", timeout=10)
        if v_resp.status_code != 200:
            display(HTML(f"<p style='color:orange;'>⚠️ No se pudo obtener la metadata. Saltando preview y .json...</p>"))
            return
            
        v_data = v_resp.json()
        base_name = os.path.splitext(pretty_name)[0]
        
        if base_name == "Desconocido":
            return

        images = v_data.get("images", [])
        if images:
            img_url = images[0].get("url")
            if img_url:
                try:
                    i_resp = requests.get(img_url, timeout=10)
                    if i_resp.status_code == 200:
                        img_path = os.path.join(dest_path, f"{base_name}.png")
                        with open(img_path, "wb") as f_img:
                            f_img.write(i_resp.content)
                        display(HTML(f"<p style='color:lightgreen;'>🖼️ Imagen preview <code>{base_name}.png</code> guardada.</p>"))
                except Exception as e:
                    pass

        trained_words = v_data.get("trainedWords", [])
        activation_text = ", ".join(trained_words)
        sd_version = v_data.get("baseModel", "Unknown")
        model_id = v_data.get("modelId", 0)
        model_version_id = v_data.get("id", 0)
        
        sha256 = ""
        files = v_data.get("files", [])
        for f in files:
            if "hashes" in f and "SHA256" in f["hashes"]:
                sha256 = f["hashes"]["SHA256"]
                break

        forge_metadata = {
            "activation text": activation_text,
            "sd version": sd_version,
            "modelId": model_id,
            "modelVersionId": model_version_id,
            "sha256": sha256
        }

        json_filename = f"{base_name}.json"
        json_path = os.path.join(dest_path, json_filename)
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(forge_metadata, f, ensure_ascii=False, indent=4)
            
        display(HTML(f"<p style='color:lightgreen;'>✅ Archivo de metadata <code>{json_filename}</code> creado.</p>"))

    except Exception as e:
        display(HTML(f"<p style='color:orange;'>⚠️ Error construyendo metadata: {e}</p>"))


@register_line_magic
def download(line):
    """
    %download url1 [-o nombre1.ext], url2, ...
    Muestra solo el nombre real y respeta la carpeta actual (%cd).
    """
    dest = os.getcwd()
    items = [item.strip() for item in line.split(",") if item.strip()]

    for item in items:
        parts = re.split(r'\s+-o\s+', item, maxsplit=1)
        url = parts[0].strip()
        custom_name = parts[1].strip() if len(parts) > 1 else None

        # ---------- Google Drive (gdown) ----------
        if "drive.google.com" in url:
            is_folder = "/folders/" in url
            tipo = "Carpeta" if is_folder else "Archivo"
            
            pretty = custom_name if custom_name else f"{tipo} de Google Drive"
            display(HTML(f"<hr><h3 style='color:yellow;'>🛸 Descargando (gdown): <code>{pretty}</code></h3>"
                         f"<h4 style='color:cyan;'>📁 Destino: <code>{dest}</code></h4>"))
            
            cmd = ["gdown"]
            if is_folder: cmd.append("--folder")
            else: cmd.append("--fuzzy")
            
            cmd.append(url)
            
            if custom_name: cmd.extend(["-O", os.path.join(dest, custom_name)])
            else: cmd.extend(["-O", f"{dest}/"]) 
            
            ejecutar_con_progreso(cmd, is_gdown=True)

        # ---------- CivitAI y CivitaiArchive (aria2 con preflight) ----------
        elif "civitai.com" in url or "civitai.red" in url or "civitaiarchive.com" in url:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            headers = {'User-Agent': user_agent}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            elif "civitai.com" in url or "civitai.red" in url:
                display(HTML("<h4 style='color:orange;'>⚠️ Token de CivitAI no encontrado.</h4>"))

            final_url = url
            pretty = custom_name
            
            try:
                with requests.get(url, headers=headers, stream=True, allow_redirects=True, timeout=15) as r:
                    final_url = r.url
                    if not pretty:
                        cd = r.headers.get('Content-Disposition', '')
                        match = re.findall(r'filename[*]?=(?:UTF-8\'\')?["\']?([^"\';]+)["\']?', cd)
                        pretty = match[0] if match else url.split('/')[-1].split('?')[0]
            except Exception as e:
                display(HTML(f"<p style='color:orange;'>⚠️ Error en preflight: {e}.</p>"))
                if not pretty:
                    pretty = url.split('/')[-1].split('?')[0]

            display(HTML(f"<hr><h3 style='color:yellow;'>📥 Descargando (aria2): <code>{pretty}</code></h3>"
                         f"<h4 style='color:cyan;'>📁 Destino: <code>{dest}</code></h4>"))

            cmd = [
                "aria2c", "--summary-interval=1",
                "-c", "-x", "16", "-s", "16", "-k", "1M",
                f"--header=User-Agent: {user_agent}",
                "-d", dest
            ]
            
            # EL ARREGLO DEL ERROR 400 DE CLOUDFLARE/S3
            if token and "X-Amz-Signature" not in final_url: 
                cmd.append(f"--header=Authorization: Bearer {token}")
            
            if pretty: cmd.extend(["-o", pretty])
            else: cmd.append("--content-disposition")
                
            cmd.append(final_url)
            
            exito = ejecutar_con_progreso(cmd, is_gdown=False)
            if exito and pretty and pretty != "Desconocido":
                generar_metadata_civitai_forge(url, dest, pretty)

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
            
            if custom_name: cmd.extend(["-o", custom_name])
            else: cmd.extend(["-o", pretty])
                
            cmd.append(url)
            ejecutar_con_progreso(cmd, is_gdown=False)

            if not custom_name and ("huggingface.co" in url):
                for f in os.listdir(dest):
                    if re.fullmatch(r'[0-9a-f]{64}', f):
                        os.rename(os.path.join(dest, f), os.path.join(dest, pretty))
                        break

# Registramos la línea mágica al importar el módulo
get_ipython().register_magic_function(download, magic_kind='line')