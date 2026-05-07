import streamlit as st
import requests

# Configuração da Página
st.set_page_config(layout="wide", page_title="NITRO MULTI-SPORTS | MACA")

# --- MENU LATERAL DE COMANDO (Aba de Escolha) ---
with st.sidebar:
    st.title("🚜 Painel do Mestre")
    st.info("Aura do mundo espelhado: Mestre Maca o que deseja!")
    
    # Seletor de Esporte - Isso cria a aba na lateral esquerda
    esporte_label = st.selectbox(
        "Escolha o Esporte para Varredura",
        ["Futebol (Brasil)", "Futebol (Inglês)", "NBA (Basquete)", "Tênis (ATP)", "NFL (EUA)"]
    )
    
    # Mapeamento técnico para a API
    mapa = {
        "Futebol (Brasil)": "soccer_brazil_campeonato",
        "Futebol (Inglês)": "soccer_epl",
        "NBA (Basquete)": "basketball_nba",
        "Tênis (ATP)": "tennis_atp",
        "NFL (EUA)": "americanfootball_nfl"
    }
    target_sport = mapa[esporte_label]
    
    bankroll = st.number_input("Banca para Cálculo (R$)", value=500.0)
    st.divider()
    st.write("Configuração: Nível 0 Ativo")

# --- ÁREA PRINCIPAL ---
st.title(f"🔥 NITRO ARB - {esporte_label.upper()}")

API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
BOOKS = "bet365,pinnacle,betano,1xbet,betfair_ex,williamhill,marathonbet,888sport,bwin,unibet"

def calc_stakes(bankroll, odds):
    inv = sum(1/o for o in odds)
    profit_pct = (1 - inv) * 100
    stakes = [(bankroll / o) / inv for o in odds]
    profit = (stakes[0] * odds[0]) - bankroll
    return {"profit_pct": profit_pct, "profit": profit, "stakes": stakes}

if st.button("🚀 EXECUTAR VARREDURA AGRESSIVA"):
    with st.spinner(f"CAÇANDO BRECHAS EM {esporte_label.upper()}..."):
        URL = f"https://api.the-odds-api.com/v4/sports/{target_sport}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal&bookmakers={BOOKS}"
        
        try:
            res = requests.get(URL).json()
            
            if not isinstance(res, list):
                st.error("Limite da API ou erro de chave. Verifique o plano.")
            else:
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
                        elif data['profit_pct'] > -8.0: monitoring.append(item)

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
                    for r in monitoring[:12]:
                        st.info(f"📊 {r['arb']['profit_pct']:.2f}% | {r['game']} | {list(r['best'].values())[0]['book']} vs {list(r['best'].values())[1]['book']}")
                else:
                    st.warning("Sem jogos para este esporte no momento.")

        except Exception as e:
            st.error(f"Falha técnica: {e}")
