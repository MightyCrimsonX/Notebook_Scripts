import os
import re
import subprocess
import sys
import threading
import time

# 1. Cambiar al directorio de trabajo (reemplazo de %cd)
swarm_dir = "/kaggle/working/SwarmUI"
if os.path.exists(swarm_dir):
    os.chdir(swarm_dir)
else:
    print(f"⚠️ Directorio {swarm_dir} no encontrado, ejecutando en: {os.getcwd()}")

# ==========================================
# 2. Iniciar túnel Gradio en THREAD
# ==========================================
print("\n🚀 Iniciando túnel Gradio en puerto 7801...")

url_gradio = None
tunnel_log = []

def iniciar_tunnel():
    global url_gradio, tunnel_log
    tunnel_script = os.path.join(swarm_dir, "gradio-tunnel.py")
    if not os.path.exists(tunnel_script):
        tunnel_script = "gradio-tunnel.py"

    try:
        proceso = subprocess.Popen(
            [sys.executable, tunnel_script, "7801"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in iter(proceso.stdout.readline, ''):
            line = line.strip()
            if line:
                tunnel_log.append(line)
                if not url_gradio:
                    match = re.search(r'https://[\w-]+\.gradio\.live', line)
                    if match:
                        url_gradio = match.group(0)
    except Exception as e:
        tunnel_log.append(f"Error al iniciar el script del túnel: {e}")

# Iniciar túnel en thread separado
thread_tunnel = threading.Thread(target=iniciar_tunnel, daemon=True)
thread_tunnel.start()

# Esperar a que aparezca la URL (máximo 30 segundos)
espera = 0
while not url_gradio and espera < 30:
    time.sleep(1)
    espera += 1
    if espera % 5 == 0:
        print(f"   Esperando URL... ({espera}s)")

if url_gradio:
    print(f"\n{'='*60}")
    print(f"🌐 URL PÚBLICA DE GRADIO: {url_gradio}")
    print(f"   Espere a que inicie correctamente SwarmUI...")
    print(f"{'='*60}\n")
else:
    print("⚠️  URL no detectada en 30s, continuando...")
    if tunnel_log:
        print("   Últimas líneas del túnel:")
        for line in tunnel_log[-5:]:
            print(f"   {line}")

# ==========================================
# 3. Variables de entorno y lanzamiento
# ==========================================
print("🐝 Iniciando SwarmUI...")
print("⏱️  Esto puede tomar unos minutos la primera vez...\n")

# Configuración de variables de entorno
mimalloc_path = '/kaggle/working/libmimalloc.so.2.1'
if os.path.exists(mimalloc_path):
    os.environ['LD_PRELOAD'] = mimalloc_path
os.environ['SWARMPATH'] = swarm_dir

# Permisos de ejecución (reemplazo de !chmod +x)
launch_script = "./launch-linux.sh"
if os.path.exists(launch_script):
    os.chmod(launch_script, 0o755)

# Ejecución en primer plano transmitiendo logs en vivo (reemplazo de !./launch-linux.sh)
try:
    subprocess.run(
        [launch_script, "--launch_mode", "none", "--host", "0.0.0.0", "--port", "7801"],
        check=True
    )
except KeyboardInterrupt:
    print("\n🛑 SwarmUI detenido por el usuario.")
except Exception as e:
    print(f"\n❌ Error durante la ejecución de SwarmUI: {e}")
