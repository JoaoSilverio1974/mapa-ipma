from playwright.sync_api import sync_playwright

def capturar_mapas():
    with sync_playwright() as p:
        print("A iniciar o browser invisível...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1200, 'height': 1200})
        page = context.new_page()
        
        try:
            print("A aceder ao site do IPMA...")
            page.goto("https://www.ipma.pt/pt/riscoincendio/fwi/")
            
            # Aguarda garantidamente pelo motor do mapa (Leaflet)
            page.wait_for_selector(".leaflet-container", timeout=20000)
            
            # Espera 5 segundos extra para que todos os polígonos da CAOP carreguem
            page.wait_for_timeout(5000) 
            
            print("A limpar banners e menus (Cookies, etc)...")
            page.evaluate("""
                // Esconde cabeçalhos, rodapés e controlos do mapa
                var elementos = document.querySelectorAll('header, footer, nav, .breadcrumb, .leaflet-control-container');
                elementos.forEach(function(el) { if(el) el.style.display = 'none'; });
                
                // Força o fecho de qualquer banner de cookies que possa tapar o mapa
                var cookies = document.querySelectorAll('[id*="cookie"], [class*="cookie"]');
                cookies.forEach(function(c) { if(c) c.style.display = 'none'; });
            """)
            
            # Agarra o mapa pela classe universal do Leaflet
            elemento_mapa = page.locator(".leaflet-container").first
            
            print("A capturar mapa de HOJE...")
            elemento_mapa.screenshot(path="portugal_hoje.png")
            
            # Tenta capturar os outros dias
            try:
                print("A capturar mapa de AMANHÃ...")
                # Procura qualquer botão que contenha a palavra "Amanhã" ou "+ 24"
                page.locator('text="Amanhã"').first.click(timeout=5000)
                page.wait_for_timeout(3000)
                elemento_mapa.screenshot(path="portugal_amanha.png")
                
                print("A capturar mapa de DEPOIS DE AMANHÃ...")
                page.locator('text="Depois de amanhã"').first.click(timeout=5000)
                page.wait_for_timeout(3000)
                elemento_mapa.screenshot(path="portugal_depois.png")
            except Exception as e2:
                print("Aviso: Não encontrou os botões dos dias seguintes, ou as palavras mudaram. Apenas Hoje foi guardado.")
                
        except Exception as e:
            print(f"ERRO CRÍTICO: Falha ao processar o mapa. Detalhes: {str(e)}")
            
        finally:
            browser.close()
            print("Processo terminado.")

if __name__ == "__main__":
    capturar_mapas()
