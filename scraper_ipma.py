import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def capturar_mapas():
    pasta_raiz = os.getcwd()
    
    # 1. Calcula as datas exatas (Hoje, Amanhã e Depois)
    hoje = datetime.now()
    amanha = hoje + timedelta(days=1)
    depois = hoje + timedelta(days=2)
    
    # 2. Formata as datas no padrão que o IPMA exige (YYYY-MM-DD)
    fmt_hoje = hoje.strftime("%Y-%m-%d")
    fmt_amanha = amanha.strftime("%Y-%m-%d")
    fmt_depois = depois.strftime("%Y-%m-%d")
    
    # A estrutura base do link que você descobriu
    url_base = "https://api.ipma.pt/public-data/mf2_preview/lsasaf_p2000_continent/lsasaf_p2000_continent_{}T00_00_00.png"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1200, 'height': 1200})
        page = context.new_page()
        
        page.goto("https://www.ipma.pt/pt/riscoincendio/fwi/")
        page.wait_for_selector(".leaflet-container", timeout=30000)
        page.wait_for_timeout(6000) # Espera pelas fronteiras (CAOP)
        
        # Limpa menus, cookies e banners
        page.evaluate("""
            var els = document.querySelectorAll('header, footer, nav, [id*=cookie], .leaflet-control-container');
            els.forEach(el => { if(el) el.style.display = 'none'; });
        """)
        
        mapa = page.locator(".leaflet-container").first
        
        # --- A MAGIA ACONTECE AQUI ---
        # Função que força o mapa a mudar a cor no ecrã usando os seus links, sem mexer nas fronteiras!
        js_mudar_imagem = """(novaUrl) => {
            var imagens = document.querySelectorAll('img[src*="lsasaf_p2000"]');
            imagens.forEach(img => img.src = novaUrl);
        }"""
        
        # 1. MAPA DE HOJE
        link_hoje = url_base.format(fmt_hoje)
        page.evaluate(js_mudar_imagem, link_hoje)
        page.wait_for_timeout(3000) # Espera 3 segundos para a cor atualizar no ecrã
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_hoje_PE.png"))
        print(f"Sucesso: portugal_hoje_PE.png ({fmt_hoje})")
        
        # 2. MAPA DE AMANHÃ
        link_amanha = url_base.format(fmt_amanha)
        page.evaluate(js_mudar_imagem, link_amanha)
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_amanha_PE.png"))
        print(f"Sucesso: portugal_amanha_PE.png ({fmt_amanha})")
        
        # 3. MAPA DE DEPOIS DE AMANHÃ
        link_depois = url_base.format(fmt_depois)
        page.evaluate(js_mudar_imagem, link_depois)
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_depois_PE.png"))
        print(f"Sucesso: portugal_depois_PE.png ({fmt_depois})")
        
        browser.close()

if __name__ == "__main__":
    capturar_mapas()
