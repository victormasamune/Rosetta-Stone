import asyncio
import websockets
import threading
import os
import sys
import subprocess
import http.server
import socketserver
import time
import multiprocessing

# ==========================================
# 1. RESOLUÇÃO DE DIRETÓRIO PARA EXE/SCRIPT
# ==========================================
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ==========================================
# 2. MOTOR DO WEBSOCKET SERVER (PORTA 8765)
# ==========================================
CLIENTS = set()

async def handler(websocket):
    CLIENTS.add(websocket)
    try:
        async for message in websocket:
            for client in CLIENTS:
                if client != websocket:
                    try:
                        await client.send(message)
                    except Exception:
                        pass
    except Exception:
        pass
    finally:
        CLIENTS.remove(websocket)

async def ws_main():
    async with websockets.serve(handler, "localhost", 8765):
        print("[WS] Servidor Rosetta Stone rodando na porta 8765.")
        await asyncio.Future()

def start_ws_server():
    asyncio.run(ws_main())

# ==========================================
# 3. MOTOR HTTP SERVER (PORTA 8080)
# ==========================================
def start_http_server():
    path = get_resource_path("")
    os.chdir(path)
    Handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8080), Handler) as httpd:
        print("[HTTP] Assets da interface servindo na porta 8080.")
        httpd.serve_forever()

# ==========================================
# 4. INICIALIZAÇÃO DA APLICAÇÃO
# ==========================================
if __name__ == '__main__':
    multiprocessing.freeze_support()

    threading.Thread(target=start_ws_server, daemon=True).start()
    threading.Thread(target=start_http_server, daemon=True).start()

    time.sleep(1.5)

    url = "http://localhost:8080/captura_voz.html"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

    rosetta_profile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rosetta_profile")
    
    chrome_flags = [
        chrome_path,
        f"--app={url}",
        f"--user-data-dir={rosetta_profile}",
        "--use-fake-ui-for-media-stream",
        "--test-type", 
        "--disable-web-security",
        "--autoplay-policy=no-user-gesture-required",
        "--no-first-run"
    ]

    try:
        process = subprocess.Popen(chrome_flags)
        while process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)