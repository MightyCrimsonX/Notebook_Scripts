import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import os
import subprocess
import requests
import re
import pickle
import json
import base64
from pathlib import Path

# --- Diccionarios de Modelos Predefinidos ---
PRESET_MODELS = {
    "WaiNSFW V16": "https://huggingface.co/Quiho/best-from-civitai/resolve/main/waiIllustriousSDXL_v160.safetensors",
    "WaiNSFW V15": "https://huggingface.co/WhiteAiZ/WAI-NSFW-illustrious-SDXL-V015/resolve/main/waiNSFWIllustrious_v150.safetensors",
    "waiNSFW V14": "https://huggingface.co/Ine007/waiNSFWIllustrious_v140/resolve/main/waiNSFWIllustrious_v140.safetensors",
    "waiSHUFFLENOOB_v20": "https://huggingface.co/WhiteAiZ/waiSHUFFLENOOB_v20/resolve/main/waiSHUFFLENOOB_v20.safetensors",
    "waiSHUFFLENOOB_vpred20": "https://huggingface.co/WhiteAiZ/waiSHUFFLENOOB_v20/resolve/main/waiSHUFFLENOOB_vPred20.safetensors",
    "ntrMIXIllustriousXL_XIII": "https://huggingface.co/misri/ntrMIXIllustriousXL_xiii/resolve/main/ntrMIXIllustriousXL_xiii.safetensors",
    "NoobaiCyberFix": "https://civitaiarchive.com/api/download/models/1122850",
    "NoobaiCyberFix vpred": "https://civitaiarchive.com/api/download/models/2371102",
    "konanMix Vpred": "https://huggingface.co/wsj1995/Checkpoint/resolve/main/1365468/1542670/konanmixnoobvPredNoob_v10.safetensors",
    "Nova Anime XL": "https://huggingface.co/Chattiori/ChattioriMixesXL/resolve/main/NovaAnimeILV8.safetensors",
    "Illustrious XL personal merge": "https://huggingface.co/nnnn1111/models/resolve/main/illustriousXLPersonalMerge_v30Noob10based.safetensors",
    "Illustrious XL personal merge vpred": "https://huggingface.co/datasets/John6666/model-mirror-14/resolve/main/illustriousXLPersonalMerge_vp05testLowsteps.safetensors",
    "Ikastrious v20.1": "https://civitai.com/api/download/models/2641077?type=Model&format=SafeTensor&size=full&fp=fp16",
    "Ikastrious Noobai": "https://huggingface.co/minaiosu/giko/resolve/main/ikastrious_v95.safetensors",
    "RouWei": "https://civitaiarchive.com/api/download/models/1832460",
    "RouWei Vpred": "https://huggingface.co/WhiteAiZ/RouWei/resolve/main/rouwei_v080Vpred.safetensors",
    "PlantMint Walnut": "https://huggingface.co/wsj1995/Checkpoint/resolve/main/1162518/1714002/plantMilkModelSuite_walnut.safetensors"
}

PRESET_VAES = {
    "sdxl_vae": "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors",
    "sdxl_vae_fix": "https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl_vae.safetensors",
    "sdxl_anime_vae": "https://huggingface.co/Anzhc/Anzhcs-VAEs/resolve/main/SDXL%20Anime%20VAE%20Dec-only%20B3.safetensors",
    "sdxl_neptunia_vae": "https://huggingface.co/JustAnotherCibrarian/vae/resolve/main/1290283/1455983/neptuniaXLILNAIVAE_contrastColors.safetensors",
    "sdxl_luna_vae": "https://huggingface.co/yuu062/tameshi/resolve/main/lunaXLVAE_luna.safetensors",
    "XL_VAE_G9": "https://civitai.com/api/download/models/1191929?type=Model&format=SafeTensor"
}

