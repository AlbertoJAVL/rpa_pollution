#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Watch-dog Telegram para el RPA de Ajustes Siebel
· Vigila que “py.exe” siga vivo.
· Si desaparece o supera el umbral de RAM, termina el proceso,
  ejecuta el BAT de arranque y avisa por Telegram.
· Toda la configuración está embebida; no depende de .env.
"""

import os
import time
import socket
import psutil
import subprocess
import pytz, logging
import requests
from typing import Optional
from datetime import datetime

# ───────────────  CONFIGURACIÓN (tomada de tu script original)  ─────────────
PROCESS_EXE          = "py.exe"   # nombre exacto en el Administrador de tareas
BAT_PATH             = r"C:\rpa_pollution\RPA_NewCN\Init.bat"

CHECK_EVERY_SEC      = 30     # frecuencia de chequeo
MEM_LIMIT_SYSTEM_PCT = 85     # % de RAM total que dispara alerta
MEM_LIMIT_PROC_MB    = 400    # MB de RAM del proceso vigilado

TELEGRAM_TOKEN       = "6819354375:AAFb2UuBWfbOkT83YDyt2IH_lHSUgOpnkuU"
TELEGRAM_CHAT_ID     = "-1002094293899"      # igual que en tu código original

# ───────────────  UTILIDADES  ───────────────────────────────────────────────
HOSTNAME = socket.gethostname()
IP_ADDR  = socket.gethostbyname(HOSTNAME)

def send_msg(error):
    IST = pytz.timezone('America/Mexico_City')
    raw_TS = datetime.now(IST)
    msg = f"Rpa: {IP_ADDR} Info:{error}"
    telegram_api = f"https://api.telegram.org/bot8426416631:AAEDYPkcuN3sRoyOAbFIYFeWhxt6gINTvrE/sendMessage?chat_id=-4843960504&text={msg}"
    tel_resp = requests.get(telegram_api)
    print(tel_resp.status_code)
    if tel_resp.status_code == 200:
        print("INFO: Notification has been sent on Telegram")
    else:
        print("ERROR: Could not send Message")

def now() -> str:
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

def proceso_vivo() -> Optional[psutil.Process]:
    """Devuelve el primer proceso cuyo ejecutable coincide con PROCESS_EXE."""
    for proc in psutil.process_iter(["name", "memory_info"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == PROCESS_EXE.lower():
                return proc
        except psutil.NoSuchProcess:
            pass
    return None

def reiniciar_bot() -> None:
    """Lanza el BAT de arranque tras avisar por Telegram."""
    send_msg(f"⚠️  {IP_ADDR} – Reiniciando RPA con {os.path.basename(BAT_PATH)}")
    subprocess.Popen(["cmd", "/c", BAT_PATH], creationflags=subprocess.CREATE_NO_WINDOW)
    subprocess.Popen(["cmd", "/c", BAT_PATH], creationflags=subprocess.CREATE_NO_WINDOW)
    subprocess.Popen(["cmd", "/c", BAT_PATH], creationflags=subprocess.CREATE_NO_WINDOW)

# ───────────────  BUCLE PRINCIPAL  ──────────────────────────────────────────
def main() -> None:
    last_ram_alert = 0
    send_msg(f"🤖 Watch-dog iniciado en {IP_ADDR} ({HOSTNAME})")

    while True:
        proc = proceso_vivo()

        # 1) Proceso caído  → alerta + arranque
        if proc is None:
            send_msg(f"🚨  {IP_ADDR} – {PROCESS_EXE} NO encontrado ({now()})")
            reiniciar_bot()
            time.sleep(10)         # da tiempo a que arranque el BAT
            continue

        # 2) RAM del proceso excedida → terminar + reinicio
        ram_mb = proc.memory_info().rss / (1024 * 1024)
        if ram_mb > MEM_LIMIT_PROC_MB:
            send_msg(f"🚨  RAM {PROCESS_EXE}: {ram_mb:.0f} MB > {MEM_LIMIT_PROC_MB} MB")
            try:
                proc.terminate(); proc.wait(15)
            except Exception as e:
                logger = logging.getLogger("rpa")
                logger.exception("Fallo en orden %s: %s", e) 
                proc.kill()
            reiniciar_bot()

        # 3) RAM del sistema elevada → alerta (máx. cada 10 min)
        mem_pct = psutil.virtual_memory().percent
        if mem_pct > MEM_LIMIT_SYSTEM_PCT and (time.time() - last_ram_alert) > 600:
            send_msg(f"⚠️  RAM sistema {mem_pct:.0f}% > {MEM_LIMIT_SYSTEM_PCT}% ({now()})")
            last_ram_alert = time.time()

        time.sleep(CHECK_EVERY_SEC)

# ───────────────  EJECUCIÓN  ────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        send_msg("⏹️  Watch-dog detenido manualmente")
send_msg("⏹️ Prueba pollution")