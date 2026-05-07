import streamlit as st
import requests

# Configurações de Elite
st.set_page_config(layout="wide", page_title="NITRO ENGINE | MACA")
st.title("🔥 NITRO ARB ENGINE - MODO AGRESSIVO")

# Chave Fixa e Configurações de API
API_KEY = "1df4197c5fc09a88fc1a9b363f7673d8"
# Adicionei o mercado de 'totals' (Gols) para aumentar as chances
BOOKS = "bet365,betano,pinnacle,1xbet,betfair_ex,williamhill,marathonbet"
SPORT = "soccer"

bankroll = st.number_input("Banca para Operação (R$)", value=500.0, min_value=10.0)

def calc_stakes(bankroll, odds):
    inv = sum(1/o for o in odds)
    profit_pct = (1 - inv) * 100
    stakes = [(bankroll / o) / inv for o in odds]
    profit = (stakes[0] * odds[0]) - bankroll
    return {"inv": inv, "profit_pct": profit_pct, "profit": profit, "stakes": stakes}

if st.button("🚀 EXECUTAR VARREDURA AGRESSIVA"):
    with st.spinner("TRATOR NA PISTA... VARRENDO MERCADO"):
        # URL buscando Vencedor (h2h) e Over/Under (totals)
        URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h,totals&oddsFormat=decimal&bookmakers={BOOKS}"
        
        try:
            res = requests.get(URL).json()
            
            if "msg" in res or not isinstance(res, list):
                st.error(f"Erro na API: {res}")
            else:
                st.sidebar.success(f"📡 {len(res)} Jogos Monitorados")
                arbs = []
                monitoring = []

                for game in res:
                    game_name = f"{game['home_team']} vs {game['away_team']}"
                    
                    # --- FILTRO 1: VENCEDOR (H2H) ---
                    best_h2h = {}
                    for book in game.get('bookmakers', []):
                        for market in book.get('markets', []):
                            if market['key'] == 'h2h':
                                for o in market['outcomes']:
                                    if o['name'] not in best_h2h or o['price'] > best_h2h[o['name']]['price']:
                                        best_h2h[o['name']] = {"price": o['price'], "book": book['title']}

                    if len(best_h2h) >= 2:
                        data = calc_stakes(bankroll, [v['price'] for v in best_h2h.values()])
                        item = {"game": game_name, "market": "Vencedor", "best": best_h2h, "arb": data}
                        if data['profit_pct'] > 0:
                            arbs.append(item)
                        elif data['profit_pct'] > -10.0: # SENSIBILIDADE MÁXIMA
                            monitoring.append(item)

                # --- EXIBIÇÃO ---
                if arbs:
                    st.subheader("💰 LUCRO GARANTIDO DETECTADO")
                    for r in arbs:
                        with st.expander(f"✅ {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=True):
                            st.success(f"Lucro Real: R$ {r['arb']['profit']:.2f}")
                            cols = st.columns(len(r['best']))
                            for i, (name, info) in enumerate(r['best'].items()):
                                cols[i].metric(name, f"R$ {r['arb']['stakes'][i]:.2f}", f"{info['book']} @ {info['price']}")
                
                st.divider()
                st.subheader("👀 RADAR DE PROXIMIDADE (EFICIÊNCIA > 90%)")
                if monitoring:
                    # Mostra os 15 melhores jogos quase lucrativos
                    monitoring = sorted(monitoring, key=lambda x: x['arb']['profit_pct'], reverse=True)
                    for r in monitoring[:15]:
                        with st.status(f"⚠️ {r['arb']['profit_pct']:.2f}% | {r['game']}", expanded=False):
                            st.write(f"Mercado: {r['market']}")
                            for name, info in r['best'].items():
                                st.write(f"👉 {name}: {info['price']} na {info['book']}")
                else:
                    st.info("Nenhum jogo relevante nas casas selecionadas agora.")

        except Exception as e:
            st.error(f"Falha no motor: {e}")

st.divider()
st.caption("Aura do mundo espelhado: Mestre Maca o que deseja!")
