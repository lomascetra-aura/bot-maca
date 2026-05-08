import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="NITRO ENGINE | MACA")
st.title("🔥 NITRO ARB - DISTRIBUIÇÃO EXATA")

# --- PAINEL DE COMANDO ---
col1, col2 = st.columns(2)
with col1:
    bankroll = st.number_input("Banca Total (R$)", value=500.0, step=50.0)
with col2:
    esporte_label = st.selectbox(
        "Alvo do Trator",
        ["Futebol (Brasil)", "NBA (Basquete)", "Tênis (ATP)", "Futebol (Inglês)", "MMA (UFC)"]
    )

mapa = {
    "Futebol (Brasil)": "soccer_brazil_campeonato",
    "NBA (Basquete)": "basketball_nba",
    "Tênis (ATP)": "tennis_atp",
    "Futebol (Inglês)": "soccer_epl",
    "MMA (UFC)": "mma_mixed_martial_arts"
}
target_sport = mapa[esporte_label]

API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
BOOKS = "bet365,pinnacle,betano,1xbet,betfair_ex,williamhill,marathonbet,888sport,bwin,unibet"

def calc_stakes(bankroll, odds):
    inv = sum(1/o for o in odds)
    profit_pct = (1 - inv) * 100
    stakes = [(bankroll / o) / inv for o in odds]
    profit = (stakes[0] * odds[0]) - bankroll
    return {"profit_pct": profit_pct, "profit": profit, "stakes": stakes}

if st.button("🚀 INICIAR VARREDURA AGRESSIVA"):
    with st.spinner(f"VARRENDO {esporte_label.upper()}..."):
        # Blindagem: Ténis e MMA às vezes usam 'h2h' ou outros IDs, buscamos os principais
        URL = f"https://api.the-odds-api.com/v4/sports/{target_sport}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal&bookmakers={BOOKS}"
        
        try:
            res = requests.get(URL).json()
            if not isinstance(res, list):
                st.error("Erro na API. Verifique os créditos da sua chave.")
            else:
                arbs, monitoring = [], []
                for game in res:
                    game_name = f"{game['home_team']} vs {game['away_team']}"
                    best_odds = {}

                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            # Aceita h2h (padrão) ou variações comuns de mercados de 2/3 opções
                            if 'h2h' in market['key']:
                                for o in market['outcomes']:
                                    name = o['name']
                                    if name not in best_odds or o['price'] > best_odds[name]['price']:
                                        best_odds[name] = {"price": o['price'], "book": book['title']}

                    if len(best_odds) >= 2:
                        # Ordenamos para garantir que o cálculo bata com a exibição
                        sorted_names = sorted(best_odds.keys())
                        prices = [best_odds[n]['price'] for n in sorted_names]
                        data = calc_stakes(bankroll, prices)
                        
                        item = {"game": game_name, "names": sorted_names, "best": best_odds, "arb": data}
                        if data['profit_pct'] > 0: arbs.append(item)
                        elif data['profit_pct'] > -6.0: monitoring.append(item)

                if arbs:
                    st.subheader("💰 ENTRADA CONFIRMADA - LUCRO!")
                    for r in arbs:
                        with st.expander(f"✅ {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=True):
                            st.write(f"**LUCRO LÍQUIDO: R$ {r['arb']['profit']:.2f}**")
                            cols = st.columns(len(r['names']))
                            for i, name in enumerate(r['names']):
                                info = r['best'][name]
                                val_aposta = r['arb']['stakes'][i]
                                cols[i].warning(f"**{name}**")
                                cols[i].write(f"Casa: {info['book']}")
                                cols[i].write(f"Odd: {info['price']}")
                                cols[i].metric("APOSTAR AGORA", f"R$ {val_aposta:.2f}")
                
                st.subheader("👀 RADAR DE OPORTUNIDADES")
                if monitoring:
                    for r in monitoring[:10]:
                        with st.status(f"📊 {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=False):
                            for i, name in enumerate(r['names']):
                                info = r['best'][name]
                                st.write(f"👉 **{name}**: {info['price']} na {info['book']} (Sugerido: R$ {r['arb']['stakes'][i]:.2f})")
                else:
                    st.info("O mercado está estável agora.")

        except Exception as e:
            st.error(f"Erro no motor: {e}")

st.divider()
st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
