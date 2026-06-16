import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def capturar_mapa_pir(data_offset, nome_ficheiro):
    # Calcula a data para o URL
    data_alvo = (datetime.now() + timedelta(days=data_offset)).strftime("%Y-%m-%d")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        # Portal oficial onde o IPMA monta o mapa PIR
        page.goto("https://protecaocivil.ipma.pt/produtos/idw-wmsprod/")
        
        # Espera que o mapa (leaflet) carregue
        page.wait_for_selector(".leaflet-container", timeout=60000)
        
        # AQUI ESTÁ O SEGREDINHO: 
        # O IPMA usa um input de data no topo. Vamos injetar JS para mudar a data
        # e forçar o mapa a atualizar com os dados desse dia.
        page.evaluate(f"document.querySelector('input[type=date]').value = '{data_alvo}'")
        page.keyboard.press("Enter")
        
        # Espera 5 segundos para o servidor renderizar as novas cores no mapa
        page.wait_for_timeout(5000)
        
        # Tira a foto apenas ao elemento do mapa
        page.locator(".leaflet-container").screenshot(path=nome_ficheiro)
        browser.close()
        print(f"Mapa {nome_ficheiro} capturado com sucesso.")

if __name__ == "__main__":
    # PE (A tua lógica original)
    # [Mantém aqui a tua função capturar_mapas_PE original]
    
    # PIR (Geográfico Real)
    capturar_mapa_pir(0, "portugal_hoje.png")
    capturar_mapa_pir(1, "portugal_amanha.png")
    capturar_mapa_pir(2, "portugal_depois.png")
