import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def capturar_mapa_pir(nome_ficheiro, data_str):
    print(f"-> A capturar mapa para {data_str}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Resolução boa para o mapa ficar nítido
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        page.goto("https://protecaocivil.ipma.pt/produtos/idw-wmsprod/")
        page.wait_for_selector(".leaflet-container", timeout=60000)
        page.wait_for_timeout(3000) # Espera o site "respirar"
        
        # A MAGIA ESTÁ AQUI: Muda a data e OBRIGA o site a atualizar o mapa
        js_mudar_data = f"""
            var input = document.querySelector('input[type="date"]');
            if(input) {{
                input.value = '{data_str}';
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        """
        page.evaluate(js_mudar_data)
        
        # Espera 8 segundos para o servidor do IPMA descarregar as novas peças WMS coloridas
        page.wait_for_timeout(8000) 
        
        # Tira a foto
        page.locator(".leaflet-container").first.screenshot(path=nome_ficheiro)
        browser.close()
        print(f"   Mapa {nome_ficheiro} guardado com sucesso.")

# --- MANTER A TUA FUNÇÃO PE AQUI ---
def capturar_mapas_PE():
    print("-> Capturando mapas PE...")
    # ... [Cola a tua função PE que já funciona perfeitamente aqui] ...
    pass

if __name__ == "__main__":
    # 1. Corre os mapas PE
    # capturar_mapas_PE()  <-- Descomenta e usa a tua função PE
    
    # 2. Corre os mapas PIR (Cálculo automático das datas)
    hoje = datetime.now()
    amanha = hoje + timedelta(days=1)
    depois = hoje + timedelta(days=2)
    
    capturar_mapa_pir("portugal_hoje.png", hoje.strftime("%Y-%m-%d"))
    capturar_mapa_pir("portugal_amanha.png", amanha.strftime("%Y-%m-%d"))
    capturar_mapa_pir("portugal_depois.png", depois.strftime("%Y-%m-%d"))
