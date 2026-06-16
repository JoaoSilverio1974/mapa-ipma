import os
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def capturar_mapas_PE():
    print("-> Processando mapas PE...")
    pasta_raiz = os.getcwd()
    hoje = datetime.now()
    urls = {
        "portugal_hoje_PE.png": hoje,
        "portugal_amanha_PE.png": hoje + timedelta(days=1),
        "portugal_depois_PE.png": hoje + timedelta(days=2)
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1200, 'height': 1200})
        page.goto("https://www.ipma.pt/pt/riscoincendio/fwi/")
        page.wait_for_selector(".leaflet-container", timeout=60000)
        page.wait_for_timeout(6000)
        for nome, data in urls.items():
            url = f"https://api.ipma.pt/public-data/mf2_preview/lsasaf_p2000_continent/lsasaf_p2000_continent_{data.strftime('%Y-%m-%d')}T00_00_00.png"
            page.evaluate(f"(url) => document.querySelectorAll('img[src*=\"lsasaf_p2000\"]')[0].src = url", url)
            page.wait_for_timeout(3000)
            page.locator(".leaflet-container").first.screenshot(path=os.path.join(pasta_raiz, nome))
        browser.close()

def capturar_mapas_PIR():
    print("-> Processando mapas PIR...")
    # Usamos o endpoint público que não dá erro de DNS
    for d in range(3):
        nome_ficheiro = ["portugal_hoje.png", "portugal_amanha.png", "portugal_depois.png"][d]
        dia_api = 0 if d == 0 else 1
        url = f"https://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d{dia_api}.json"
        
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                dados = resp.json().get('data', [])
                fig, ax = plt.subplots(figsize=(6, 12))
                ax.set_facecolor('#E6F2FF')
                for i, item in enumerate(dados):
                    cor = {"1": "#90EE90", "2": "#FFFF66", "3": "#F4A460", "4": "#DC6464", "5": "#8B5A69"}.get(str(item.get('rcm', 1)), "#90EE90")
                    ax.add_patch(plt.Rectangle((10, 950 - (i*10)), 6, 6, color=cor, edgecolor='none'))
                ax.set_xlim(0, 100); ax.set_ylim(0, 1000); ax.axis('off')
                plt.savefig(nome_ficheiro, dpi=100); plt.close()
        except Exception as e:
            print(f"Erro no PIR: {e}")

if __name__ == "__main__":
    capturar_mapas_PE()
    capturar_mapas_PIR()
