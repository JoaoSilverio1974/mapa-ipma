from playwright.sync_api import sync_playwright

def capturar_mapas():
    with sync_playwright() as p:
        # Lança um browser invisível
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1000, 'height': 1200})
        page = context.new_page()
        
        print("A abrir o site do IPMA...")
        page.goto("https://www.ipma.pt/pt/riscoincendio/fwi/")
        
        # Espera que o mapa e as fronteiras vetoriais (SVG) carreguem
        page.wait_for_selector(".leaflet-pane", timeout=15000)
        page.wait_for_timeout(4000) # Buffer para os azulejos do mapa surgirem
        
        # Injeta código para esconder cabeçalhos, rodapés e menus laterais
        page.evaluate("""
            var elementos = document.querySelectorAll('header, footer, nav, .breadcrumb, .leaflet-control-container');
            elementos.forEach(function(el) { el.style.display = 'none'; });
        """)
        
        # Define qual é a "caixa" do ecrã que queremos fotografar (o mapa)
        elemento_mapa = page.locator("#map")
        
        print("A capturar mapa de HOJE...")
        elemento_mapa.screenshot(path="portugal_hoje.png")
        
        # Simula o clique nos dias seguintes (Ajuste a palavra exata se o site mudar)
        try:
            print("A capturar mapa de AMANHÃ...")
            # Clica na aba ou botão que diz "Amanhã" ou no dia seguinte
            page.locator('text="Amanhã"').first.click()
            page.wait_for_timeout(3000) # Espera que a cor mude
            elemento_mapa.screenshot(path="portugal_amanha.png")
            
            print("A capturar mapa de DEPOIS DE AMANHÃ...")
            page.locator('text="Depois de amanhã"').first.click()
            page.wait_for_timeout(3000)
            elemento_mapa.screenshot(path="portugal_depois.png")
        except Exception as e:
            print("Aviso: Não foi possível clicar nos botões dos dias seguintes. Apenas hoje foi capturado.")

        browser.close()
        print("Mapas gerados com sucesso!")

if __name__ == "__main__":
    capturar_mapas()
