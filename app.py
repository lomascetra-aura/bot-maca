import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="NITRO ENGINE | MACA")
st.title("🔥 NITRO ARB - MULTICASAS ATIVO")

API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
# Lista das 10 gigantes (Foco total em encontrar a diferença entre elas)
BOOKS = "bet365,pinnacle,betano,1xbet,betfair_ex,williamhill,marathonbet,888sport,bwin,unibet"
SPORT = "soccer"

bankroll = st.number_input("Banca para Operação (R$)", value=500.0)

def calc_stakes(bankroll, odds):
    inv = sum(1/o for o in odds)
    profit_pct = (1 - inv) * 100
    stakes = [(bankroll / o) / inv for o in odds]
    profit = (stakes[0] * odds[0]) - bankroll
    return {"inv": inv, "profit_pct": profit_pct, "profit": profit, "stakes": stakes}

if st.button("🚀 INICIAR VARREDURA MULTICASAS"):
    with st.spinner("COMPARANDO ODDS ENTRE AS 10 GIGANTES..."):
        URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal&bookmakers={BOOKS}"
        
        try:
            res = requests.get(URL).json()
            st.sidebar.success(f"📡 {len(res)} Jogos no Radar")
            
            arbs, monitoring = [], []

            for game in res:
                game_name = f"{game['home_team']} vs {game['away_team']}"
                best_odds = {}

                # Varre todas as casas do jogo para pegar a MAIOR odd de cada resultado
                for book in game.get('bookmakers', []):
                    for market in book.get('markets', []):
                        if market['key'] == 'h2h':
                            for o in market['outcomes']:
                                outcome_name = o['name']
                                price = o['price']
                                if outcome_name not in best_odds or price > best_odds[outcome_name]['price']:
                                    best_odds[outcome_name] = {"price": price, "book": book['title']}

                if len(best_odds) >= 2:
                    prices = [v['price'] for v in best_odds.values()]
                    data = calc_stakes(bankroll, prices)
                    item = {"game": game_name, "best": best_odds, "arb": data}
                    
                    if data['profit_pct'] > 0:
                        arbs.append(item)
                    elif data['profit_pct'] > -5.0: # Radar de proximidade
                        monitoring.append(item)

            # --- EXIBIÇÃO ---
            if arbs:
                st.subheader("💰 OPORTUNIDADE DE LUCRO!")
                for r in arbs:
                    with st.expander(f"✅ {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=True):
                        cols = st.columns(len(r['best']))
                        for i, (name, info) in enumerate(r['best'].items()):
                            cols[i].metric(name, f"R$ {r['arb']['stakes'][i]:.2f}", f"{info['book']} @ {info['price']}")

            st.subheader("👀 RADAR DE DIFERENÇA DE ODDS")
            if monitoring:
                monitoring = sorted(monitoring, key=lambda x: x['arb']['profit_pct'], reverse=True)
                for r in monitoring[:15]:
                    with st.status(f"📊 {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=False):
                        # Aqui ele mostra a diferença entre as casas
                        txt = " | ".join([f"{n}: {i['price']} ({i['book']})" for n, i in r['best'].items()])
                        st.write(txt)
            else:
                st.info("Buscando variações nas outras casas...")

        except Exception as e:
            st.error(f"Erro: {e}")

st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
