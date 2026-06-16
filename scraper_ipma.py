import os
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def capturar_mapas_PE():
    print("-> A iniciar captura dos mapas PE (Playwright)...")
    pasta_raiz = os.getcwd()
    
    hoje = datetime.now()
    amanha = hoje + timedelta(days=1)
    depois = hoje + timedelta(days=2)
    
    fmt_hoje = hoje.strftime("%Y-%m-%d")
    fmt_amanha = amanha.strftime("%Y-%m-%d")
    fmt_depois = depois.strftime("%Y-%m-%d")
    
    url_base = "https://api.ipma.pt/public-data/mf2_preview/lsasaf_p2000_continent/lsasaf_p2000_continent_{}T00_00_00.png"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1200, 'height': 1200})
        page = context.new_page()
        
        page.goto("https://www.ipma.pt/pt/riscoincendio/fwi/")
        page.wait_for_selector(".leaflet-container", timeout=30000)
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
        
        # MAPA HOJE PE
        link_hoje = url_base.format(fmt_hoje)
        page.evaluate(js_mudar_imagem, link_hoje)
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_hoje_PE.png"))
        print(f"   Sucesso: portugal_hoje_PE.png ({fmt_hoje})")
        
        # MAPA AMANHA PE
        link_amanha = url_base.format(fmt_amanha)
        page.evaluate(js_mudar_imagem, link_amanha)
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_amanha_PE.png"))
        print(f"   Sucesso: portugal_amanha_PE.png ({fmt_amanha})")
        
        # MAPA DEPOIS PE
        link_depois = url_base.format(fmt_depois)
        page.evaluate(js_mudar_imagem, link_depois)
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_depois_PE.png"))
        print(f"   Sucesso: portugal_depois_PE.png ({fmt_depois})")
        
        browser.close()

def capturar_mapas_PIR():
    print("\n-> A iniciar geração dos mapas PIR/RCM (JSON/Matplotlib)...")
    CORES_RISCO = {
        "1": "#90EE90", "2": "#FFFF66", "3": "#F4A460", 
        "4": "#DC6464", "5": "#8B5A69"
    }

    for d in range(3):
        data_alvo = (datetime.now() + timedelta(days=d)).strftime("%Y-%m-%d")
        nome_ficheiro = "portugal_hoje.png" if d == 0 else "portugal_amanha.png" if d == 1 else "portugal_depois.png"
        
        url = f"https://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d{d}.json"
        resposta = requests.get(url)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            fig, ax = plt.subplots(figsize=(5, 10))
            ax.set_facecolor('#E6F2FF')
            
            lista_registos = dados.get('data', [])
            x_pos, y_pos = 10, 950
            
            for registo in lista_registos:
                if isinstance(registo, dict):
                    rcm_val = str(registo.get('rcm', 1))
                    cor = CORES_RISCO.get(rcm_val, "#90EE90")
                    
                    ax.add_patch(plt.Rectangle((x_pos, y_pos), 6, 6, color=cor, edgecolor='none'))
                    
                    x_pos += 8
                    if x_pos > 85:
                        x_pos = 10
                        y_pos -= 10
                    if y_pos < 50: 
                        break
            
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 1000)
            ax.axis('off')
            
            plt.title(f"RISCO INCÊNDIO (PIR) - {data_alvo}", fontsize=14, fontweight='bold', pad=20)
            plt.tight_layout()
            plt.savefig(nome_ficheiro, dpi=100, facecolor=fig.get_facecolor(), edgecolor='none')
            plt.close()
            print(f"   Sucesso: {nome_ficheiro}")
        else:
            print(f"   Falha ao aceder à API PIR no dia {d}")

if __name__ == "__main__":
    print("==== INÍCIO DO PROCESSO ====")
    capturar_mapas_PE()
    capturar_mapas_PIR()
    print("==== PROCESSO CONCLUÍDO ====")
