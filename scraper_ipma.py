import os
import json
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def capturar_mapas_PE():
    print("-> A iniciar captura dos mapas PE (Fronteiras)...")
    pasta_raiz = os.getcwd()
    hoje = datetime.now()
    
    fmt_hoje = hoje.strftime("%Y-%m-%d")
    fmt_amanha = (hoje + timedelta(days=1)).strftime("%Y-%m-%d")
    fmt_depois = (hoje + timedelta(days=2)).strftime("%Y-%m-%d")
    
    url_base = "https://api.ipma.pt/public-data/mf2_preview/lsasaf_p2000_continent/lsasaf_p2000_continent_{}T00_00_00.png"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1200, 'height': 1200})
        page = context.new_page()
        
        page.goto("https://www.ipma.pt/pt/riscoincendio/fwi/")
        page.wait_for_selector(".leaflet-container", timeout=60000)
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
        
        # HOJE PE
        page.evaluate(js_mudar_imagem, url_base.format(fmt_hoje))
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_hoje_PE.png"))
        print(f"   Sucesso: portugal_hoje_PE.png")
        
        # AMANHA PE
        page.evaluate(js_mudar_imagem, url_base.format(fmt_amanha))
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_amanha_PE.png"))
        print(f"   Sucesso: portugal_amanha_PE.png")
        
        # DEPOIS PE
        page.evaluate(js_mudar_imagem, url_base.format(fmt_depois))
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_depois_PE.png"))
        print(f"   Sucesso: portugal_depois_PE.png")
        
        browser.close()

def capturar_mapas_PIR():
    print("\n-> A transferir mapas PIR (Download Direto do Servidor IPMA)...")
    hoje = datetime.now()
    ano_atual = hoje.year
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for d in range(3):
            data_alvo = (hoje + timedelta(days=d)).strftime("%Y-%m-%d")
            nome_ficheiro = "portugal_hoje.png" if d == 0 else "portugal_amanha.png" if d == 1 else "portugal_depois.png"
            
            url_wms = (
                "https://cs2.ipma.pt/azstats/wms?"
                f"map=rcm_{ano_atual}-forecast_9p1d-continental-prevstat-idw&"
                "service=WMS&request=GetMap&"
                f"layers=PT%3AIPMA%3ACDG%3ALAYER%3Arcm_{ano_atual}-forecast_9p1d-continental-prevstat-idw%3APIR%3ACONCELHOS&"
                "styles=&format=image%2Fpng&transparent=true&version=1.1.1&"
                f"time={data_alvo}T00%3A00%3A00Z&"
                "width=800&height=1200&srs=EPSG%3A3857&"
                "bbox=-1252344.27,4383204.95,-626172.14,5322463.15"
            )
            
            print(f"   A transferir {nome_ficheiro} ({data_alvo})...")
            
            response = page.goto(url_wms, timeout=120000, wait_until="commit")
            
            if response and response.status == 200:
                with open(nome_ficheiro, "wb") as f:
                    f.write(response.body())
                print(f"   Sucesso: {nome_ficheiro} guardado!")
            else:
                print(f"   Falha ao obter {nome_ficheiro}. O IPMA pode não ter este dia disponível.")
                
        browser.close()

