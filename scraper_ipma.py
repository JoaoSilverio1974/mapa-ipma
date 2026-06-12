import os
from playwright.sync_api import sync_playwright

def capturar_mapas():
    # Obter o caminho atual onde o código está a correr (raiz do repositório)
    pasta_raiz = os.getcwd()
    print(f"Diretório de trabalho: {pasta_raiz}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1200, 'height': 1200})
        page = context.new_page()
        
        page.goto("https://www.ipma.pt/pt/riscoincendio/fwi/")
        page.wait_for_selector(".leaflet-container", timeout=30000)
        page.wait_for_timeout(8000) # Espera extra para renderizar as camadas CAOP
        
        # Limpeza visual
        page.evaluate("""
            var els = document.querySelectorAll('header, footer, nav, .leaflet-control-container, [id*=cookie]');
            els.forEach(el => { if(el) el.style.display = 'none'; });
        """)
        
        mapa = page.locator(".leaflet-container").first
        
        # Captura forçando o caminho absoluto na pasta raiz
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_hoje.png"))
        print("Guardado: portugal_hoje.png")
        
        try:
            page.locator('text="Amanhã"').first.click(timeout=5000)
            page.wait_for_timeout(4000)
            mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_amanha.png"))
            print("Guardado: portugal_amanha.png")
            
            page.locator('text="Depois de amanhã"').first.click(timeout=5000)
            page.wait_for_timeout(4000)
            mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_depois.png"))
            print("Guardado: portugal_depois.png")
        except:
            print("Aviso: Falha na captura dos dias seguintes.")
            
        browser.close()

if __name__ == "__main__":
    capturar_mapas()
