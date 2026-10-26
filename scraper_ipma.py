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
    print("\n-> A iniciar captura dos mapas SMI (Página Original do IPMA)...")
    pasta_raiz = os.getcwd()
    hoje = datetime.now()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Resolução ampla para garantir que o mapa carrega com máxima qualidade
        context = browser.new_context(viewport={'width': 1200, 'height': 1200})
        page = context.new_page()
        
        try:
            print("   A aceder ao portal de Previsão SMI...")
            page.goto("https://www.ipma.pt/pt/agrometeorologia/smi/prev-smi.jsp", timeout=60000)
            page.wait_for_timeout(5000)
            
            # Limpa o lixo visual para que a fotografia incida apenas no mapa limpo
            page.evaluate("""
                var els = document.querySelectorAll('header, footer, nav, [id*=cookie], #nav-left, .breadcrumb, .leaflet-control-container');
                els.forEach(el => { if(el) el.style.display = 'none'; });
            """)
            
            for d in range(3):
                data_alvo = (hoje + timedelta(days=d)).strftime("%Y-%m-%d")
                nome_ficheiro = "smi_hoje.png" if d == 0 else "smi_amanha.png" if d == 1 else "smi_depois.png"
                
                print(f"   A processar {nome_ficheiro} ({data_alvo})...")
                
                # Injeção Cirúrgica: Altera APENAS a data da camada de água do IPMA.
                # Como usamos o mapa original da página, o fundo e as fronteiras ficam intactos!
                page.evaluate(f"""
                    let newTime = '{data_alvo}T00:00:00.000Z';
                    let tiles = document.querySelectorAll('img.leaflet-tile');
                    tiles.forEach(img => {{
                        // Verifica se é a imagem dos dados do SMI e altera o parâmetro 'time'
                        if (img.src.includes('smi-forecast')) {{
                            img.src = img.src.replace(/time=[^&]+/, 'time=' + newTime);
                        }}
                    }});
                """)
                
                # Aguardar 4 segundos para o navegador carregar os novos dados coloridos
                page.wait_for_timeout(4000)
                
                # Localiza a caixa exata do mapa e tira o Screenshot
                locators = [".leaflet-container", "#map", ".main-content img", "#content"]
                elemento_mapa = None
                
                for seletor in locators:
                    if page.locator(seletor).count() > 0:
                        elemento_mapa = page.locator(seletor).first
                        break
                        
                if elemento_mapa:
                    elemento_mapa.screenshot(path=os.path.join(pasta_raiz, nome_ficheiro))
                    print(f"   ✔️ Sucesso: {nome_ficheiro} guardado.")
                else:
                    print(f"   ❌ Falha: Não foi possível detetar o contentor do mapa.")
                    
        except Exception as e:
            print(f"   ❌ Erro durante o processamento do SMI: {e}")
            
        finally:
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