def capturar_mapas_SMI():
    print("\n-> A compilar mapas SMI (Montagem do Mapa Base Esri + Camada WMS do IPMA)...")
    hoje = datetime.now()
    pasta_raiz = os.getcwd()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Tamanho vertical tipo "retrato" para focar perfeitamente em Portugal
        context = browser.new_context(viewport={'width': 800, 'height': 1200})
        page = context.new_page()
        
        for d in range(3):
            data_alvo = (hoje + timedelta(days=d)).strftime("%Y-%m-%d")
            nome_ficheiro = "smi_hoje.png" if d == 0 else "smi_amanha.png" if d == 1 else "smi_depois.png"
            print(f"   A compilar {nome_ficheiro} ({data_alvo})...")
            
            # Criamos uma página HTML virtual na hora, que junta o Mapa de Fundo da Esri, os dados do IPMA e as Fronteiras por cima
            html_mapa = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                <style>body, html {{ margin: 0; padding: 0; width: 800px; height: 1200px; background-color: #f8f9fa; }} #map {{ width: 100%; height: 100%; }}</style>
            </head>
            <body>
                <div id="map"></div>
                <script>
                    var map = L.map('map', {{ zoomControl: false, attributionControl: false }});
                    
                    // CAMADA 1: O Mapa base por baixo (Esri World Light Gray Base)
                    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                        maxZoom: 16
                    }}).addTo(map);
                    
                    // CAMADA 2: Os dados transparentes do SMI (IPMA)
                    L.tileLayer.wms('https://cs2.ipma.pt/wms', {{
                        dataset: 'smi-forecast_10p1d-continental-ecmwf',
                        layers: 'PT:IPMA:CDG:LAYER:smi-forecast_10p1d-continental-ecmwf_latest',
                        format: 'image/png',
                        transparent: true,
                        version: '1.1.1',
                        time: '{data_alvo}T00:00:00.000Z',
                        dim_layer: '100'
                    }}).addTo(map);

                    // CAMADA 3: Nomes e Fronteiras por Cima (Esri World Light Gray Reference)
                    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                        maxZoom: 16
                    }}).addTo(map);
                    
                    // Focar as coordenadas exatas de Portugal Continental
                    map.fitBounds([[36.95, -9.5], [42.15, -6.2]]);
                </script>
            </body>
            </html>
            """
            
            try:
                # Injeta a página construída no navegador e espera que todas as 3 camadas carreguem perfeitamente (5 segundos)
                page.set_content(html_mapa)
                page.wait_for_timeout(5000) 
                
                # Tira a fotografia ao mapa já comletamente montado
                page.screenshot(path=os.path.join(pasta_raiz, nome_ficheiro))
                print(f"   ✔️ Sucesso: {nome_ficheiro} compilado e guardado!")
                
            except Exception as e:
                print(f"   ❌ Falha ao compilar {nome_ficheiro}: {e}")
                
        browser.close()

def capturar_mapas_Bacias():
    print("\n-> A iniciar captura dos mapas de Bacias Hidrográficas...")
    pasta_raiz = os.getcwd()
    hoje = datetime.now()
    
    MEU_UTILIZADOR = os.environ.get("IPMA_USER", "escreve_aqui_o_utilizador")
    MINHA_PASSWORD = os.environ.get("IPMA_PASS", "escreve_aqui_a_password")
    
    caminho_creds = os.path.join(pasta_raiz, "credenciais.json")
    if os.path.exists(caminho_creds):
        try:
            with open(caminho_creds, 'r') as f:
                creds = json.load(f)
                MEU_UTILIZADOR = creds.get('utilizador', MEU_UTILIZADOR)
                MINHA_PASSWORD = creds.get('password', MINHA_PASSWORD)
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        context = browser.new_context(
            viewport={'width': 1200, 'height': 1200},
            http_credentials={'username': MEU_UTILIZADOR, 'password': MINHA_PASSWORD}
        )
        page = context.new_page()
        
        for d in range(3):
            data_alvo = (hoje + timedelta(days=d)).strftime("%Y-%m-%d")
            nome_ficheiro = "bacias_hoje.png" if d == 0 else "bacias_amanha.png" if d == 1 else "bacias_depois.png"
            
            print(f"   A processar {nome_ficheiro} ({data_alvo})...")
            try:
                page.goto(f"https://protecaocivil.ipma.pt/produtos/precipitacao-total-observada-e-prevista-por-bacia-2-a-9-dias/?data={data_alvo}", timeout=60000)
                page.wait_for_timeout(5000)
                
                page.evaluate("""
                    var els = document.querySelectorAll('header, footer, nav, .navbar, .site-header, .widget');
                    els.forEach(el => { if(el) el.style.display = 'none'; });
                """)
                
                locators = [".entry-content img", ".entry-content iframe", "#main-content", "article"]
                elemento_mapa = None
                
                for seletor in locators:
                    if page.locator(seletor).count() > 0:
                        elemento_mapa = page.locator(seletor).first
                        break
                        
                if elemento_mapa:
                    elemento_mapa.screenshot(path=os.path.join(pasta_raiz, nome_ficheiro))
                    print(f"   ✔️ Sucesso: {nome_ficheiro} guardado.")
                else:
                    page.screenshot(path=os.path.join(pasta_raiz, nome_ficheiro), full_page=True)
                    print(f"   ✔️ Sucesso (Fallback Vista Geral): {nome_ficheiro} guardado.")
                    
            except Exception as e:
                print(f"   ❌ Erro ao capturar mapa das Bacias: {e}")
                
        browser.close()

if __name__ == "__main__":
    capturar_mapas_PE()
    capturar_mapas_PIR()
    capturar_mapas_SMI()
    capturar_mapas_Bacias()
