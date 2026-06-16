import requests
import os

# Link direto para o mapa de Risco de Incêndio (IPMA)
# Este link devolve a imagem final, sem precisar de montar peças.
URL_MAPA = "https://services.ipma.pt/geoserver/incendios/wms?service=WMS&version=1.1.1&request=GetMap&layers=incendios:rcm_concelhos&styles=&format=image/png&transparent=true&width=1000&height=1200&srs=EPSG:3857&bbox=-1200000,4300000,-600000,5200000"

def salvar_mapa(nome):
    try:
        r = requests.get(URL_MAPA, timeout=30)
        if r.status_code == 200:
            with open(nome, 'wb') as f:
                f.write(r.content)
            print(f"Sucesso: {nome}")
    except Exception as e:
        print(f"Falhou: {e}")

if __name__ == "__main__":
    salvar_mapa("portugal_hoje.png")
