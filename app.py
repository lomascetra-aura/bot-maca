import streamlit as st
import requests
from datetime import datetime

# =========================
# CONFIGURAÇÃO NITRO
# =========================
st.set_page_config(layout="wide", page_title="NITRO ARB BRASIL")
st.title("🔥 NITRO ARB BRASIL 2026")
st.caption("Maca, o trator está pronto para a varredura!")

# =========================
# PAINEL DE CONTROLE
# =========================
col1, col2, col3 = st.columns(3)
with col1:
    bankroll = st.number_input("Banca Total (R$)", value=500.0, step=50.0)
with col2:
    esporte_label = st.selectbox(
        "Esporte",
        ["Tênis (ATP)", "NBA", "Futebol Brasil", "Futebol Inglês", "MMA/UFC"]
    )
with col3:
    mercado_label = st.selectbox(
        "Mercado",
        ["Vencedor (H2H)", "Totais"]
    )

# =========================
# CONFIGURAÇÕES TÉCNICAS
# =========================
SPORTS = {
    "Tênis (ATP)": "tennis_atp",
    "NBA": "basketball_nba",
    "Futebol Brasil": "soccer_brazil_campeonato",
    "Futebol Inglês": "soccer_epl",
    "MMA/UFC": "mma_mixed_martial_arts"
}

MARKETS = {"Vencedor (H2H)": "h2h", "Totais": "totals"}

# Chave API do Mestre Maca
API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"

# Casas selecionadas: Foco em liquidez e profissionalismo
ALLOWED_BOOKS = ["pinnacle", "stake", "betano", "bet365", "1xbet", "bwin"]
BOOKS_QUERY = ",".join(ALLOWED_BOOKS)

# Filtros
MIN_PROFIT = 0.5  
MIN_ODD = 1.35
MAX_RESULTS = 15

# =========================
# MOTOR DE CÁLCULO
# =========================
def calc_stakes(bankroll, odds):
    inv = sum(1 / o for o in odds)
    profit_pct = (1 - inv) * 100
    stakes = [(bankroll / o) / inv for o in odds]
    guaranteed_profit = (stakes[0] * odds[0]) - bankroll
    return {"profit_pct": profit_pct, "profit": guaranteed_profit, "stakes": stakes}

# =========================
# EXECUÇÃO DO SCANNER
# =========================
if st.button("🚀 ESCANEAR OPORTUNIDADES"):
    with st.spinner("TRATOR VARRENDO O MERCADO..."):
        sport_key = SPORTS[esporte_label]
        market_key = MARKETS[mercado_label]

        # ATP DINÂMICO
        if esporte_label == "Tênis (ATP)":
            try:
                res_sports = requests.get(f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}").json()
                active = [s["key"] for s in res_sports if "tennis_atp" in s["key"]]
                if active: sport_key = active[0]
                else: st.warning("Nenhum torneio ATP ativo no momento."); st.stop()
            except: st.error("Falha ao validar torneios ativos."); st.stop()

        # CHAMADA API
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={API_KEY}&regions=eu&markets={market_key}&oddsFormat=decimal&bookmakers={BOOKS_QUERY}"

        try:
            data = requests.get(url, timeout=15).json()
            if not isinstance(data, list) or len(data) == 0:
                st.warning("📭 Sem oportunidades agora. Tente outro esporte.")
                st.stop()

            opportunities = []

            for game in data:
                game_name = f"{game.get('home_team')} vs {game.get('away_team')}"
                
                # LÓGICA VENCEDOR (H2H)
                if market_key == "h2h":
                    best_odds = {}
                    for book in game.get("bookmakers", []):
                        for mkt in book.get("markets", []):
                            for outcome in mkt.get("outcomes", []):
                                name = outcome["name"]
                                if name not in best_odds or outcome["price"] > best_odds[name]["price"]:
                                    best_odds[name] = {"price": outcome["price"], "book": book["title"]}
                    
                    if len(best_odds) >= 2:
                        names = list(best_odds.keys())
                        prices = [best_odds[n]["price"] for n in names]
                        if min(prices) >= MIN_ODD:
                            res = calc_stakes(bankroll, prices)
                            if res["profit_pct"] >= MIN_PROFIT:
                                opportunities.append({"type": "H2H", "game": game_name, "profit_pct": res["profit_pct"], "profit": res["profit"], "stakes": res["stakes"], "names": names, "details": best_odds})

                # LÓGICA TOTAIS (Gols/Pontos)
                else:
                    totals = {}
                    for book in game.get("bookmakers", []):
                        for mkt in book.get("markets", []):
                            for outcome in mkt.get("outcomes", []):
                                label = f"{outcome['name']} {outcome['point']}"
                                if label not in totals or outcome["price"] > totals[label]["price"]:
                                    totals[label] = {"price": outcome["price"], "book": book["title"], "point": outcome["point"]}
                    
                    points = set([v["point"] for v in totals.values()])
                    for p in points:
                        o_k, u_k = f"Over {p}", f"Under {p}"
                        if o_k in totals and u_k in totals:
                            prices = [totals[o_k]["price"], totals[u_k]["price"]]
                            if min(prices) >= MIN_ODD:
                                res = calc_stakes(bankroll, prices)
                                if res["profit_pct"] >= MIN_PROFIT:
                                    opportunities.append({"type": "TOTAL", "game": game_name, "line": p, "profit_pct": res["profit_pct"], "profit": res["profit"], "stakes": res["stakes"], "names": [o_k, u_k], "details": {o_k: totals[o_k], u_k: totals[u_k]}})

            # EXIBIÇÃO DAS OPORTUNIDADES
            if opportunities:
                opportunities = sorted(opportunities, key=lambda x: x["profit_pct"], reverse=True)[:MAX_RESULTS]
                for arb in opportunities:
                    header = f"💰 {arb['profit_pct']:.2f}% | {arb['game']}"
                    if arb["type"] == "TOTAL": header += f" | Linha {arb['line']}"
                    with st.expander(header, expanded=True):
                        st.write(f"#### Retorno Garantido: R$ {arb['profit']:.2f}")
                        cols = st.columns(len(arb["names"]))
                        for i, name in enumerate(arb["names"]):
                            info = arb["details"][name]
                            cols[i].metric(label=name, value=f"@ {info['price']}", delta=info['book'])
                            cols[i].write(f"Apostar: **R$ {arb['stakes'][i]:.2f}**")
            else:
                st.info("Varredura completa: Nenhuma arbitragem lucrativa encontrada.")

        except Exception as e:
            st.error(f"Erro no motor Nitro: {e}")

st.divider()
st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
