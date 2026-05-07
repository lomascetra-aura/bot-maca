import asyncio
import aiohttp
import uvloop
import streamlit as st
from collections import defaultdict

# Instalando o motor de alta performance
try:
    uvloop.install()
except:
    pass 

API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8" # Sua Key fixa aqui
BOOKS = "bet365,betano,betfair_ex,pinnacle,1xbet,williamhill,marathonbet"
SPORT = "soccer"
URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h,totals&oddsFormat=decimal&bookmakers={BOOKS}"

st.set_page_config(layout="wide", page_title="NITRO ENGINE | MACA")
st.title("🔥 NITRO ARB ENGINE - MODO AGRESSIVO")

bankroll = st.number_input("Banca para Operação (R$)", value=500.0, min_value=10.0)

async def fetch():
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        async with session.get(URL) as resp:
            return await resp.json()

def calc_stakes(bankroll, odds):
    inv = sum(1/o for o in odds)
    profit_pct = (1 - inv) * 100
    
    # Cálculo de Stakes (Apostas)
    stakes = [(bankroll / o) / inv for o in odds]
    payout = stakes[0] * odds[0]
    profit = payout - bankroll

    return {
        "inv": inv,
        "profit_pct": profit_pct,
        "profit": profit,
        "stakes": stakes
    }

# Processamento de Vencedor (H2H) e Totais (Gols)
def process_markets(bookmakers):
    best_h2h = {}
    grouped_totals = defaultdict(dict)

    for book in bookmakers:
        title = book["title"]
        for market in book["markets"]:
            if market["key"] == "h2h":
                for o in market["outcomes"]:
                    if o["name"] not in best_h2h or o["price"] > best_h2h[o["name"]]["price"]:
                        best_h2h[o["name"]] = {"price": o["price"], "book": title}
            
            elif market["key"] == "totals":
                for o in market["outcomes"]:
                    point, side = o["point"], o["name"]
                    current = grouped_totals[point].get(side)
                    if not current or o["price"] > current["price"]:
                        grouped_totals[point][side] = {"price": o["price"], "book": title}
    
    return best_h2h, grouped_totals

async def scanner():
    data = await fetch()
    arbs, monitoring = [], []

    for game in data:
        game_name = f'{game["home_team"]} vs {game["away_team"]}'
        h2h_best, totals_grouped = process_markets(game["bookmakers"])

        # Checar H2H
        if len(h2h_best) >= 2:
            res = calc_stakes(bankroll, [v["price"] for v in h2h_best.values()])
            item = {"game": game_name, "market": "H2H", "best": h2h_best, "arb": res}
            if res["profit_pct"] > 0: arbs.append(item)
            elif res["profit_pct"] > -2: monitoring.append(item) # Radar: até 2% de "prejuízo" (quase lucro)

        # Checar Totals
        for point, sides in totals_grouped.items():
            if "Over" in sides and "Under" in sides:
                res = calc_stakes(bankroll, [sides["Over"]["price"], sides["Under"]["price"]])
                item = {"game": game_name, "market": f"Gols {point}", "best": sides, "arb": res}
                if res["profit_pct"] > 0: arbs.append(item)
                elif res["profit_pct"] > -2: monitoring.append(item)

    return arbs, monitoring

if st.button("🚀 EXECUTAR VARREDURA AGRESSIVA"):
    with st.spinner("TRATOR NA PISTA..."):
        arbs, monitoring = asyncio.run(scanner())

        if arbs:
            st.subheader("💰 LUCRO GARANTIDO DETECTADO")
            for r in arbs:
                with st.expander(f'✅ {r["arb"]["profit_pct"]:.2f}% | {r["game"]} | {r["market"]}', expanded=True):
                    st.success(f'LUCRO ESTIMADO: R$ {r["arb"]["profit"]:.2f}')
                    cols = st.columns(len(r["best"]))
                    for idx, (side, info) in enumerate(r["best"].items()):
                        cols[idx].metric(side, f'R$ {r["arb"]["stakes"][idx]:.2f}', f'{info["price"]} @ {info["book"]}')
        
        st.divider()
        st.subheader("👀 RADAR DE PROXIMIDADE (QUASE LUCRO)")
        if monitoring:
            # Ordena pelo que está mais perto de 0%
            monitoring = sorted(monitoring, key=lambda x: x["arb"]["profit_pct"], reverse=True)
            for r in monitoring[:5]:
                st.info(f'⚠️ {r["arb"]["profit_pct"]:.2f}% | {r["game"]} | {r["market"]} (Monitorando)')
        else:
            st.write("Mercado muito frio. Sem oportunidades próximas.")

st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
