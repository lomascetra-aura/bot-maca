import streamlit as st
import requests

# =========================
# CONFIGURAÇÃO DE INTERFACE
# =========================
st.set_page_config(layout="wide", page_title="NITRO ARB BRASIL")
st.title("🔥 NITRO ARB - MODO RADAR TOTAL")

# =========================
# PAINEL DE CONTROLE (CENTRALIZADO)
# =========================
col1, col2, col3 = st.columns(3)
with col1:
    bankroll = st.number_input("Banca Total (R$)", value=500.0, step=50.0)
with col2:
    esporte_label = st.selectbox(
        "Escolha o Esporte",
        ["Futebol Brasil", "NBA (Basquete)", "Tênis (ATP)", "Futebol Inglês", "MMA/UFC"]
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
    "Futebol Brasil": "soccer_brazil_campeonato",
    "NBA (Basquete)": "basketball_nba",
    "Tênis (ATP)": "tennis_atp",
    "Futebol Inglês": "soccer_epl",
    "MMA/UFC": "mma_mixed_martial_arts"
}

MARKET_KEY = "h2h" if mercado_label == "Vencedor (H2H)" else "totals"

# Casas de Alta Liquidez
ALLOWED_BOOKS = "pinnacle,bet365,betano,1xbet,betfair_ex,williamhill,marathonbet,888sport,bwin,unibet"

# FILTROS ESCANCARADOS (Para ver tudo no radar)
MIN_PROFIT = -10.0  # Mostra até jogos com 10% de prejuízo para vigilância
MIN_ODD = 1.01      # Aceita qualquer odd para não filtrar dados
MAX_RESULTS = 20    # Quantidade de jogos na tela

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
if st.button("🚀 EXECUTAR VARREDURA AGRESSIVA"):
    with st.spinner(f"TRATOR VARRENDO {esporte_label.upper()}..."):
        sport_key = SPORTS_MAP[esporte_label]

        # Ajuste Dinâmico para Tênis (Evita erro de esporte inativo)
        if esporte_label == "Tênis (ATP)":
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

            if not data:
                st.warning("📭 Nenhum dado encontrado para este esporte agora.")
                st.stop()

            opportunities = []

            for game in data:
                game_name = f"{game.get('home_team')} vs {game.get('away_team')}"
                
                # LÓGICA VENCEDOR (H2H)
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

                # LÓGICA TOTAIS (Over/Under)
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

            # EXIBIÇÃO DOS RESULTADOS
            if opportunities:
                opportunities = sorted(opportunities, key=lambda x: x["data"]["profit_pct"], reverse=True)[:MAX_RESULTS]
                
                for arb in opportunities:
                    p_pct = arb["data"]["profit_pct"]
                    
                    if p_pct > 0:
                        header = f"✅ LUCRO: {p_pct:.2f}% | {arb['game']}"
                        if arb["type"] == "TOTAL": header += f" (Linha {arb['line']})"
                        with st.expander(header, expanded=True):
                            st.success(f"### Retorno Garantido: R$ {arb['data']['profit']:.2f}")
                            cols = st.columns(len(arb["names"]))
                            for i, name in enumerate(arb["names"]):
                                info = arb["details"][name]
                                cols[i].metric(name, f"Odd {info['price']}", info['book'])
                                cols[i].warning(f"APOSTAR: R$ {arb['data']['stakes'][i]:.2f}")
                    else:
                        header = f"📊 RADAR: {p_pct:.2f}% | {arb['game']}"
                        with st.expander(header):
                            st.info(f"Monitorando diferença de odds... ({p_pct:.2f}%)")
                            cols = st.columns(len(arb["names"]))
                            for i, name in enumerate(arb["names"]):
                                info = arb["details"][name]
                                cols[i].write(f"**{name}**")
                                cols[i].write(f"Casa: {info['book']} | Odd: {info['price']}")
                                cols[i].write(f"Sugerido: R$ {arb['data']['stakes'][i]:.2f}")
            else:
                st.info("Nenhuma odd encontrada para as casas selecionadas.")

        except Exception as e:
            st.error(f"Erro no motor Nitro: {e}")

st.divider()
st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
