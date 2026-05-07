import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="NITRO MULTI-SPORTS | MACA")
st.title("🔥 NITRO ARB - MULTI-ESPORTES")

API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
BOOKS = "bet365,pinnacle,betano,1xbet,betfair_ex,williamhill,marathonbet,888sport,bwin,unibet"

# --- MENU LATERAL DE COMANDO ---
st.sidebar.title("Configurações do Trator")
esporte_selecionado = st.sidebar.selectbox(
    "Escolha o Esporte",
    ["soccer_brazil_campeonato", "soccer_epl", "basketball_nba", "tennis_atp", "americanfootball_nfl"]
)
bankroll = st.sidebar.number_input("Banca (R$)", value=500.0)

def calc_stakes(bankroll, odds):
    inv = sum(1/o for o in odds)
    profit_pct = (1 - inv) * 100
    stakes = [(bankroll / o) / inv for o in odds]
    profit = (stakes[0] * odds[0]) - bankroll
    return {"profit_pct": profit_pct, "profit": profit, "stakes": stakes}

if st.button("🚀 INICIAR VARREDURA MULTI-ESPORTES"):
    with st.spinner(f"CAÇANDO BRECHAS EM: {esporte_selecionado}..."):
        URL = f"https://api.the-odds-api.com/v4/sports/{esporte_selecionado}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal&bookmakers={BOOKS}"
        
        try:
            res = requests.get(URL).json()
            arbs, monitoring = [], []

            for game in res:
                game_name = f"{game['home_team']} vs {game['away_team']}"
                best_odds = {}

                for book in game.get('bookmakers', []):
                    for market in book.get('markets', []):
                        if market['key'] == 'h2h':
                            for o in market['outcomes']:
                                if o['name'] not in best_odds or o['price'] > best_odds[o['name']]['price']:
                                    best_odds[o['name']] = {"price": o['price'], "book": book['title']}

                if len(best_odds) >= 2:
                    prices = [v['price'] for v in best_odds.values()]
                    data = calc_stakes(bankroll, prices)
                    item = {"game": game_name, "best": best_odds, "arb": data}
                    
                    if data['profit_pct'] > 0: arbs.append(item)
                    elif data['profit_pct'] > -5.0: monitoring.append(item)

            if arbs:
                st.subheader("💰 LUCRO GARANTIDO")
                for r in arbs:
                    with st.expander(f"✅ {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=True):
                        cols = st.columns(len(r['best']))
                        for i, (name, info) in enumerate(r['best'].items()):
                            cols[i].metric(name, f"R$ {r['arb']['stakes'][i]:.2f}", f"{info['book']} @ {info['price']}")

            st.subheader("👀 RADAR DE PROXIMIDADE")
            if monitoring:
                monitoring = sorted(monitoring, key=lambda x: x['arb']['profit_pct'], reverse=True)
                for r in monitoring[:10]:
                    st.info(f"📊 {r['arb']['profit_pct']:.2f}% | {r['game']} | {list(r['best'].values())[0]['book']} vs {list(r['best'].values())[1]['book']}")
            else:
                st.info("Nenhuma oportunidade detectada agora.")

        except Exception as e:
            st.error(f"Erro no motor: {e}")

st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
