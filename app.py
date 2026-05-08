import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="NITRO ENGINE | MACA")
st.title("🔥 NITRO ARB - MODO À PROVA DE FALHAS")

# --- PAINEL DE CONTROLE ---
col1, col2 = st.columns(2)
with col1:
    bankroll = st.number_input("Banca Total (R$)", value=500.0, step=50.0)
with col2:
    esporte_label = st.selectbox(
        "Alvo do Trator",
        ["NBA (Basquete)", "Tênis (ATP)", "Futebol (Brasil)", "Futebol (Inglês)", "MMA (UFC)"]
    )

# Mapeamento Refinado (Nomes exatos da API para não dar erro de crédito)
mapa = {
    "NBA (Basquete)": "basketball_nba",
    "Tênis (ATP)": "tennis_atp_aus_open", # Ajustado para o torneio ativo (ex: Aus Open) ou use 'tennis_atp' genérico
    "Futebol (Brasil)": "soccer_brazil_campeonato",
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
        # A URL agora usa um parâmetro de segurança para evitar erros de crédito
        URL = f"https://api.the-odds-api.com/v4/sports/{target_sport}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal&bookmakers={BOOKS}"
        
        try:
            response = requests.get(URL)
            res = response.json()
            
            # Se a API reclamar de créditos ou esporte inexistente
            if response.status_code != 200:
                st.error(f"⚠️ Alerta da API: {res.get('msg', 'Verifique se o esporte está ativo ou se os créditos acabaram.')}")
            elif not isinstance(res, list) or len(res) == 0:
                st.warning(f"📭 Nenhum jogo ativo encontrado para {esporte_label} no momento.")
            else:
                arbs, monitoring = [], []
                for game in res:
                    game_name = f"{game['home_team']} vs {game['away_team']}"
                    best_odds = {}

                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            # Captura tanto 'h2h' quanto 'h2h_2' (comum no Tênis)
                            if 'h2h' in market['key']:
                                for o in market['outcomes']:
                                    name = o['name']
                                    if name not in best_odds or o['price'] > best_odds[name]['price']:
                                        best_odds[name] = {"price": o['price'], "book": book['title']}

                    if len(best_odds) >= 2:
                        sorted_names = sorted(best_odds.keys())
                        prices = [best_odds[n]['price'] for n in sorted_names]
                        data = calc_stakes(bankroll, prices)
                        
                        item = {"game": game_name, "names": sorted_names, "best": best_odds, "arb": data}
                        if data['profit_pct'] > 0: arbs.append(item)
                        elif data['profit_pct'] > -8.0: monitoring.append(item)

                # --- EXIBIÇÃO ---
                if arbs:
                    st.subheader("💰 ENTRADA CONFIRMADA!")
                    for r in arbs:
                        with st.expander(f"✅ {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=True):
                            st.write(f"**LUCRO LÍQUIDO: R$ {r['arb']['profit']:.2f}**")
                            cols = st.columns(len(r['names']))
                            for i, name in enumerate(r['names']):
                                info = r['best'][name]
                                aposta = r['arb']['stakes'][i]
                                cols[i].metric(f"APOSTAR R$ {aposta:.2f}", f"Odd {info['price']}", info['book'])
                
                st.subheader("👀 RADAR DE OPORTUNIDADES")
                if monitoring:
                    for r in monitoring[:10]:
                        with st.status(f"📊 {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=False):
                            for i, name in enumerate(r['names']):
                                info = r['best'][name]
                                st.write(f"💵 **Apostar R$ {r['arb']['stakes'][i]:.2f}** no **{name}** (Odd {info['price']} na {info['book']})")
        
        except Exception as e:
            st.error(f"Erro no motor: {e}")

st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
