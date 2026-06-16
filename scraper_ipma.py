import os
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# --- PARTE 1: A TUA LÓGICA ORIGINAL (MAPAS PE) ---
def capturar_mapas_PE():
    print("-> A processar mapas PE (Playwright)...")
    pasta_raiz = os.getcwd()
    
    hoje = datetime.now()
    amanha = hoje + timedelta(days=1)
    depois = hoje + timedelta(days=2)
    
    fmt_hoje = hoje.strftime("%Y-%m-%d")
    fmt_amanha = amanha.strftime("%Y-%m-%d")
    fmt_depois = depois.strftime("%Y-%m-%d")
    
    url_base = "https://api.ipma.pt/public-data/mf2_preview/lsasaf_p2000_continent/lsasaf_p2000_continent_{}T00_00_00.png"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1200, 'height': 1200})
        page = context.new_page()
        
        page.goto("https://www.ipma.pt/pt/riscoincendio/fwi/")
        page.wait_for_selector(".leaflet-container", timeout=30000)
        page.wait_for_timeout(6000)
        
        page.evaluate("""
            var els = document.querySelectorAll('header, footer, nav, [id*=cookie], .leaflet-control-container');
            els.forEach(el => { if(el) el.style.display = 'none'; });
        """)
        
        mapa = page.locator(".leaflet-container").first
        
        js_mudar_imagem = """(novaUrl) => {
            var imagens = document.querySelectorAll('img[src*="lsasaf_p2000"]');
            imagens.forEach(img => img.src = novaUrl);
        }"""
        
        # 1. PE HOJE
        link_hoje = url_base.format(fmt_hoje)
        page.evaluate(js_mudar_imagem, link_hoje)
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_hoje_PE.png"))
        
        # 2. PE AMANHÃ
        link_amanha = url_base.format(fmt_amanha)
        page.evaluate(js_mudar_imagem, link_amanha)
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_amanha_PE.png"))
        
        # 3. PE DEPOIS
        link_depois = url_base.format(fmt_depois)
        page.evaluate(js_mudar_imagem, link_depois)
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_depois_PE.png"))
        
        browser.close()

# --- PARTE 2: A NOVA FUNÇÃO PIR (GEOSERVER) ---
def capturar_mapas_PIR():
    print("-> A sacar mapas PIR (Geoserver)...")
    for d in range(3):
        data_alvo = (datetime.now() + timedelta(days=d)).strftime("%Y-%m-%d")
        # Nomes que o teu Excel espera:
        nome_ficheiro = "portugal_hoje.png" if d == 0 else "portugal_amanha.png" if d == 1 else "portugal_depois.png"
        
        # Geoserver oficial que já validámos que funciona
        url = f"https://services.ipma.pt/geoserver/incendios/wms?service=WMS&version=1.1.1&request=GetMap&layers=incendios:rcm_concelhos&styles=&format=image/png&transparent=true&width=600&height=1200&srs=EPSG:3857&bbox=-1070000,4420000,-680000,5200000&time={data_alvo}T00:00:00Z"
        
        headers = {"User-Agent": "Mozilla/5.0"}
        resposta = requests.get(url, headers=headers)
        
        if resposta.status_code == 200:
            with open(nome_ficheiro, 'wb') as f:
                f.write(resposta.content)
            print(f"   Sucesso: {nome_ficheiro}")

if __name__ == "__main__":
    capturar_mapas_PE()
    capturar_mapas_PIR()