PRESET_UPSCALERS = {
    "AnimeSharp": "https://huggingface.co/Kim2091/AnimeSharp/resolve/main/4x-AnimeSharp.pth",
    "UltraSharp": "https://huggingface.co/lokCX/4x-Ultrasharp/resolve/main/4x-UltraSharp.pth",
    "Remacri": "https://huggingface.co/LyliaEngine/remacri_original/resolve/main/remacri_original.pt",
    "RealESRGAN_x4plus_anime": "https://huggingface.co/gemasai/RealESRGAN_x4plus_anime_6B/resolve/main/RealESRGAN_x4plus_anime_6B.pth",
    "JaNai": "https://huggingface.co/halllooo/4x_illustrationJaNaiV1/resolve/main/4x_IllustrationJaNai_V1_ESRGAN_135k.pth",
    "YandereNeoXL": "https://huggingface.co/kaeru-shigure/mlx-4x_NMKD-YandereNeoXL_200k/resolve/main/4x_NMKD-YandereNeoXL_200k.safetensors"
}

PRESET_CONTROLNETS = {
    "Controlnet Union Pro Max": "https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/resolve/main/diffusion_pytorch_model_promax.safetensors",
    "Controlnet Lite (Todos)": "https://huggingface.co/bdsqlsz/qinglong_controlnet-lllite/resolve/main/bdsqlsz_controlllite_xl_sketch.safetensors, https://huggingface.co/bdsqlsz/qinglong_controlnet-lllite/resolve/main/bdsqlsz_controlllite_xl_softedge.safetensors, https://huggingface.co/bdsqlsz/qinglong_controlnet-lllite/resolve/main/bdsqlsz_controlllite_xl_dw_openpose.safetensors, https://huggingface.co/bdsqlsz/qinglong_controlnet-lllite/resolve/main/bdsqlsz_controlllite_xl_canny.safetensors, https://huggingface.co/bdsqlsz/qinglong_controlnet-lllite/resolve/main/bdsqlsz_controlllite_xl_depth_V2.safetensors, https://huggingface.co/bdsqlsz/qinglong_controlnet-lllite/resolve/main/bdsqlsz_controlllite_xl_lineart_anime_denoise.safetensors"
}

PRESET_DIFFUSION = {
    "z-image-turbo-Q4_K_M": "https://huggingface.co/unsloth/Z-Image-Turbo-GGUF/resolve/main/z-image-turbo-Q4_K_M.gguf",
    "z-image-turbo-Q8_0": "https://huggingface.co/unsloth/Z-Image-Turbo-GGUF/resolve/main/z-image-turbo-Q8_0.gguf"
}

PRESET_TEXT_ENCODERS = {
    "Qwen3-4B-Q4_K_M": "https://huggingface.co/unsloth/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q4_K_M.gguf",
    "Qwen3-4B-Q8_0": "https://huggingface.co/unsloth/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q8_0.gguf"
}

PRESET_UNET = {} 
PRESET_CLIP = {} 

