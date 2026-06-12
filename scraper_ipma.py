import os
from playwright.sync_api import sync_playwright

def capturar_mapas():
    pasta_raiz = os.getcwd()
    print(f"Diretório de trabalho: {pasta_raiz}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1200, 'height': 1200})
        page = context.new_page()
        
        page.goto("https://www.ipma.pt/pt/riscoincendio/fwi/")
        page.wait_for_selector(".leaflet-container", timeout=30000)
        page.wait_for_timeout(8000) # Espera pelas camadas da CAOP
        
        # Limpeza visual
        page.evaluate("""
            var els = document.querySelectorAll('header, footer, nav, .leaflet-control-container, [id*=cookie]');
            els.forEach(el => { if(el) el.style.display = 'none'; });
        """)
        
        mapa = page.locator(".leaflet-container").first
        
        # Captura com os NOVOS NOMES solicitados (_PE)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_hoje_PE.png"))
        print("Guardado: portugal_hoje_PE.png")
        
        try:
            page.locator('text="Amanhã"').first.click(timeout=5000)
            page.wait_for_timeout(4000)
            mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_amanha_PE.png"))
            print("Guardado: portugal_amanha_PE.png")
            
            page.locator('text="Depois de amanhã"').first.click(timeout=5000)
            page.wait_for_timeout(4000)
            mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_depois_PE.png"))
            print("Guardado: portugal_depois_PE.png")
        except:
            print("Aviso: Falha na captura dos dias seguintes.")
            
        browser.close()

if __name__ == "__main__":
    capturar_mapas()
