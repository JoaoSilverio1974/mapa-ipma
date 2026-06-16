import os
from playwright.sync_api import sync_playwright

def capturar_mapa(url, nome, seletor):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.goto(url)
        page.wait_for_selector(seletor, timeout=60000)
        page.wait_for_timeout(5000) # Espera o carregamento real
        page.locator(seletor).first.screenshot(path=nome)
        browser.close()
        print(f"Foto guardada: {nome}")

if __name__ == "__main__":
    # PE: Usa a tua lógica original (mantém a tua função capturar_mapas_PE())
    # PIR: Captura direta do mapa oficial (sem gráficos de quadrados)
    capturar_mapa("https://protecaocivil.ipma.pt/produtos/idw-wmsprod/", "portugal_hoje.png", ".leaflet-container")
    capturar_mapa("https://protecaocivil.ipma.pt/produtos/idw-wmsprod/", "portugal_amanha.png", ".leaflet-container")
    capturar_mapa("https://protecaocivil.ipma.pt/produtos/idw-wmsprod/", "portugal_depois.png", ".leaflet-container")