def iniciar():
    # --- Configuración de Rutas para Kaggle ---
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
    os.makedirs(COMFY_EXT_DIR, exist_ok=True)

    # --- Leer token desde pickle en Kaggle ---
    TOKEN_FILE = Path.home() / ".civitai_token.pkl"
    token_guardado = ""
    if TOKEN_FILE.exists():
        try:
            token_guardado = pickle.loads(TOKEN_FILE.read_bytes())
        except Exception:
            pass

    # --- Elementos de la Interfaz ---
    out_console = widgets.Output(layout={'border': '1px solid #ccc', 'padding': '10px', 'margin': '10px 0', 'height': '250px', 'overflow': 'auto'})

    token_input = widgets.Password(
        value=token_guardado,
        placeholder='Ingresa tu API Token (Opcional pero recomendado)',
        description='Civitai Token:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='500px')
    )

    # Widgets de Progreso
    progress_bar = widgets.IntProgress(
        value=0, min=0, max=100, 
        description='Progreso:', 
        bar_style='info', 
        orientation='horizontal', 
        layout=widgets.Layout(width='80%', display='none')
    )
    status_label = widgets.Label(value="", layout=widgets.Layout(display='none'))
    progress_container = widgets.VBox([progress_bar, status_label])

    def ejecutar_con_progreso(cmd, is_gdown=False):
        progress_bar.value = 0
        progress_bar.layout.display = 'flex'
        status_label.layout.display = 'flex'
        status_label.value = "Iniciando descarga..."
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
        
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
        status_label.value = "¡Descarga completada! ✅"

    def generar_metadata_civitai(url, dest_path, pretty_name):
        """Descarga información del modelo desde la API de Civitai y crea el .swarm.json"""
        match = re.search(r'models/(\d+)', url)
        if not match:
            match = re.search(r'modelVersionId=(\d+)', url)
        if not match:
            return

        version_id = match.group(1)

        try:
            with out_console:
                display(HTML(f"<p style='color:#4682B4;'>📄 Obteniendo metadata y preview desde Civitai para el ID <code>{version_id}</code>...</p>"))
            
            # Obtener datos de la versión del modelo
            v_resp = requests.get(f"https://civitai.com/api/v1/model-versions/{version_id}", timeout=10)
            if v_resp.status_code != 200:
                with out_console:
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
            thumbnail_b64 = ""
            images = v_data.get("images", [])
            if images:
                img_url = images[0].get("url")
                if img_url:
                    try:
                        i_resp = requests.get(img_url, timeout=10)
                        if i_resp.status_code == 200:
                            content_type = i_resp.headers.get('content-type', 'image/jpeg')
                            b64_str = base64.b64encode(i_resp.content).decode('utf-8')
                            thumbnail_b64 = f"data:{content_type};base64,{b64_str}"
                    except Exception:
                        pass

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
                
            with out_console:
                display(HTML(f"<p style='color:lightgreen;'>✅ Archivo de Swarm <code>{json_filename}</code> creado con éxito.</p>"))

        except Exception as e:
            with out_console:
                display(HTML(f"<p style='color:orange;'>⚠️ Error construyendo metadata: {e}</p>"))

    def procesar_descarga(b, url_widget, method_widget, dest_path):
        raw_urls = url_widget.value.strip()
        method = method_widget.value
        token = token_input.value.strip()
        
        urls = [u.strip() for u in raw_urls.split(",") if u.strip()]
        
        if not urls:
            with out_console:
                clear_output()
                display(HTML("<h4 style='color:red;'>⚠️ Por favor, ingresa al menos una URL válida.</h4>"))
            return

        with out_console:
            clear_output()
            display(HTML(f"<h2>🚀 Iniciando cola de descarga: {len(urls)} archivo(s)</h2>"))

        for i, url in enumerate(urls, 1):
            progress_bar.bar_style = 'info'
            progress_bar.value = 0
            status_label.value = f"Preparando archivo {i} de {len(urls)}..."

            download_url = url
            if ("civitai.com" in url or "civitaiarchive.com" in url) and token:
                download_url = f"{url}{'&' if '?' in url else '?'}token={token}"

            pretty_name = "Desconocido"
            
            if url == "https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/resolve/main/diffusion_pytorch_model_promax.safetensors":
                pretty_name = "Controlnet_Union_Pro_Max.safetensors"
            if url == "https://huggingface.co/Anzhc/Anzhcs-VAEs/resolve/main/SDXL%20Anime%20VAE%20Dec-only%20B3.safetensors":
                pretty_name = "SDXL_Anime_Vae.safetensors"
            elif method == 'aria2':
                if "civitai.com" in url or "civitaiarchive.com" in url:
                    try:
                        with requests.get(download_url, stream=True, timeout=5) as r:
                            cd = r.headers.get('Content-Disposition', '')
                            match = re.findall(r'filename[*]?=(?:UTF-8\'\')?["\']?([^"\';]+)["\']?', cd)
                            if match: 
                                pretty_name = match[0]
                            else:
                                pretty_name = url.split('/')[-1].split('?')[0]
                    except Exception:
                        pretty_name = url.split('/')[-1].split('?')[0]
                else:
                    pretty_name = url.split('/')[-1].split('?')[0]
            elif method == 'gdown':
                pretty_name = "Archivo de Google Drive (Gdown gestiona el nombre)"

            with out_console:
                display(HTML(f"<hr><h3 style='color:#D4AF37;'>📥 [{i}/{len(urls)}] Descargando: <code>{pretty_name}</code></h3>"))
                display(HTML(f"<h4 style='color:#4682B4;'>📁 Destino: <code>{dest_path}</code></h4>"))
                
                if ("civitai.com" in url or "civitaiarchive.com" in url) and token:
                    print("🔑 Token detectado y aplicado desde el gestor.")
                elif ("civitai.com" in url or "civitaiarchive.com" in url) and not token:
                    print("⚠️ Descargando sin token (algunos modelos pueden requerirlo).")

            if method == 'aria2':
                cmd = [
                    "aria2c", "--content-disposition",
                    "-c", "-x", "16", "-s", "16", "-k", "1M",
                    "--summary-interval=1", "-d", dest_path
                ]
                
                if pretty_name and pretty_name != "Desconocido" and "civitai.com" not in url and "civitaiarchive.com" not in url:
                    cmd.extend(["-o", pretty_name, url])
                else:
                    cmd.append(download_url)
                    
                ejecutar_con_progreso(cmd, is_gdown=False)
                
                if "huggingface.co" in url and pretty_name:
                    for f in os.listdir(dest_path):
                        if re.fullmatch(r'[0-9a-f]{64}', f):
                            os.rename(os.path.join(dest_path, f), os.path.join(dest_path, pretty_name))
                            break

            elif method == 'gdown':
                cmd = ["gdown", "--fuzzy", url, "-O", f"{dest_path}/"]
                ejecutar_con_progreso(cmd, is_gdown=True)

            # --- Crear el JSON si es de Civitai ---
            if pretty_name and pretty_name != "Desconocido":
                if "civitai.com" in url or "civitaiarchive.com" in url:
                    generar_metadata_civitai(url, dest_path, pretty_name)

        with out_console:
            display(HTML("<hr><h2 style='color:lightgreen;'>✅ ¡Todas las descargas han finalizado!</h2>"))

    def procesar_extensiones(b, url_widget):
        raw_urls = url_widget.value.strip()
        urls = [u.strip() for u in raw_urls.split(",") if u.strip()]
        
        if not urls:
            with out_console:
                clear_output()
                display(HTML("<h4 style='color:red;'>⚠️ Por favor, ingresa al menos una URL de GitHub válida.</h4>"))
            return

        with out_console:
            clear_output()
            display(HTML(f"<h2>🚀 Iniciando clonación de {len(urls)} extensión(es)</h2>"))

        for i, url in enumerate(urls, 1):
            progress_bar.layout.display = 'flex'
            status_label.layout.display = 'flex'
            progress_bar.bar_style = 'info'
            progress_bar.value = 50 
            
            repo_name = url.rstrip('/').split('/')[-1].replace('.git', '')
            target_path = os.path.join(COMFY_EXT_DIR, repo_name)
            status_label.value = f"Clonando {repo_name} ({i}/{len(urls)})..."

            with out_console:
                display(HTML(f"<hr><h3 style='color:#D4AF37;'>📥 [{i}/{len(urls)}] Clonando: <code>{repo_name}</code></h3>"))
                display(HTML(f"<h4 style='color:#4682B4;'>📁 Destino: <code>{target_path}</code></h4>"))

            if os.path.exists(target_path):
                with out_console:
                    print(f"⚠️ La carpeta {repo_name} ya existe. Saltando git clone...")
            else:
                cmd_clone = ["git", "clone", url, target_path]
                res_clone = subprocess.run(cmd_clone, capture_output=True, text=True)
                if res_clone.returncode != 0:
                    with out_console:
                        print(f"❌ Error al clonar:\n{res_clone.stderr}")
                    continue

            req_file = os.path.join(target_path, "requirements.txt")
            if os.path.exists(req_file):
                status_label.value = f"Instalando dependencias para {repo_name}..."
                with out_console:
                    print(f"📦 requirements.txt detectado. Instalando con uv...")
                
                cmd_uv = ["uv", "pip", "install", "--system", "-r", req_file]
                res_uv = subprocess.run(cmd_uv, capture_output=True, text=True)
                
                with out_console:
                    if res_uv.returncode == 0:
                        print("✅ Dependencias instaladas exitosamente.")
                    else:
                        print(f"⚠️ Hubo un problema al instalar algunas dependencias:\n{res_uv.stderr}")
            else:
                with out_console:
                    print("ℹ️ No se encontró requirements.txt. Omitiendo instalación de dependencias.")

            progress_bar.value = 100
            progress_bar.bar_style = 'success'
            status_label.value = "¡Extensión procesada! ✅"

        with out_console:
            display(HTML("<hr><h2 style='color:lightgreen;'>✅ ¡Todas las extensiones han sido procesadas!</h2>"))


    # --- Pestaña 1: Modelos Base ---
    opciones_presets_base = ['-- Personalizado / Manual --'] + list(PRESET_MODELS.keys())
    preset_base_dropdown = widgets.Dropdown(options=opciones_presets_base, value='-- Personalizado / Manual --', description='Favoritos:', layout=widgets.Layout(width='80%'))
    base_url = widgets.Text(placeholder='https://url1, https://url2, ...', description='URL:', layout=widgets.Layout(width='80%'))

    def actualizar_url_base(change):
        seleccion = change['new']
        if seleccion in PRESET_MODELS:
            base_url.value = PRESET_MODELS[seleccion]
        else:
            base_url.value = ""

    preset_base_dropdown.observe(actualizar_url_base, names='value')

    base_method = widgets.Dropdown(options=['aria2', 'gdown'], value='aria2', description='Método:')
    base_btn = widgets.Button(description='Descargar Modelos', button_style='primary', icon='download')
    base_btn.on_click(lambda b: procesar_descarga(b, base_url, base_method, BASE_MODELS_DIR))

    tab_base = widgets.VBox([
        widgets.HTML("<h4>Descargar Modelos (Checkpoints)</h4><p>Elige un modelo favorito o pega enlaces separados por comas (,)</p>"),
        preset_base_dropdown,
        widgets.HBox([base_url, base_method]),
        base_btn
    ])

    # --- Pestaña 2: LoRAs ---
    lora_url = widgets.Text(placeholder='https://url1, https://url2, ...', description='URLs:', layout=widgets.Layout(width='80%'))
    lora_method = widgets.Dropdown(options=['aria2', 'gdown'], value='aria2', description='Método:')
    lora_btn = widgets.Button(description='Descargar LoRAs', button_style='success', icon='download')
    lora_btn.on_click(lambda b: procesar_descarga(b, lora_url, lora_method, LORA_DIR))

    tab_lora = widgets.VBox([
        widgets.HTML("<h4>Descargar LoRAs</h4><p>Pega múltiples URLs separadas por comas (,)</p>"),
        widgets.HBox([lora_url, lora_method]),
        lora_btn
    ])

    # --- Pestaña 3: VAEs ---
    opciones_presets_vae = ['-- Personalizado / Manual --'] + list(PRESET_VAES.keys())
    preset_vae_dropdown = widgets.Dropdown(options=opciones_presets_vae, value='-- Personalizado / Manual --', description='Favoritos:', layout=widgets.Layout(width='80%'))
    vae_url = widgets.Text(placeholder='https://url1, https://url2, ...', description='URL:', layout=widgets.Layout(width='80%'))

    def actualizar_url_vae(change):
        seleccion = change['new']
        if seleccion in PRESET_VAES:
            vae_url.value = PRESET_VAES[seleccion]
        else:
            vae_url.value = ""

    preset_vae_dropdown.observe(actualizar_url_vae, names='value')

    vae_method = widgets.Dropdown(options=['aria2', 'gdown'], value='aria2', description='Método:')
    vae_btn = widgets.Button(description='Descargar VAEs', button_style='info', icon='download')
    vae_btn.on_click(lambda b: procesar_descarga(b, vae_url, vae_method, VAE_DIR))

    tab_vae = widgets.VBox([
        widgets.HTML("<h4>Descargar VAEs</h4><p>Elige un VAE favorito o pega enlaces separados por comas (,)</p>"),
        preset_vae_dropdown,
        widgets.HBox([vae_url, vae_method]),
        vae_btn
    ])

    # --- Pestaña 4: Upscalers ---
    opciones_presets_upscalers = ['-- Personalizado / Manual --', '-- Descargar Todos --'] + list(PRESET_UPSCALERS.keys())
    preset_upscaler_dropdown = widgets.Dropdown(options=opciones_presets_upscalers, value='-- Personalizado / Manual --', description='Favoritos:', layout=widgets.Layout(width='80%'))
    upscaler_url = widgets.Text(placeholder='https://url1, https://url2, ...', description='URL:', layout=widgets.Layout(width='80%'))

    def actualizar_url_upscaler(change):
        seleccion = change['new']
        if seleccion == '-- Descargar Todos --':
            upscaler_url.value = ", ".join(PRESET_UPSCALERS.values())
        elif seleccion in PRESET_UPSCALERS:
            upscaler_url.value = PRESET_UPSCALERS[seleccion]
        else:
            upscaler_url.value = ""

    preset_upscaler_dropdown.observe(actualizar_url_upscaler, names='value')

    upscaler_method = widgets.Dropdown(options=['aria2', 'gdown'], value='aria2', description='Método:')
    upscaler_btn = widgets.Button(description='Descargar Upscalers', button_style='warning', icon='download')
    upscaler_btn.on_click(lambda b: procesar_descarga(b, upscaler_url, upscaler_method, UPSCALER_DIR))

    tab_upscaler = widgets.VBox([
        widgets.HTML("<h4>Descargar Upscalers (ESRGAN)</h4><p>Elige un upscaler, selecciona <b>'-- Descargar Todos --'</b>, o pega enlaces separados por comas (,)</p>"),
        preset_upscaler_dropdown,
        widgets.HBox([upscaler_url, upscaler_method]),
        upscaler_btn
    ])

    # --- Pestaña 5: ControlNet ---
    opciones_presets_controlnet = ['-- Personalizado / Manual --'] + list(PRESET_CONTROLNETS.keys())
    preset_controlnet_dropdown = widgets.Dropdown(options=opciones_presets_controlnet, value='-- Personalizado / Manual --', description='Favoritos:', layout=widgets.Layout(width='80%'))
    controlnet_url = widgets.Text(placeholder='https://url1, https://url2, ...', description='URL:', layout=widgets.Layout(width='80%'))

    def actualizar_url_controlnet(change):
        seleccion = change['new']
        if seleccion in PRESET_CONTROLNETS:
            controlnet_url.value = PRESET_CONTROLNETS[seleccion]
        else:
            controlnet_url.value = ""

    preset_controlnet_dropdown.observe(actualizar_url_controlnet, names='value')

    controlnet_method = widgets.Dropdown(options=['aria2', 'gdown'], value='aria2', description='Método:')
    controlnet_btn = widgets.Button(description='Descargar ControlNet', button_style='danger', icon='download')
    controlnet_btn.on_click(lambda b: procesar_descarga(b, controlnet_url, controlnet_method, CONTROLNET_DIR))

    tab_controlnet = widgets.VBox([
        widgets.HTML("<h4>Descargar Modelos ControlNet</h4><p>Elige el Pro Max, el paquete Lite, o pega enlaces separados por comas (,)</p>"),
        preset_controlnet_dropdown,
        widgets.HBox([controlnet_url, controlnet_method]),
        controlnet_btn
    ])

    # --- Pestaña 6: Diffusion Models ---
    opciones_presets_diffusion = ['-- Personalizado / Manual --'] + list(PRESET_DIFFUSION.keys())
    preset_diffusion_dropdown = widgets.Dropdown(options=opciones_presets_diffusion, value='-- Personalizado / Manual --', description='Favoritos:', layout=widgets.Layout(width='80%'))
    diffusion_url = widgets.Text(placeholder='https://url1, https://url2, ...', description='URL:', layout=widgets.Layout(width='80%'))

    def actualizar_url_diffusion(change):
        seleccion = change['new']
        if seleccion in PRESET_DIFFUSION:
            diffusion_url.value = PRESET_DIFFUSION[seleccion]
        else:
            diffusion_url.value = ""

    preset_diffusion_dropdown.observe(actualizar_url_diffusion, names='value')

    diffusion_method = widgets.Dropdown(options=['aria2', 'gdown'], value='aria2', description='Método:')
    diffusion_btn = widgets.Button(description='Descargar Diffusion Models', button_style='primary', icon='download')
    diffusion_btn.on_click(lambda b: procesar_descarga(b, diffusion_url, diffusion_method, DIFFUSION_DIR))

    tab_diffusion = widgets.VBox([
        widgets.HTML("<h4>Descargar Diffusion Models</h4><p>Elige un modelo GGUF o pega enlaces separados por comas (,)</p>"),
        preset_diffusion_dropdown,
        widgets.HBox([diffusion_url, diffusion_method]),
        diffusion_btn
    ])

    # --- Pestaña 7: Text Encoders ---
    opciones_presets_te = ['-- Personalizado / Manual --'] + list(PRESET_TEXT_ENCODERS.keys())
    preset_te_dropdown = widgets.Dropdown(options=opciones_presets_te, value='-- Personalizado / Manual --', description='Favoritos:', layout=widgets.Layout(width='80%'))
    te_url = widgets.Text(placeholder='https://url1, https://url2, ...', description='URL:', layout=widgets.Layout(width='80%'))

    def actualizar_url_te(change):
        seleccion = change['new']
        if seleccion in PRESET_TEXT_ENCODERS:
            te_url.value = PRESET_TEXT_ENCODERS[seleccion]
        else:
            te_url.value = ""

    preset_te_dropdown.observe(actualizar_url_te, names='value')

    te_method = widgets.Dropdown(options=['aria2', 'gdown'], value='aria2', description='Método:')
    te_btn = widgets.Button(description='Descargar Text Encoders', button_style='info', icon='download')
    te_btn.on_click(lambda b: procesar_descarga(b, te_url, te_method, TEXT_ENCODER_DIR))

    tab_te = widgets.VBox([
        widgets.HTML("<h4>Descargar Text Encoders</h4><p>Elige un modelo Qwen o pega enlaces separados por comas (,)</p>"),
        preset_te_dropdown,
        widgets.HBox([te_url, te_method]),
        te_btn
    ])

    # --- Pestaña 8: Unet ---
    opciones_presets_unet = ['-- Personalizado / Manual --'] + list(PRESET_UNET.keys())
    preset_unet_dropdown = widgets.Dropdown(options=opciones_presets_unet, value='-- Personalizado / Manual --', description='Favoritos:', layout=widgets.Layout(width='80%'))
    unet_url = widgets.Text(placeholder='https://url1, https://url2, ...', description='URL:', layout=widgets.Layout(width='80%'))

    def actualizar_url_unet(change):
        seleccion = change['new']
        if seleccion in PRESET_UNET:
            unet_url.value = PRESET_UNET[seleccion]
        else:
            unet_url.value = ""

    preset_unet_dropdown.observe(actualizar_url_unet, names='value')

    unet_method = widgets.Dropdown(options=['aria2', 'gdown'], value='aria2', description='Método:')
    unet_btn = widgets.Button(description='Descargar Unet', button_style='primary', icon='download')
    unet_btn.on_click(lambda b: procesar_descarga(b, unet_url, unet_method, UNET_DIR))

    tab_unet = widgets.VBox([
        widgets.HTML("<h4>Descargar Modelos Unet</h4><p>Pega múltiples URLs separadas por comas (,)</p>"),
        preset_unet_dropdown,
        widgets.HBox([unet_url, unet_method]),
        unet_btn
    ])

    # --- Pestaña 9: Clip ---
    opciones_presets_clip = ['-- Personalizado / Manual --'] + list(PRESET_CLIP.keys())
    preset_clip_dropdown = widgets.Dropdown(options=opciones_presets_clip, value='-- Personalizado / Manual --', description='Favoritos:', layout=widgets.Layout(width='80%'))
    clip_url = widgets.Text(placeholder='https://url1, https://url2, ...', description='URL:', layout=widgets.Layout(width='80%'))

    def actualizar_url_clip(change):
        seleccion = change['new']
        if seleccion in PRESET_CLIP:
            clip_url.value = PRESET_CLIP[seleccion]
        else:
            clip_url.value = ""

    preset_clip_dropdown.observe(actualizar_url_clip, names='value')

    clip_method = widgets.Dropdown(options=['aria2', 'gdown'], value='aria2', description='Método:')
    clip_btn = widgets.Button(description='Descargar Clip', button_style='info', icon='download')
    clip_btn.on_click(lambda b: procesar_descarga(b, clip_url, clip_method, CLIP_DIR))

    tab_clip = widgets.VBox([
        widgets.HTML("<h4>Descargar Modelos Clip</h4><p>Pega múltiples URLs separadas por comas (,)</p>"),
        preset_clip_dropdown,
        widgets.HBox([clip_url, clip_method]),
        clip_btn
    ])

    # --- Pestaña 10: Extensiones ComfyUI ---
    comfy_ext_url = widgets.Text(placeholder='https://github.com/autor/repositorio.git, ...', description='URLs (Git):', layout=widgets.Layout(width='80%'))
    comfy_ext_btn = widgets.Button(description='Clonar e Instalar', button_style='danger', icon='code')
    comfy_ext_btn.on_click(lambda b: procesar_extensiones(b, comfy_ext_url))

    tab_comfy_ext = widgets.VBox([
        widgets.HTML("<h4>Clonar Extensiones para ComfyUI</h4><p>Pega enlaces de repositorios de GitHub separados por comas (,). Se clonarán e instalarán sus requirements usando uv.</p>"),
        comfy_ext_url,
        comfy_ext_btn
    ])

    # --- Ensamblar Interfaz ---
    tabs = widgets.Tab(children=[tab_base, tab_lora, tab_vae, tab_upscaler, tab_controlnet, tab_diffusion, tab_te, tab_unet, tab_clip, tab_comfy_ext])
    tabs.set_title(0, '📦 Modelos Base')
    tabs.set_title(1, '✨ LoRAs')
    tabs.set_title(2, '🎨 VAEs')
    tabs.set_title(3, '🔍 Upscalers')
    tabs.set_title(4, '🕹️ ControlNet')
    tabs.set_title(5, '🌌 Diffusion Models')
    tabs.set_title(6, '📝 Text Encoders')
    tabs.set_title(7, '🧠 Unet')
    tabs.set_title(8, '🔗 Clip')
    tabs.set_title(9, '🧩 Extensiones Comfy')

    if token_guardado:
        mensaje_token = "<i>(✅ Token cargado automáticamente desde la memoria persistente)</i>"
    else:
        mensaje_token = "<i>(⚠️ No se encontró token guardado, puedes ingresarlo manualmente)</i>"

    ui = widgets.VBox([
        widgets.HTML("<h2>Gestor Total de Descargas para SwarmUI (Kaggle)</h2>"),
        widgets.HBox([token_input, widgets.HTML(mensaje_token)]),
        tabs,
        widgets.HTML("<hr>"),
        progress_container,
        out_console
    ])

    display(ui)