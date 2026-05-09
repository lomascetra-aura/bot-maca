import streamlit as st
import requests

# Configuração Nitro
st.set_page_config(layout="wide", page_title="NITRO ENGINE | MACA")
st.title("🔥 NITRO ARB - TRATOR DE LUCRO 2026")

# --- PAINEL DE CONTROLE ---
col1, col2, col3 = st.columns(3)
with col1:
    bankroll = st.number_input("Banca Total (R$)", value=500.0, step=50.0)
with col2:
    esporte_label = st.selectbox(
        "Alvo do Trator",
        ["Futebol (Brasil)", "NBA (Basquete)", "Tênis (ATP)", "Futebol (Inglês)", "MMA (UFC)"]
    )
with col3:
    mercado_selecionado = st.selectbox(
        "Tipo de Mercado",
        ["Vencedor (H2H)", "Totais (Gols/Points)"]
    )

# Mapeamentos
mapa_esportes = {
    "Futebol (Brasil)": "soccer_brazil_campeonato",
    "NBA (Basquete)": "basketball_nba",
    "Tênis (ATP)": "tennis_atp", 
    "Futebol (Inglês)": "soccer_epl",
    "MMA (UFC)": "mma_mixed_martial_arts"
}

mapa_mercados = {
    "Vencedor (H2H)": "h2h",
    "Totais (Gols/Points)": "totals"
}

API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
ALLOWED_BOOKS = ["pinnacle", "betfair_ex", "bet365", "betano", "1xbet", "stake", "bwin"]
BOOKS_QUERY = ",".join(ALLOWED_BOOKS)

def calc_stakes(bankroll, odds):
    inv = sum(1/o for o in odds)
    profit_pct = (1 - inv) * 100
    stakes = [(bankroll / o) / inv for o in odds]
    profit = (stakes[0] * odds[0]) - bankroll
    return {"profit_pct": profit_pct, "profit": profit, "stakes": stakes}

if st.button("🚀 INICIAR VARREDURA AGRESSIVA"):
    with st.spinner("CAÇANDO OPORTUNIDADES..."):
        target_sport = mapa_esportes[esporte_label]
        target_market = mapa_mercados[mercado_selecionado]
        
        # Correção para Tênis dinâmico
        if esporte_label == "Tênis (ATP)":
            try:
                url_s = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
                active = [s['key'] for s in requests.get(url_s).json() if "tennis_atp" in s['key']]
                if active: target_sport = active[0]
                else: st.warning("Sem tênis ativo."); st.stop()
            except: st.stop()

        URL = f"https://api.the-odds-api.com/v4/sports/{target_sport}/odds/?apiKey={API_KEY}&regions=eu&markets={target_market}&oddsFormat=decimal&bookmakers={BOOKS_QUERY}"
        
        try:
            res = requests.get(URL).json()
            if not isinstance(res, list) or len(res) == 0:
                st.warning("📭 Sem dados.")
            else:
                arbs, monitoring = [], []
                for game in res:
                    game_name = f"{game['home_team']} vs {game['away_team']}"
                    
                    if target_market == "h2h":
                        best_odds_h2h = {}
                        for book in game.get('bookmakers', []):
                            if book['key'] not in ALLOWED_BOOKS: continue
                            for market in book.get('markets', []):
                                if market['key'] == 'h2h':
                                    for o in market['outcomes']:
                                        if o['name'] not in best_odds_h2h or o['price'] > best_odds_h2h[o['name']]['price']:
                                            best_odds_h2h[o['name']] = {"price": o['price'], "book": book['title']}
                        
                        if len(best_odds_h2h) >= 2:
                            names = list(best_odds_h2h.keys())
                            prices = [best_odds_h2h[n]['price'] for n in names]
                            data = calc_stakes(bankroll, prices)
                            item = {"game": game_name, "data": data, "names": names, "details": best_odds_h2h, "type": "H2H"}
                            if data['profit_pct'] > 0: arbs.append(item)
                            elif data['profit_pct'] > -5.0: monitoring.append(item)

                    else:
                        # Lógica para TOTAIS (Agora com POINT explícito)
                        totals_groups = {}
                        for book in game.get('bookmakers', []):
                            if book['key'] not in ALLOWED_BOOKS: continue
                            for market in book.get('markets', []):
                                if market['key'] == 'totals':
                                    for o in market['outcomes']:
                                        point = o['point']
                                        label = f"{o['name']} {point}" # Ex: Over 2.5
                                        if label not in totals_groups or o['price'] > totals_groups[label]['price']:
                                            totals_groups[label] = {"price": o['price'], "book": book['title'], "point": point, "side": o['name']}
                        
                        points = set([v['point'] for v in totals_groups.values()])
                        for p in points:
                            over_key, under_key = f"Over {p}", f"Under {p}"
                            if over_key in totals_groups and under_key in totals_groups:
                                o_data, u_data = totals_groups[over_key], totals_groups[under_key]
                                data = calc_stakes(bankroll, [o_data['price'], u_data['price']])
                                item = {"game": game_name, "line": p, "data": data, "names": [over_key, under_key], 
                                        "details": {over_key: o_data, under_key: u_data}, "type": "TOTAL"}
                                if data['profit_pct'] > 0: arbs.append(item)
                                elif data['profit_pct'] > -5.0: monitoring.append(item)

                # --- EXIBIÇÃO ---
                if arbs:
                    st.subheader("💰 ENTRADA CONFIRMADA!")
                    for r in arbs:
                        header = f"✅ {r['data']['profit_pct']:.2f}% | {r['game']}"
                        if r['type'] == "TOTAL": header += f" (LINHA: {r['line']})"
                        
                        with st.expander(header, expanded=True):
                            st.write(f"**LUCRO LÍQUIDO: R$ {r['data']['profit']:.2f}**")
                            cols = st.columns(len(r['names']))
                            for i, name in enumerate(r['names']):
                                info = r['details'][name]
                                cols[i].metric(f"R$ {r['data']['stakes'][i]:.2f}", f"{name} @ {info['price']}", info['book'])
                
                st.subheader("👀 RADAR NITRO")
                for r in monitoring[:8]:
                    info_txt = f"📊 {r['data']['profit_pct']:.2f}% | {r['game']}"
                    if r['type'] == "TOTAL": info_txt += f" | LINHA: {r['line']}"
                    st.info(info_txt)

        except Exception as e: st.error(f"Erro: {e}")

st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
