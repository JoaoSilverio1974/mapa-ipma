import os
import json
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def capturar_mapas_PE():
    print("-> A transferir mapas PE (Download Direto da API IPMA)...")
    hoje = datetime.now()
    pasta_raiz = os.getcwd()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for d in range(3):
            data_alvo = (hoje + timedelta(days=d)).strftime("%Y-%m-%d")
            nome_ficheiro = "portugal_hoje_PE.png" if d == 0 else "portugal_amanha_PE.png" if d == 1 else "portugal_depois_PE.png"
            
            url_pe = f"https://api.ipma.pt/public-data/mf2_preview/lsasaf_p2000_continent/lsasaf_p2000_continent_{data_alvo}T00_00_00.png"
            
            print(f"   A transferir {nome_ficheiro} ({data_alvo})...")
            try:
                response = page.goto(url_pe, timeout=120000, wait_until="commit")
                if response and response.status == 200 and "image" in response.headers.get("content-type", ""):
                    with open(os.path.join(pasta_raiz, nome_ficheiro), "wb") as f:
                        f.write(response.body())
                    print(f"   ✔️ Sucesso: {nome_ficheiro} guardado!")
                else:
                    print(f"   ❌ Falha ao obter {nome_ficheiro} (Content-Type inválido ou dia indisponível).")
            except Exception as e:
                print(f"   ❌ Erro ao transferir {nome_ficheiro}: {e}")
                
        browser.close()

def capturar_mapas_PIR():
    print("\n-> A transferir mapas PIR (Download Direto do Servidor IPMA)...")
    hoje = datetime.now()
    ano_atual = hoje.year
    pasta_raiz = os.getcwd()
    
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
            try:
                response = page.goto(url_wms, timeout=120000, wait_until="commit")
                if response and response.status == 200 and "image" in response.headers.get("content-type", ""):
                    with open(os.path.join(pasta_raiz, nome_ficheiro), "wb") as f:
                        f.write(response.body())
                    print(f"   ✔️ Sucesso: {nome_ficheiro} guardado!")
                else:
                    print(f"   ❌ Falha ao obter {nome_ficheiro}.")
            except Exception as e:
                print(f"   ❌ Erro ao transferir {nome_ficheiro}: {e}")
                
        browser.close()

def capturar_mapas_SMI():
    print("\n-> A compilar mapas SMI (Fundo Esri + Dados WMS IPMA + Limites Concelhos)...")
    hoje = datetime.now()
    pasta_raiz = os.getcwd()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 800, 'height': 1200})
        page = context.new_page()
        
        for d in range(3):
            data_alvo = (hoje + timedelta(days=d)).strftime("%Y-%m-%d")
            nome_ficheiro = "smi_hoje.png" if d == 0 else "smi_amanha.png" if d == 1 else "smi_depois.png"
            print(f"   A compilar {nome_ficheiro} ({data_alvo})...")
            
            html_mapa = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8" />
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                <style>
                    body, html {{ margin: 0; padding: 0; width: 800px; height: 1200px; background-color: #d0cfd4; }}
                    #map {{ width: 100%; height: 100%; }}
                </style>
            </head>
            <body>
                <div id="map"></div>
                <script>
                    var map = L.map('map', {{ zoomControl: false, attributionControl: false }});
                    
                    // 1. Fundo Base Esri (Cinzento limpo sem cidades)
                    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                        maxZoom: 16
                    }}).addTo(map);
                    
                    // 2. Camada WMS oficial do SMI do IPMA
                    L.tileLayer.wms('https://cs2.ipma.pt/wms?dataset=smi-forecast_10p1d-continental-ecmwf', {{
                        layers: 'PT:IPMA:CDG:LAYER:smi-forecast_10p1d-continental-ecmwf_latest',
                        format: 'image/png',
                        transparent: true,
                        version: '1.1.1',
                        time: '{data_alvo}T00:00:00.000Z',
                        dim_layer: '100'
                    }}).addTo(map);

                    // 3. Limites dos Concelhos de Portugal Continental por cima
                    fetch('https://raw.githubusercontent.com/dssg-pt/dados-Portugal/master/concelhos.geojson')
                        .then(r => r.json())
                        .then(data => {{
                            L.geoJSON(data, {{
                                style: {{
                                    color: '#111111',
                                    weight: 1.1,
                                    opacity: 0.85,
                                    fillOpacity: 0
                                }}
                            }}).addTo(map);
                            window.concelhosCarregados = true;
                        }})
                        .catch(err => {{
                            console.error(err);
                            window.concelhosCarregados = true;
                        }});
                    
                    // Enquadramento exato de Portugal Continental
                    map.fitBounds([[36.90, -9.55], [42.20, -6.15]]);
                </script>
            </body>
            </html>
            """
            
            try:
                page.set_content(html_mapa, wait_until="networkidle", timeout=60000)
                # Garante que o GeoJSON dos concelhos e os tiles WMS terminaram de renderizar
                page.wait_for_function("window.concelhosCarregados === true", timeout=30000)
                page.wait_for_timeout(3000)
                
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
                page.goto(f"https://protecaocivil.ipma.pt/produtos/precipitacao-total-observada-e-prevista-por-bacia-2-a-9-dias/?data={data_alvo}", timeout=120000, wait_until="commit")
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
