import os
from playwright.sync_api import sync_playwright

def capturar_mapas():
    pasta_raiz = os.getcwd()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1200, 'height': 1200})
        page = context.new_page()
        
        page.goto("https://www.ipma.pt/pt/riscoincendio/fwi/")
        page.wait_for_selector(".leaflet-container", timeout=30000)
        page.wait_for_timeout(8000) # Espera pelas fronteiras da CAOP
        
        # Limpa o "lixo" visual em volta do mapa
        page.evaluate("""
            var els = document.querySelectorAll('header, footer, nav, [id*=cookie]');
            els.forEach(el => { if(el) el.style.display = 'none'; });
        """)
        
        mapa = page.locator(".leaflet-container").first
        
        # --- FUNÇÕES DE LIMPEZA DOS CONTROLOS ---
        # Esconde os botões do mapa momentaneamente só para a foto ficar "limpa"
        def esconder_menus():
            page.evaluate("document.querySelectorAll('.leaflet-control-container').forEach(e => e.style.display = 'none');")
        def mostrar_menus():
            page.evaluate("document.querySelectorAll('.leaflet-control-container').forEach(e => e.style.display = 'block');")

        # 1. MAPA DE HOJE
        esconder_menus()
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_hoje_PE.png"))
        print("Guardado com sucesso: portugal_hoje_PE.png")
        mostrar_menus()
        
        # 2. MAPA DE AMANHÃ
        try:
            # Clica no 2º input (radio button) do controlo de datas do IPMA
            page.evaluate("""
                var radios = document.querySelectorAll('input[type=radio]');
                if(radios.length > 1) { radios[1].click(); }
            """)
            page.wait_for_timeout(4000) # Espera a cor atualizar
            esconder_menus()
            mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_amanha_PE.png"))
            print("Guardado com sucesso: portugal_amanha_PE.png")
            mostrar_menus()
        except Exception as e:
            print("Aviso: Falha ao mudar para o mapa de Amanhã.")

        # 3. MAPA DE DEPOIS DE AMANHÃ
        try:
            # Clica no 3º input (radio button) do controlo de datas
            page.evaluate("""
                var radios = document.querySelectorAll('input[type=radio]');
                if(radios.length > 2) { radios[2].click(); }
            """)
            page.wait_for_timeout(4000)
            esconder_menus()
            mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_depois_PE.png"))
            print("Guardado com sucesso: portugal_depois_PE.png")
            mostrar_menus()
        except Exception as e:
            print("Aviso: Falha ao mudar para o mapa de Depois de Amanhã.")
            
        browser.close()

if __name__ == "__main__":
    capturar_mapas()
