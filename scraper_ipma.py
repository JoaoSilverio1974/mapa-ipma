import os
import requests
from datetime import datetime, timedelta

def baixar_mapa_pir(nome_ficheiro, data_str):
    print(f"-> A sacar mapa oficial: {nome_ficheiro} ({data_str})")
    
    # URL configurada para devolver o mapa de Portugal inteiro (bbox cobre o continente)
    # A variável 'time' define a data no servidor do IPMA
    url = f"https://services.ipma.pt/geoserver/incendios/wms?service=WMS&version=1.1.1&request=GetMap&layers=incendios:rcm_concelhos&styles=&format=image/png&transparent=true&width=1000&height=1200&srs=EPSG:3857&bbox=-1200000,4300000,-600000,5200000&time={data_str}T00:00:00Z"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200 and 'image' in resp.headers.get('Content-Type', ''):
            with open(nome_ficheiro, 'wb') as f:
                f.write(resp.content)
            print(f"   Sucesso: {nome_ficheiro} guardado.")
        else:
            print(f"   Falha (Status {resp.status_code}): Não foi possível obter o mapa.")
    except Exception as e:
        print(f"   Erro de rede: {e}")

if __name__ == "__main__":
    # --- 1. Mapas PE (A tua lógica Playwright que já funcionava) ---
    # [COLA AQUI A TUA FUNÇÃO capturar_mapas_PE() ORIGINAL]
    
    # --- 2. Mapas PIR (O mapa de Portugal inteiro e limpo) ---
    hoje = datetime.now()
    baixar_mapa_pir("portugal_hoje.png", hoje.strftime("%Y-%m-%d"))
    baixar_mapa_pir("portugal_amanha.png", (hoje + timedelta(days=1)).strftime("%Y-%m-%d"))
    baixar_mapa_pir("portugal_depois.png", (hoje + timedelta(days=2)).strftime("%Y-%m-%d"))
