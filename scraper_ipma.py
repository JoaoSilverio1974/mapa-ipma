import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def capturar_mapas_PE():
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
            data_str = data.strftime("%Y-%m-%d")
            url = f"https://api.ipma.pt/public-data/mf2_preview/lsasaf_p2000_continent/lsasaf_p2000_continent_{data_str}T00_00_00.png"
            page.evaluate(f"(url) => document.querySelectorAll('img[src*=\"lsasaf_p2000\"]')[0].src = url", url)
            page.wait_for_timeout(3000)
            page.locator(".leaflet-container").first.screenshot(path=os.path.join(pasta_raiz, nome))
        browser.close()

if __name__ == "__main__":
    capturar_mapas_PE()
