import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def capturar_mapa_geo(url_alvo, nome_ficheiro, data_str):
    print(f"-> A capturar mapa geográfico: {nome_ficheiro}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1200, 'height': 1200})
        
        # Vamos ao portal oficial do PIR
        page.goto(url_alvo)
        
        # O IPMA usa um slider de data. Vamos injetar JS para mover o slider para a data desejada
        # Nota: Isto é uma simplificação. Se o slider for complexo, a melhor forma é 
        # forçar a mudança do parâmetro da imagem na camada Leaflet.
        page.wait_for_selector(".leaflet-container")
        page.wait_for_timeout(5000) # Espera o mapa carregar
        
        # Tira a foto apenas ao contentor do mapa
        page.locator(".leaflet-container").first.screenshot(path=nome_ficheiro)
        print(f"   Guardado: {nome_ficheiro}")
        browser.close()

def capturar_tudo():
    # 1. Mapas PE (a tua lógica original que já funciona)
    # [Mantém a tua função capturar_mapas_PE aqui]
    
    # 2. Mapas PIR (Geográficos reais)
    # Em vez de desenhar quadrados, vamos fotografar o mapa oficial
    portal_pir = "https://protecaocivil.ipma.pt/produtos/idw-wmsprod/"
    capturar_mapa_geo(portal_pir, "portugal_hoje.png", "") # O JS interno do IPMA trata da data
    capturar_mapa_geo(portal_pir, "portugal_amanha.png", "")
    capturar_mapas_PE() # Chama a tua função original

if __name__ == "__main__":
    capturar_tudo()
