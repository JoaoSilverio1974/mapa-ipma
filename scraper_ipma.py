import os
from playwright.sync_api import sync_playwright

def capturar_mapa_inteiro(nome_ficheiro, data_str):
    print(f"-> A capturar mapa para {data_str}...")
    with sync_playwright() as p:
        # Lançar browser em modo headless (invisível)
        browser = p.chromium.launch(headless=True)
        # Viewport grande para garantir que o mapa ocupa o ecrã todo
        page = browser.new_page(viewport={'width': 1600, 'height': 1200})
        
        # URL do portal oficial que desenha o mapa
        page.goto("https://protecaocivil.ipma.pt/produtos/idw-wmsprod/")
        
        # Esperar que o mapa (leaflet) carregue totalmente
        page.wait_for_selector(".leaflet-container", timeout=60000)
        
        # O IPMA usa um input de data. Injetamos a data que queremos
        page.evaluate(f"document.querySelector('input[type=date]').value = '{data_str}'")
        page.keyboard.press("Enter")
        
        # Esperar que o mapa se redesenhe com os dados da data
        page.wait_for_timeout(8000)
        
        # Tirar fotografia APENAS ao elemento do mapa (isto corta automaticamente os menus)
        page.locator(".leaflet-container").first.screenshot(path=nome_ficheiro)
        
        print(f"   Mapa {nome_ficheiro} guardado com sucesso.")
        browser.close()

if __name__ == "__main__":
    # PE (A tua função original mantida)
    # [Mantém aqui a tua função capturar_mapas_PE original]
    
    # PIR (Mapas Geográficos Reais)
    hoje = "2026-06-18" # Ajusta para o formato que o input espera
    capturar_mapa_inteiro("portugal_hoje.png", hoje)
    capturar_mapa_inteiro("portugal_amanha.png", "2026-06-19")
    capturar_mapa_inteiro("portugal_depois.png", "2026-06-20")
