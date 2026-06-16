import os
from playwright.sync_api import sync_playwright

def capturar_mapa(nome_ficheiro, data_str):
    print(f"-> A capturar mapa para {data_str}...")
    with sync_playwright() as p:
        # Modo 'headed=False' pode ajudar se o site bloquear automação, mas tentamos 'True' primeiro
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1600, 'height': 1200})
        
        # O portal que realmente monta os mapas
        page.goto("https://protecaocivil.ipma.pt/produtos/idw-wmsprod/")
        
        # Esperar que o mapa (leaflet) carregue
        page.wait_for_selector(".leaflet-container", timeout=60000)
        
        # Injetar a data no campo que o IPMA usa
        page.evaluate(f"document.querySelector('input[type=date]').value = '{data_str}'")
        page.keyboard.press("Enter")
        
        # Esperar tempo real para o servidor desenhar o mapa
        page.wait_for_timeout(10000)
        
        # Captura o mapa inteiro (contorno, cores e legenda)
        page.locator(".leaflet-container").first.screenshot(path=nome_ficheiro)
        browser.close()
        print(f"   Mapa {nome_ficheiro} guardado.")

if __name__ == "__main__":
    # PE (A tua lógica original de injetar imagem)
    # [Mantém aqui a tua função capturar_mapas_PE() que já funcionava]
    
    # PIR (Geográfico Real - Captura das fotos)
    hoje = "2026-06-18" # Ajusta para hoje
    capturar_mapa("portugal_hoje.png", hoje)
    capturar_mapa("portugal_amanha.png", "2026-06-19")
    capturar_mapa("portugal_depois.png", "2026-06-20")
