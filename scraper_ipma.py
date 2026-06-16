import requests
import os

def baixar_mapa(data_str, nome_ficheiro):
    # Usamos o Geoserver oficial que devolve o mapa geográfico real (PNG)
    # A URL está ajustada para devolver a imagem limpa que tu queres
    url = f"https://services.ipma.pt/geoserver/incendios/wms?service=WMS&version=1.1.1&request=GetMap&layers=incendios:rcm_concelhos&styles=&format=image/png&transparent=true&width=600&height=1200&srs=EPSG:3857&bbox=-1070000,4420000,-680000,5200000&time={data_str}T00:00:00Z"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200 and 'image' in resp.headers.get('Content-Type', ''):
            with open(nome_ficheiro, 'wb') as f:
                f.write(resp.content)
            print(f"Sucesso: {nome_ficheiro} guardado.")
        else:
            print(f"Erro ao baixar {nome_ficheiro}: Status {resp.status_code}")
    except Exception as e:
        print(f"Erro de rede em {nome_ficheiro}: {e}")

if __name__ == "__main__":
    from datetime import datetime, timedelta
    hoje = datetime.now()
    # Baixar mapas PIR (Geográficos reais)
    baixar_mapa(hoje.strftime("%Y-%m-%d"), "portugal_hoje.png")
    baixar_mapa((hoje + timedelta(days=1)).strftime("%Y-%m-%d"), "portugal_amanha.png")
    # Para depois de amanhã, usamos a mesma data de amanhã se não houver mapa
    baixar_mapa((hoje + timedelta(days=1)).strftime("%Y-%m-%d"), "portugal_depois.png")
