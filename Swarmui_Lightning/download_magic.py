# download_magic.py
"""
Mágica %download para IPython / Jupyter / Colab.
Al importar este módulo se registra automáticamente la línea mágica %download.
Uso:
    import download_magic
    %download https://civitai.com/api/download/models/..., https://huggingface.co/...
"""

from IPython import get_ipython
from IPython.core.magic import register_line_magic
from IPython.display import HTML, display
import os
import subprocess
import re
import requests

# Recuperamos el token de %store
ipython = get_ipython()
token = None
try:
    ipython.magic("store -r token_civitai")
    token = ipython.user_ns.get("token_civitai")
except Exception:
    pass

@register_line_magic
def download(line):
    """
    %download url1, url2, ...
    Muestra solo el nombre real y respeta la carpeta actual (%cd).
    """
    dest = os.getcwd()
    urls = [u.strip() for u in line.split(",") if u.strip()]

    for url in urls:
        # ---------- CivitAI ----------
        if "civitai.com" in url:
            if not token:
                display(HTML("<h4 style='color:red;'>⚠️ Token de CivitAI no encontrado.</h4>"))
                continue
            url_token = f"{url}{'&' if '?' in url else '?'}token={token}"

            try:
                with requests.get(url_token, stream=True, timeout=5) as r:
                    cd = r.headers.get('Content-Disposition', '')
                    match = re.findall(r'filename[*]?=(?:UTF-8\'\')?["\']?([^"\';]+)["\']?', cd)
                    pretty = match[0] if match else url.split('/')[-1].split('?')[0]
            except Exception:
                pretty = url.split('/')[-1].split('?')[0]

            display(HTML(f"<h3 style='color:yellow;'>📥 Descargando: <code>{pretty}</code></h3>"
                         f"<h4 style='color:cyan;'>📁 Destino: <code>{dest}</code></h4>"))

            subprocess.run([
                "aria2c", "--console-log-level=error", "--content-disposition",
                "-c", "-x", "6", "-s", "6", "-k", "1M",
                "-d", dest, url_token
            ])

        # ---------- HuggingFace ----------
        else:
            pretty = url.split('/')[-1].split('?')[0]
            display(HTML(f"<h3 style='color:yellow;'>📥 Descargando: <code>{pretty}</code></h3>"
                         f"<h4 style='color:cyan;'>📁 Destino: <code>{dest}</code></h4>"))
            subprocess.run([
                "aria2c", "--console-log-level=error", "--content-disposition",
                "-c", "-x", "8", "-s", "8", "-k", "1M",
                "-d", dest, "-o", pretty, url
            ])
            for f in os.listdir(dest):
                if re.fullmatch(r'[0-9a-f]{64}', f):
                    os.rename(os.path.join(dest, f), os.path.join(dest, pretty))
                    break

    display(HTML("<h3 style='color:lightgreen;'>✅ Descarga finalizada</h3>"))

# Registramos la línea mágica al importar el módulo
get_ipython().register_magic_function(download, magic_kind='line')