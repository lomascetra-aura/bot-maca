import streamlit as st
import requests

# =========================
# CONFIGURAÇÃO DE INTERFACE
# =========================
st.set_page_config(layout="wide", page_title="NITRO ARB BRASIL")
st.title("🔥 NITRO ARB - RADAR GLOBAL V8.3")

# =========================
# PAINEL DE CONTROLE
# =========================
col1, col2, col3 = st.columns(3)
with col1:
    bankroll = st.number_input("Banca Total (R$)", value=500.0, step=50.0)
with col2:
    esporte_label = st.selectbox(
        "Escolha o Esporte/Liga",
        [
            "Futebol Espanha (La Liga)", 
            "Futebol Alemanha (Bundesliga)",
            "Futebol Itália (Serie A)",
            "Futebol Champions League",
            "Futebol Libertadores",
            "Futebol Portugal (Primeira Liga)",
            "Futebol Brasil (Série A)", 
            "NBA (Basquete)", 
            "Tênis (ATP)", 
            "Futebol Inglês (EPL)", 
            "MMA/UFC"
        ]
    )
with col3:
    mercado_label = st.selectbox(
        "Escolha o Mercado",
        ["Vencedor (H2H)", "Totais (Over/Under)"]
    )

# =========================
# CONFIGURAÇÕES TÉCNICAS
# =========================
API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"

SPORTS_MAP = {
    "Futebol Espanha (La Liga)": "soccer_spain_la_liga",
    "Futebol Alemanha (Bundesliga)": "soccer_germany_bundesliga",
    "Futebol Itália (Serie A)": "soccer_italy_serie_a",
    "Futebol Champions League": "soccer_uefa_champs_league",
    "Futebol Libertadores": "soccer_conmebol_libertadores",
    "Futebol Portugal (Primeira Liga)": "soccer_portugal_primeira_liga",
    "Futebol Brasil (Série A)": "soccer_brazil_campeonato",
    "Futebol Inglês (EPL)": "soccer_epl",
    "NBA (Basquete)": "basketball_nba",
    "Tênis (ATP)": "tennis_atp",
    "MMA/UFC": "mma_mixed_martial_arts"
}

MARKET_KEY = "h2h" if mercado_label == "Vencedor (H2H)" else "totals"

# William Hill Removida conforme ordem do Mestre Maca
ALLOWED_BOOKS = "pinnacle,bet365,betano,1xbet,betfair_ex,marathonbet,888sport,bwin,unibet,stake"

# Filtros para Radar Total (Vigiar tudo)
MIN_PROFIT = -10.0
MAX_RESULTS = 20

def calc_stakes(bankroll, odds):
    inv = sum(1 / o for o in odds)
    profit_pct = (1 - inv) * 100
    stakes = [(bankroll / o) / inv for o in odds]
    guaranteed_profit = (stakes[0] * odds[0]) - bankroll
    return {"profit_pct": profit_pct, "profit": guaranteed_profit, "stakes": stakes}

# =========================
# EXECUÇÃO DO SCANNER
# =========================
if st.button("🚀 EXECUTAR VARREDURA AGRESSIVA"):
    with st.spinner(f"VARRENDO {esporte_label.upper()}..."):
        sport_key = SPORTS_MAP[esporte_label]

        # Ajuste Inteligente para Tênis
        if "Tênis" in esporte_label:
            try:
                active_res = requests.get(f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}").json()
                active_tennis = [s["key"] for s in active_res if "tennis_atp" in s["key"]]
                if active_tennis: sport_key = active_tennis[0]
            except: pass

        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={API_KEY}&regions=eu&markets={MARKET_KEY}&oddsFormat=decimal&bookmakers={ALLOWED_BOOKS}"

        try:
            response = requests.get(url, timeout=15)
            data = response.json()

            if response.status_code != 200:
                st.error(f"Erro na API: {data.get('msg', 'Verifique seus créditos.')}")
                st.stop()

            opportunities = []

            for game in data:
                game_name = f"{game.get('home_team')} vs {game.get('away_team')}"
                
                if MARKET_KEY == "h2h":
                    best_odds = {}
                    for book in game.get("bookmakers", []):
                        for mkt in book.get("markets", []):
                            for outcome in mkt.get("outcomes", []):
                                name = outcome["name"]
                                if name not in best_odds or outcome["price"] > best_odds[name]["price"]:
                                    best_odds[name] = {"price": outcome["price"], "book": book['title']}
                    
                    if len(best_odds) >= 2:
                        names = sorted(best_odds.keys())
                        prices = [best_odds[n]["price"] for n in names]
                        res = calc_stakes(bankroll, prices)
                        if res["profit_pct"] >= MIN_PROFIT:
                            opportunities.append({"game": game_name, "data": res, "names": names, "details": best_odds, "type": "H2H"})
                else:
                    totals = {}
                    for book in game.get("bookmakers", []):
                        for mkt in book.get("markets", []):
                            for outcome in mkt.get("outcomes", []):
                                label = f"{outcome['name']} {outcome['point']}"
                                if label not in totals or outcome["price"] > totals[label]["price"]:
                                    totals[label] = {"price": outcome["price"], "book": book['title'], "point": outcome["point"]}
                    
                    lines = set([v["point"] for v in totals.values()])
                    for p in lines:
                        o_k, u_k = f"Over {p}", f"Under {p}"
                        if o_k in totals and u_k in totals:
                            prices = [totals[o_k]["price"], totals[u_k]["price"]]
                            res = calc_stakes(bankroll, prices)
                            if res["profit_pct"] >= MIN_PROFIT:
                                opportunities.append({"game": game_name, "data": res, "names": [o_k, u_k], "details": {o_k: totals[o_k], u_k: totals[u_k]}, "type": "TOTAL", "line": p})

            if opportunities:
                opportunities = sorted(opportunities, key=lambda x: x["data"]["profit_pct"], reverse=True)[:MAX_RESULTS]
                for arb in opportunities:
                    p_pct = arb["data"]["profit_pct"]
                    
                    # Estilo Visual: Verde para Lucro, Azul para Radar
                    if p_pct > 0:
                        header = f"✅ LUCRO: {p_pct:.2f}% | {arb['game']}"
                        with st.expander(header, expanded=True):
                            st.success(f"### Retorno Garantido: R$ {arb['data']['profit']:.2f}")
                            cols = st.columns(len(arb["names"]))
                            for i, name in enumerate(arb["names"]):
                                info = arb["details"][name]
                                cols[i].metric(name, f"Odd {info['price']}", info['book'])
                                cols[i].warning(f"**Apostar: R$ {arb['data']['stakes'][i]:.2f}**")
                    else:
                        header = f"📊 RADAR: {p_pct:.2f}% | {arb['game']}"
                        with st.expander(header):
                            st.info(f"Monitorando diferença de odds: {p_pct:.2f}%")
                            cols = st.columns(len(arb["names"]))
                            for i, name in enumerate(arb["names"]):
                                info = arb["details"][name]
                                cols[i].write(f"**{name}**")
                                cols[i].write(f"Odd: {info['price']} ({info['book']})")
                                cols[i].write(f"Sugerido: R$ {arb['data']['stakes'][i]:.2f}")
            else:
                st.info("Nenhuma odd encontrada. Tente outra liga ou mercado.")

        except Exception as e:
            st.error(f"Erro no motor Nitro: {e}")

st.divider()
st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
