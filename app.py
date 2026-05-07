import streamlit as st
import requests

# Configurações de Interface
st.set_page_config(layout="wide", page_title="NITRO ENGINE | MACA")
st.title("🔥 NITRO ARB ENGINE - MODO AGRESSIVO")

# Chave e Configurações Técnicas
API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
BOOKS = "bet365,betano,betfair_ex,pinnacle,1xbet,williamhill,marathonbet"
SPORT = "soccer"

bankroll = st.number_input("Banca para Operação (R$)", value=500.0, min_value=10.0)

def calc_stakes(bankroll, odds):
    inv = sum(1/o for o in odds)
    profit_pct = (1 - inv) * 100
    stakes = [(bankroll / o) / inv for o in odds]
    profit = (stakes[0] * odds[0]) - bankroll
    return {"inv": inv, "profit_pct": profit_pct, "profit": profit, "stakes": stakes}

if st.button("🚀 EXECUTAR VARREDURA AGRESSIVA"):
    with st.spinner("TRATOR NA PISTA..."):
        URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h,totals&oddsFormat=decimal&bookmakers={BOOKS}"
        
        try:
            res = requests.get(URL).json()
            arbs = []
            monitoring = []

            for game in res:
                game_name = f"{game['home_team']} vs {game['away_team']}"
                
                # Coleta as melhores odds de H2H
                best_h2h = {}
                for book in game['bookmakers']:
                    for market in book['markets']:
                        if market['key'] == 'h2h':
                            for o in market['outcomes']:
                                if o['name'] not in best_h2h or o['price'] > best_h2h[o['name']]['price']:
                                    best_h2h[o['name']] = {"price": o['price'], "book": book['title']}

                if len(best_h2h) >= 2:
                    data = calc_stakes(bankroll, [v['price'] for v in best_h2h.values()])
                    item = {"game": game_name, "market": "Vencedor", "best": best_h2h, "arb": data}
                    if data['profit_pct'] > 0: arbs.append(item)
                    elif data['profit_pct'] > -2.5: monitoring.append(item)

            # Exibição dos Resultados
            if arbs:
                st.subheader("💰 LUCRO GARANTIDO")
                for r in arbs:
                    with st.expander(f"✅ {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=True):
                        st.write(f"Lucro: R$ {r['arb']['profit']:.2f}")
            
            st.divider()
            st.subheader("👀 RADAR DE PROXIMIDADE")
            if monitoring:
                monitoring = sorted(monitoring, key=lambda x: x['arb']['profit_pct'], reverse=True)
                for r in monitoring[:8]:
                    st.info(f"⚠️ {r['arb']['profit_pct']:.2f}% | {r['game']} ({list(r['best'].values())[0]['book']})")
            else:
                st.write("Aguardando oscilação do mercado...")

        except Exception as e:
            st.error(f"Erro de conexão: {e}")

st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
